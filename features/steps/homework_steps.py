from behave import given, when, then
from app.eshop import Product, ShoppingCart, Order
from unittest.mock import MagicMock

@given('A product "{name}" with price {price} and availability {amount}')
def create_product(context, name, price, amount):
    context.product = Product(name, float(price), int(amount))
    if not hasattr(context, 'products_db'):
        context.products_db = {}
    context.products_db[name] = context.product

@given('Another product "{name}" with price {price} and availability {amount}')
def create_another_product(context, name, price, amount):
    context.second_product = Product(name, float(price), int(amount))

@when('I add product "{name}" with amount {amount} to cart')
def add_product_to_cart(context, name, amount):
    prod = context.products_db.get(name, getattr(context, 'product', None))
    context.cart.add_product(prod, int(amount))

@when('I add product "{name}" (first one) with amount {amount} to cart')
def add_first_clone(context, name, amount):
    context.cart.add_product(context.product, int(amount))

@when('I remove product "{name}" from cart')
def remove_product(context, name):
    prod = context.products_db.get(name, context.product)
    context.cart.remove_product(prod)

@when('I try to add product "{name}" with amount {amount}')
def try_add_fail(context, name, amount):
    try:
        context.cart.add_product(context.product, int(amount))
        context.error = None
    except ValueError as e:
        context.error = e

@when('I submit the order')
def submit_order(context):
    mock_shipping = MagicMock()
    order = Order(cart=context.cart, shipping_service=mock_shipping)
    order.place_order(shipping_type="Нова Пошта")

@then('The cart should contain product "{name}"')
def check_contains(context, name):
    found = False
    for prod in context.cart.products:
        if prod.name == name:
            found = True
            break
    assert found is True

@then('The cart should contain product "{name}" with quantity {qty}')
def check_quantity(context, name, qty):
    target_product = context.products_db.get(name, context.product)
    assert context.cart.products[target_product] == int(qty)

@then('The total cost should be {total}')
def check_total(context, total):
    assert context.cart.calculate_total() == float(total)

@then('The cart contains the product regardless of price difference')
def check_identity(context):
    assert context.product in context.cart.products or context.second_product in context.cart.products

@then('The cart should be empty')
def check_empty(context):
    assert len(context.cart.products) == 0

@then('An error regarding availability should be raised')
def check_error(context):
    assert context.error is not None
    assert "items" in str(context.error)

@then('The product "{name}" availability should be {amount}')
def check_inventory(context, name, amount):
    prod = context.products_db.get(name, context.product)
    assert prod.available_amount == int(amount)

@given('A product "" with price {price} and availability {amount}')
def create_empty_name_product(context, price, amount):
    context.product = Product("", float(price), int(amount))
    if not hasattr(context, 'products_db'):
        context.products_db = {}
    context.products_db[""] = context.product

@when('I add product "" with amount {amount} to cart')
def add_empty_product_to_cart(context, amount):
    prod = context.products_db.get("", getattr(context, 'product', None))
    context.cart.add_product(prod, int(amount))

@then('The cart should contain product ""')
def check_contains_empty(context):
    found = False
    for prod in context.cart.products:
        if prod.name == "":
            found = True
            break
    assert found is True