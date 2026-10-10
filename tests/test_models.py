import pytest
from pydantic import ValidationError
from pricewatch.models import ProductItem

def make(**over):
    base = dict(store="x.com", variant_id=1, url="https://x.com/p",
                title="Item", price="499.00", compare_at_price=None, in_stock=True)
    base.update(over)
    return ProductItem(**base)

def test_price_string_is_cleaned():
    assert make(price="₹1,299.50").price == 1299.50

def test_variant_id_becomes_string():
    assert make(variant_id=12345).variant_id == "12345"

def test_zero_compare_price_becomes_none():
    assert make(compare_at_price="0.00").compare_at_price is None

def test_zero_price_is_rejected():
    with pytest.raises(ValidationError):
        make(price="0.00")

def test_missing_title_is_rejected():
    with pytest.raises(ValidationError):
        ProductItem(store="x", variant_id=1, url="u", price=10, in_stock=True)