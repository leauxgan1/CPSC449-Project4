from aiosmtpd.controller import Controller

class PrintMessageHandler:
    async def handle_DATA(self, server, session, envelope):
        # Print the received email message to stdout
        print("Received email:")
        print(f"From: {envelope.mail_from}")
        print(f"To: {', '.join(envelope.rcpt_tos)}")
        print(f"Subject: {envelope.content['subject']}")
        print(f"Message:\n{envelope.content.getvalue().decode('utf-8')}")

if name == 'main':
    controller = Controller(PrintMessageHandler(), hostname='localhost', port=8025)
    controller.start()