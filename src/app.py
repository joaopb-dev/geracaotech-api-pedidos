"""Servidor HTTP da API de pedidos, sem dependências externas de execução."""
import json
import logging
import os
import signal
import sys
import threading
import time
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from src.domain import InvalidOrder, create_order
from src.repository import OrderRepository

LOG = logging.getLogger("orders")
MAX_BODY = 65536


class Metrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.requests = {}

    def record(self, method, route, status):
        with self.lock:
            key = (method, route, status)
            self.requests[key] = self.requests.get(key, 0) + 1

    def render(self):
        lines = ["# HELP orders_http_requests_total Total de requisicoes HTTP.",
                 "# TYPE orders_http_requests_total counter"]
        with self.lock:
            for (method, route, status), count in sorted(self.requests.items()):
                lines.append(f'orders_http_requests_total{{method="{method}",route="{route}",status="{status}"}} {count}')
        return "\n".join(lines) + "\n"


class OrderServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, repository):
        self.repository = repository
        self.metrics = Metrics()
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    server_version = "OrdersAPI"
    sys_version = ""

    def log_message(self, format, *args):
        pass

    def respond(self, status, body, content_type="application/json; charset=utf-8", headers=None):
        data = body.encode("utf-8") if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)
        return status

    def do_GET(self):
        self.dispatch()

    def do_POST(self):
        self.dispatch()

    def dispatch(self):
        start = time.monotonic()
        path = urlsplit(self.path).path
        route = "/orders/{id}" if path.startswith("/orders/") else path if path in ("/orders", "/health", "/metrics") else "other"
        status = 500
        try:
            status = self.handle_request(path)
        except (BrokenPipeError, ConnectionResetError):
            LOG.warning(json.dumps({"event": "client_disconnected", "route": route}))
        except Exception:
            LOG.error(json.dumps({"event": "request_error", "route": route}))
            try:
                status = self.respond(500, {"error": "Erro interno."})
            except (BrokenPipeError, ConnectionResetError):
                pass
        finally:
            self.server.metrics.record(self.command, route, status)
            LOG.info(json.dumps({"event": "request", "method": self.command, "route": route,
                                 "status": status, "duration_ms": round((time.monotonic() - start) * 1000, 2)}))

    def handle_request(self, path):
        if self.command == "GET" and path == "/health":
            return self.respond(200, {"status": "ok"})
        if self.command == "GET" and path == "/metrics":
            return self.respond(200, self.server.metrics.render(), "text/plain; version=0.0.4; charset=utf-8")
        if self.command == "GET" and path.startswith("/orders/"):
            order = self.server.repository.get(path[len("/orders/"):])
            return self.respond(200, order) if order else self.respond(404, {"error": "Pedido não encontrado."})
        if path == "/orders" and self.command == "POST":
            if self.headers.get_content_type() != "application/json":
                self.close_connection = True
                return self.respond(415, {"error": "Use Content-Type: application/json."})
            try:
                length = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                length = -1
            if length < 0 or length > MAX_BODY:
                self.close_connection = True
                return self.respond(413, {"error": "Content-Length inválido ou corpo muito grande."})
            try:
                data = json.loads(self.rfile.read(length), parse_float=Decimal)
                order = create_order(data)
            except (UnicodeDecodeError, ValueError, InvalidOperation) as exc:
                return self.respond(400, {"error": str(exc) if isinstance(exc, InvalidOrder) else "JSON inválido."})
            return self.respond(201, self.server.repository.add(order))
        if path == "/orders" or path.startswith("/orders/") or path in ("/health", "/metrics"):
            allowed = "POST" if path == "/orders" else "GET"
            return self.respond(405, {"error": "Método não permitido."}, headers={"Allow": allowed})
        return self.respond(404, {"error": "Rota não encontrada."})


def main():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")
    path = os.getenv("DATABASE_PATH", "data/orders.db")
    port = int(os.getenv("PORT", "8080"))
    server = OrderServer(("0.0.0.0", port), OrderRepository(path))
    LOG.info(json.dumps({"event": "server_started", "port": port}))
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        LOG.info(json.dumps({"event": "server_stopped"}))


if __name__ == "__main__":
    main()
