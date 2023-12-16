import pika

def send_rabbitmq_message(message):
    print(message)
    exchange_name = "notif_exchange"
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    channel.basic_publish(exchange=exchange_name, routing_key='', body=message)
    connection.close()