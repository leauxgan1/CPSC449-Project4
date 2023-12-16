import pika
import httpx
import smtplib
from email.message import EmailMessage

def send_rabbitmq_message(exchange_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    channel.basic_publish(exchange=exchange_name, routing_key='', body=message)
    connection.close()


def create_exchange(exchange_name, exchange_type='fanout'):
    connection_params = pika.ConnectionParameters('your_rabbitmq_host', 5672, 'your_rabbitmq_user', 'your_rabbitmq_password')
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
    # Declare the exchange
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)
    
    connection.close()

# Example usage
# create_exchange('enrollment_exchange', 'fanout')


def consume_rabbitmq_email(exchange_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    #channel.queue_declare()
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(f' [x] Received {body}')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


def consume_rabbitmq_httpx(exchange_name):


#http://localhost:5500
#r = httpx.post('https://httpbin.org/post', data={'key': 'value'})