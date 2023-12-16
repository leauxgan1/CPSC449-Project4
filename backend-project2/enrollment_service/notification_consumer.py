import pika
import redis
import httpx

r = redis.Redis()

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

exchange_name = "notif_exchange"

channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name_webhook = result.method.queue
channel.queue_bind(exchange=exchange_name, queue=queue_name_webhook)

result = channel.queue_declare(queue='', exclusive=True)
queue_name_email = result.method.queue
channel.queue_bind(exchange=exchange_name, queue=queue_name_email)

print(' [*] Waiting for logs. To exit press CTRL+C')

def get_webhook(message: str):
    webhood_key = "webhook_" + message
    subscriptions = r.lrange(webhood_key, 0, -1)
    return (subscriptions[0]).decode("utf-8")[2:]

def get_email(message: str):
    email_key = "email_" + message
    subscriptions = r.lrange(email_key, 0, -1)
    return (subscriptions[0]).decode("utf-8")[2:]

def callback_webhook(ch, method, properties, body):
    webhook_url = get_webhook(body.decode("utf-8"))
    body_str = body.decode("utf-8")
    student_id = body_str[0:body_str.find("_")]
    class_id = body_str[body_str.find("_")+1:]
    try:
        response = httpx.post(webhook_url, data={'message': f'{student_id} was successfully enrolled into class {class_id}'})
        response.raise_for_status()
        print(response.status_code)
    except httpx.HTTPError as exc:
        ch.basic_nack(delivery_tag=method.delivery_tag)
        print(f"HTTP Exception for {exc.request.url} - {exc}")
        return

    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback_email(ch, method, properties, body):
    email = get_email(body.decode("utf-8"))

channel.basic_consume(queue=queue_name_webhook, on_message_callback=callback_webhook)
channel.basic_consume(queue=queue_name_email, on_message_callback=callback_email, auto_ack=True)

channel.start_consuming()