import pika
import httpx
import smtplib

def send_rabbitmq_message(exchange_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    channel.basic_publish(exchange=exchange_name, routing_key='', body=message)
    connection.close()


def consume_rabbitmq_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    #channel.queue_declare()

    def callback(ch, method, properties, body):
        print(f' [x] Received {body}')

    channel.basic_consume(exchange=exchange_name, routing_key='', body=message)

    channel.start_consuming()

#http://localhost:5500
#r = httpx.post('https://httpbin.org/post', data={'key': 'value'})