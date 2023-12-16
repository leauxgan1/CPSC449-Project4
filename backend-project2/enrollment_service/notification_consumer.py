import pika

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

def callback_webhook(ch, method, properties, body):
    print(f' [x] Webhook Callback: {body}')

def callback_email(ch, method, properties, body):
    print(f' [x] Email Callback {body}')

channel.basic_consume(queue=queue_name_webhook, on_message_callback=callback_webhook, auto_ack=True)
channel.basic_consume(queue=queue_name_email, on_message_callback=callback_email, auto_ack=True)

channel.start_consuming()