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

def send_email_notification(to_email, subject, body):
    from_email = 'your_email@example.com'  # replace with your email
    smtp_server = 'localhost'
    smtp_port = 8025

    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject

    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(from_email, to_email, message.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")

http://localhost:5500
r = httpx.post('https://httpbin.org/post', data={'key': 'value'})