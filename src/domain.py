"""Regras do domínio, independentes de HTTP e persistência."""
from decimal import Decimal


class InvalidOrder(ValueError):
    """Dados incompatíveis com as regras de pedido."""


def is_integer_in_range(value, minimum, maximum):
    """Aceita números JSON de valor inteiro sem arredondar casas decimais."""
    if type(value) is int:
        return minimum <= value <= maximum
    if isinstance(value, Decimal):
        return value.is_finite() and minimum <= value <= maximum and value == value.to_integral_value()
    return False


def create_order(data):
    if not isinstance(data, dict) or set(data) != {"items"}:
        raise InvalidOrder("Envie um objeto contendo apenas items.")
    items = data["items"]
    if not isinstance(items, list) or not items:
        raise InvalidOrder("O pedido precisa de ao menos um item.")
    if len(items) > 100:
        raise InvalidOrder("O pedido pode ter no máximo 100 itens.")
    result = []
    total = 0
    for item in items:
        if not isinstance(item, dict) or set(item) != {"name", "quantity", "unit_price_cents"}:
            raise InvalidOrder("Cada item exige name, quantity e unit_price_cents.")
        name, quantity, price = item["name"], item["quantity"], item["unit_price_cents"]
        if not isinstance(name, str) or not name.strip() or len(name) > 200:
            raise InvalidOrder("O nome deve ter entre 1 e 200 caracteres.")
        if not is_integer_in_range(quantity, 1, 10000):
            raise InvalidOrder("A quantidade deve ser um inteiro entre 1 e 10000.")
        if not is_integer_in_range(price, 0, 100000000):
            raise InvalidOrder("O preço em centavos deve ser um inteiro entre 0 e 100000000.")
        quantity, price = int(quantity), int(price)
        total += quantity * price
        result.append({"name": name.strip(), "quantity": quantity, "unit_price_cents": price})
    return {"items": result, "total_cents": total}
