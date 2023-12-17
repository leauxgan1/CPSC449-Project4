import pika
import redis
import httpx
import base64

import smtplib, ssl
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    if subscriptions and len((subscriptions[0]).decode("utf-8")) > 2:
        return (subscriptions[0]).decode("utf-8")[2:]
    else:
        return None

def get_email(message: str):
    email_key = "email_" + message
    subscriptions = r.lrange(email_key, 0, -1)
    if subscriptions and len((subscriptions[0]).decode("utf-8")) > 2:
        return (subscriptions[0]).decode("utf-8")[2:]
    else:
        return None

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
    body_str = body.decode("utf-8")
    student_id = body_str[0:body_str.find("_")]
    class_id = body_str[body_str.find("_")+1:]

    # Create EmailMessage object
    msg = EmailMessage()
    msg.set_content(f"Hello,\n\nThis is to inform you that {student_id} has subscribed to class {class_id}.")

    # Set email address to where you want to send the email
    msg['To'] = email

    # Set email subject
    msg['Subject'] = "Student Subscription Notification"

    # Set email sender (From address)
    msg['From'] = "example@gmail.com"  # Replace with sender email address

    login_username =  "example@gmail.com"
    login_password = ""

    # Create an SMTP connection and send the email
    try:
        server = smtplib.SMTP('localhost', 8025)
        server.starttls()  # Use TLS
        server.login(login_username, login_password)
        server.send_message(msg)
        server.quit()
        print(f' [x] Email Sent to {email}')
    except Exception as e:
        print(f' [x] Error sending email: {str(e)}')

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback_email_2(ch, method, properties, body):

    receiver_email = get_email(body.decode("utf-8"))
    body_str = body.decode("utf-8")
    student_id = body_str[0:body_str.find("_")]
    class_id = body_str[body_str.find("_")+1:]

    sender_email = "example@gmail.com"
    subject = "Student Subscription Notification"
    body = f"Hello,\n\nThis is to inform you that {student_id} has subscribed to class {class_id}."

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username =  "example@gmail.com"
    smtp_password = ""

    encoded_username = base64.b64encode(smtp_username.encode()).decode()
    encoded_password = base64.b64encode(smtp_password.encode()).decode()

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(encoded_username, encoded_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("Email sent successfully!")

# using .starttls()
def callback_email_3(ch, method, properties, body):

    body_str = body.decode("utf-8")
    student_id = body_str[0:body_str.find("_")]
    class_id = body_str[body_str.find("_")+1:]
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "example@gmail.com"
    receiver_email = get_email(body.decode("utf-8"))
    password = ""
    message = f"Hello,\n\nThis is to inform you that {student_id} has subscribed to class {class_id}."

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

# using SMTP_SSL()
def callback_email_4(ch, method, properties, body):

    body_str = body.decode("utf-8")
    student_id = body_str[0:body_str.find("_")]
    class_id = body_str[body_str.find("_")+1:]
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = "example@gmail.com"
    receiver_email = get_email(body.decode("utf-8"))
    password = ""
    message = f"Hello,\n\nThis is to inform you that {student_id} has subscribed to class {class_id}."

    encoded_username = base64.b64encode(sender_email.encode()).decode()
    encoded_password = base64.b64encode(password.encode()).decode()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(encoded_username, encoded_password)
        server.sendmail(sender_email, receiver_email, message)


channel.basic_consume(queue=queue_name_webhook, on_message_callback=callback_webhook)
channel.basic_consume(queue=queue_name_email, on_message_callback=callback_email_2, auto_ack=True)

channel.start_consuming()
