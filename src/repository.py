"""Repository SQLite: isolamento da persistência em relação ao domínio."""
import json
from contextlib import closing
import sqlite3
import uuid
from pathlib import Path


class OrderRepository:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connection()) as connection, connection:
            connection.execute("CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")

    def connection(self):
        return sqlite3.connect(self.path, timeout=10)

    def add(self, order):
        order = {"id": str(uuid.uuid4()), **order}
        with closing(self.connection()) as connection, connection:
            connection.execute("INSERT INTO orders (id, payload) VALUES (?, ?)", (order["id"], json.dumps(order)))
        return order

    def get(self, order_id):
        with closing(self.connection()) as connection, connection:
            row = connection.execute("SELECT payload FROM orders WHERE id = ?", (order_id,)).fetchone()
        return json.loads(row[0]) if row else None
