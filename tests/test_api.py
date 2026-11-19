import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.app import Handler, Metrics
from src.repository import OrderRepository


class MemorySocket:
    def __init__(self, data):
        self.input = io.BytesIO(data)
        self.output = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if 'r' in mode:
            return self.input
        return self.output

    def sendall(self, data):
        self.output.write(data)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "orders.db")
        self.server = SimpleNamespace(repository=OrderRepository(self.db), metrics=Metrics())

    def request(self, method, path, body='', content_type=None):
        body = body.encode()
        headers = f'{method} {path} HTTP/1.0\r\nHost: localhost\r\nContent-Length: {len(body)}\r\n'
        if content_type:
            headers += f'Content-Type: {content_type}\r\n'
        sock = MemorySocket(headers.encode() + b'\r\n' + body)
        Handler(sock, ('127.0.0.1', 12345), self.server)
        head, response = sock.output.getvalue().split(b'\r\n\r\n', 1)
        return int(head.split(b' ')[1]), response.decode()

    def test_create_query_and_restart(self):
        data = {"items": [{"name": "Livro", "quantity": 2, "unit_price_cents": 1299}]}
        status, body = self.request("POST", "/orders", json.dumps(data), "application/json")
        self.assertEqual(status, 201)
        order = json.loads(body)
        self.assertEqual(order["total_cents"], 2598)
        status, body = self.request("GET", "/orders/" + order["id"])
        self.assertEqual((status, json.loads(body)), (200, order))
        self.server.repository = OrderRepository(self.db)
        status, body = self.request("GET", "/orders/" + order["id"])
        self.assertEqual((status, json.loads(body)), (200, order))

    def test_errors_and_metrics(self):
        self.assertEqual(self.request("GET", "/orders/nope")[0], 404)
        self.assertEqual(self.request("GET", "/unknown")[0], 404)
        self.assertEqual(self.request("GET", "/orders")[0], 405)
        self.assertEqual(self.request("POST", "/orders", "{}")[0], 415)
        self.assertEqual(self.request("POST", "/orders", "{", "application/json")[0], 400)
        self.assertEqual(self.request("POST", "/orders", '{"items":[]}', "application/json")[0], 400)
        self.assertEqual(self.request("GET", "/health")[0], 200)
        status, metric = self.request("GET", "/metrics")
        self.assertEqual(status, 200)
        self.assertIn('orders_http_requests_total{method="POST",route="/orders",status="400"} 2', metric)

    def test_json_integer_values_preserve_decimal_precision(self):
        body = '{"items":[{"name":"Livro","quantity":2.0,"unit_price_cents":1.299e3}]}'
        status, response = self.request("POST", "/orders", body, "application/json")
        self.assertEqual(status, 201)
        order = json.loads(response)
        self.assertEqual(order["items"][0]["quantity"], 2)
        self.assertIs(type(order["items"][0]["quantity"]), int)
        self.assertEqual(order["total_cents"], 2598)
        status, response = self.request("GET", "/orders/" + order["id"])
        self.assertEqual((status, json.loads(response)), (200, order))

        for number in ("1.5", "1.00000000000000001", "1e-999", "1e999"):
            with self.subTest(number=number):
                body = '{"items":[{"name":"Livro","quantity":' + number + ',"unit_price_cents":1}]}'
                self.assertEqual(self.request("POST", "/orders", body, "application/json")[0], 400)

        body = '{"items":[{"name":"Livro","quantity":1,"unit_price_cents":1.00000000000000001}]}'
        self.assertEqual(self.request("POST", "/orders", body, "application/json")[0], 400)

        for number in ("1e9999999999999999999999999", "9" * 5000):
            with self.subTest(number=number[:30]):
                body = '{"items":[{"name":"Livro","quantity":' + number + ',"unit_price_cents":1}]}'
                self.assertEqual(self.request("POST", "/orders", body, "application/json")[0], 400)

    def test_database_failure_is_a_json_500_and_is_counted(self):
        with patch.object(self.server.repository, "get", side_effect=RuntimeError("private database detail")):
            with self.assertLogs("orders", level="ERROR") as logs:
                status, body = self.request("GET", "/orders/123")
        self.assertEqual(status, 500)
        self.assertEqual(json.loads(body), {"error": "Erro interno."})
        self.assertNotIn("private database detail", body)
        self.assertEqual(json.loads(logs.records[0].getMessage())["event"], "request_error")
        _, metric = self.request("GET", "/metrics")
        self.assertIn('route="/orders/{id}",status="500"} 1', metric)

    def test_method_not_allowed_lists_allowed_method(self):
        for method, path, allowed in (("GET", "/orders", "POST"), ("POST", "/health", "GET")):
            with self.subTest(path=path):
                sock = MemorySocket(f"{method} {path} HTTP/1.0\r\nHost: localhost\r\n\r\n".encode())
                Handler(sock, ('127.0.0.1', 12345), self.server)
                head = sock.output.getvalue().split(b'\r\n\r\n', 1)[0]
                self.assertIn(b' 405 ', head)
                self.assertIn(f'Allow: {allowed}'.encode(), head)
