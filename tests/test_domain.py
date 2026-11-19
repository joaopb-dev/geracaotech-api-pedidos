import unittest
from src.domain import InvalidOrder, create_order


class DomainTests(unittest.TestCase):
    def test_total_and_name(self):
        result = create_order({"items": [{"name": " Livro ", "quantity": 2, "unit_price_cents": 1999},
                                         {"name": "Caneta", "quantity": 3, "unit_price_cents": 150}]})
        self.assertEqual(result["total_cents"], 4448)
        self.assertEqual(result["items"][0]["name"], "Livro")

    def test_invalid_orders(self):
        good = {"name": "Livro", "quantity": 1, "unit_price_cents": 1}
        invalid = [None, {}, {"items": []}, {"items": [None]}, {"items": [good] * 101},
                   {"items": [{**good, "name": " "}]}, {"items": [{**good, "quantity": 0}]},
                   {"items": [{**good, "quantity": True}]}, {"items": [{**good, "unit_price_cents": -1}]},
                   {"items": [{**good, "unit_price_cents": 1.5}]}, {"items": [dict(good, extra=1)]}]
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(InvalidOrder):
                    create_order(value)

    def test_boundaries(self):
        item = {"name": "x" * 200, "quantity": 10000, "unit_price_cents": 100000000}
        self.assertEqual(create_order({"items": [item]})["total_cents"], 1000000000000)
        for update in ({"name": "x" * 201}, {"quantity": 10001},
                       {"unit_price_cents": 100000001}, {"unit_price_cents": True}):
            with self.subTest(update=update), self.assertRaises(InvalidOrder):
                create_order({"items": [{**item, **update}]})

    def test_zero_price_is_valid(self):
        order = create_order({"items": [{"name": "Amostra", "quantity": 1, "unit_price_cents": 0}]})
        self.assertEqual(order["total_cents"], 0)


if __name__ == "__main__":
    unittest.main()
