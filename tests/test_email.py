import asyncio
import os

from dotenv import load_dotenv
from pypoller.communicators.email.client import EmailClient
from pypoller.utils import create_logger

if __name__ == '__main__':
	load_dotenv() # Load the environment from .env

	receiver_address = os.environ['EMAIL_RECEIVER_ADDRESS']
	sender_address = os.environ['EMAIL_HOST_USER']
	account_password = os.environ['EMAIL_HOST_PASSWORD']
	email_host = os.environ['EMAIL_HOST']
	email_port = int(os.environ['EMAIL_PORT'])
	email_use_tls = bool(os.environ['EMAIL_USE_TLS'])

	body = {
		"subject": "Test Subject",
		"body": "Test Body",
		"receivers": receiver_address,
	}

	logger = create_logger('mailer')

	email_client = EmailClient(sender_address, account_password, logger, email_host, email_port, use_tls=email_use_tls)

	loop = asyncio.get_event_loop()
	loop.run_until_complete(email_client.send(receiver_address, message=body, msg_type="json"))
