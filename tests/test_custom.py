import pytest
import boto3
import time
from datetime import datetime, timedelta, timezone
from app.eshop import Product, ShoppingCart, Order
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE, SHIPPING_TABLE_NAME


@pytest.fixture
def real_shipping_service(dynamo_resource):
    return ShippingService(ShippingRepository(), ShippingPublisher())


@pytest.fixture
def clean_sqs():
    sqs = boto3.client("sqs", endpoint_url=AWS_ENDPOINT_URL, region_name=AWS_REGION, aws_access_key_id="test",
                       aws_secret_access_key="test")
    q_url = sqs.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    sqs.purge_queue(QueueUrl=q_url)
    time.sleep(1)
    return sqs, q_url

def test_1_black_friday_massive_orders(real_shipping_service, clean_sqs):
    sqs, q_url = clean_sqs
    shipping_ids = []

    for i in range(5):
        cart = ShoppingCart()
        cart.add_product(Product(f"Sale_Item_{i}", 10, 100), 1)
        order = Order(cart, real_shipping_service)
        shipping_ids.append(order.place_order("Нова Пошта"))

    processed = real_shipping_service.process_shipping_batch()

    assert len(processed) == 5
    for s_id in shipping_ids:
        assert real_shipping_service.check_status(s_id) == real_shipping_service.SHIPPING_COMPLETED


def test_2_emoji_and_cyrillic_in_dynamodb(real_shipping_service):
    cart = ShoppingCart()
    cart.add_product(Product("Крутий Товар 💻", 999, 5), 1)
    order = Order(cart, real_shipping_service)

    shipping_id = order.place_order("Укр Пошта")

    item = real_shipping_service.repository.get_shipping(shipping_id)
    assert "Крутий Товар 💻" in item["product_ids"]


def test_3_insufficient_product_amount_prevents_aws_calls(real_shipping_service, clean_sqs):
    sqs, q_url = clean_sqs
    cart = ShoppingCart()
    product = Product("Rare_Item", 1000, 2)

    with pytest.raises(ValueError, match="has only 2 items"):
        cart.add_product(product, 5)

    messages = sqs.receive_message(QueueUrl=q_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)
    assert 'Messages' not in messages


def test_4_time_travel_failed_shipping(real_shipping_service):
    cart = ShoppingCart()
    cart.add_product(Product("Time_Item", 10, 10), 1)
    order = Order(cart, real_shipping_service)

    due_date = datetime.now(timezone.utc) + timedelta(seconds=1)
    shipping_id = order.place_order("Meest Express", due_date=due_date)

    time.sleep(2)

    real_shipping_service.process_shipping(shipping_id)
    assert real_shipping_service.check_status(shipping_id) == real_shipping_service.SHIPPING_FAILED


def test_5_invalid_shipping_type_leaves_no_ghost_data(real_shipping_service, clean_sqs):
    sqs, q_url = clean_sqs
    cart = ShoppingCart()
    cart.add_product(Product("Test_Item", 10, 10), 1)
    order = Order(cart, real_shipping_service)

    with pytest.raises(ValueError, match="Shipping type is not available"):
        order.place_order("Доставка Голубами")

    messages = sqs.receive_message(QueueUrl=q_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)
    assert 'Messages' not in messages


def test_6_direct_dynamodb_audit(real_shipping_service):
    cart = ShoppingCart()
    cart.add_product(Product("Audit_Item", 50, 5), 1)
    order = Order(cart, real_shipping_service)
    shipping_id = order.place_order("Самовивіз")

    dynamo_client = boto3.client("dynamodb", endpoint_url=AWS_ENDPOINT_URL, region_name=AWS_REGION,
                                 aws_access_key_id="test", aws_secret_access_key="test")
    response = dynamo_client.get_item(
        TableName=SHIPPING_TABLE_NAME,
        Key={"shipping_id": {"S": shipping_id}}
    )

    assert "Item" in response
    assert response["Item"]["shipping_status"]["S"] == real_shipping_service.SHIPPING_IN_PROGRESS


def test_7_empty_cart_creates_valid_record(real_shipping_service):
    cart = ShoppingCart()
    order = Order(cart, real_shipping_service)

    shipping_id = order.place_order("Нова Пошта")

    item = real_shipping_service.repository.get_shipping(shipping_id)
    assert item["product_ids"] == ""


def test_8_polling_empty_sqs_is_graceful(real_shipping_service, clean_sqs):
    sqs, q_url = clean_sqs

    processed = real_shipping_service.process_shipping_batch()

    assert processed == []


def test_9_multiple_products_comma_separated(real_shipping_service):
    cart = ShoppingCart()
    cart.add_product(Product("Apple", 10, 10), 2)
    cart.add_product(Product("Banana", 5, 10), 5)
    cart.add_product(Product("Cherry", 2, 100), 10)

    order = Order(cart, real_shipping_service)
    shipping_id = order.place_order("Укр Пошта")

    item = real_shipping_service.repository.get_shipping(shipping_id)
    assert "Apple" in item["product_ids"]
    assert "Banana" in item["product_ids"]
    assert "Cherry" in item["product_ids"]
    assert item["product_ids"].count(",") == 2


def test_10_sqs_message_body_is_exactly_shipping_id(real_shipping_service, clean_sqs):
    sqs, q_url = clean_sqs
    cart = ShoppingCart()
    cart.add_product(Product("Secret_Data", 100, 1), 1)
    order = Order(cart, real_shipping_service)

    shipping_id = order.place_order("Нова Пошта")

    response = sqs.receive_message(QueueUrl=q_url, MaxNumberOfMessages=1, WaitTimeSeconds=2)
    messages = response.get("Messages", [])

    assert len(messages) == 1
    assert messages[0]["Body"] == shipping_id