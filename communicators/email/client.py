import asyncio
import json
import logging
import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

import aiosmtplib
from jinja2 import Environment, PackageLoader
from pypoller.communicators.client import BaseClient
from pypoller.exceptions import ValidationError
from pypoller.utils import create_logger, insert_template_placeholders


class EmailClient(BaseClient):
	def __init__(self, sender_address, account_password, logger=None, email_host="smtp.gmail.com", email_port=465, use_tls=True):
		super(EmailClient).__init__()
		self.sender_address = sender_address
		self.account_password = account_password
		self.email_host = email_host
		self.email_port = email_port
		self.use_tls = use_tls
		self.client_type = "email"
		self.logger = logger
		self.fallback_receivers = None

		self.validate()
	

	def validate(self):
		try:
			assert isinstance(self.logger, logging.Logger), "self.logger must be an instance of logging.Logger"
		except AssertionError as ae:
			raise ValidationError(f"{ae}")
	
	
	async def authorize(self):
		pass

	
	async def send_async_email(self, receivers, subject="", body="", msg_type="text"):
		"""
		Coroutine which sends an email asynchronously to a single receiver.
		"""
		message = MIMEMultipart('mixed')
		message["From"] = self.sender_address
		message["Subject"] = subject

		if msg_type == "json":
			message.attach(MIMEText(body, 'html'))
		else:
			message.attach(MIMEText(body, 'plain'))

		await aiosmtplib.send(
			message, hostname=self.email_host, port=self.email_port, 
			username=self.sender_address, password=self.account_password,
			use_tls=self.use_tls,
			recipients=receivers,
		)
		self.logger.info(f"Email Sent using {self.email_host}!")
	

	def parse_message(self, message, msg_type="text"):
		if msg_type == "json":
			content = message
			self.body = content
			self.msg_type = msg_type
			self.message = self.body
			self.subject = self.message["subject"]
			self.body = self.message["body"]
			self.fallback_receivers = self.message["receivers"]
		
		else:
			# TODO: Change this and add more validation checks / errors
			self.body = message

	
	async def send(self, receivers, message, msg_type="text"):
		self.parse_message(message, msg_type=msg_type)	
		if receivers is None:
			receivers = self.fallback_receivers
		await self.send_async_email(
			receivers, subject=self.subject,
			body=self.body, msg_type=self.msg_type
		)


	async def close(self):
		pass
