import asyncio
import json
import logging
import os
import pickle
from string import Template

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, PackageLoader
from pypoller.communicators.client import BaseClient
from pypoller.exceptions import ValidationError
from pypoller.utils import create_logger, insert_template_placeholders
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient


class SlackClient(BaseClient):
	def __init__(self, bot_token, logger=None, channel_id=None, bot_name="SlackBot"):
		super(SlackClient).__init__()
		self.client = AsyncWebClient(token=bot_token)
		self.channel_id = channel_id
		self.subject = ""
		self.prefix = ""
		self.suffix = ""
		self.msg_type = "text"
		self.bot_name = bot_name # Must have the https://api.slack.com/scopes/chat:write.customize scope to post as `bot_name`
		self.client_type = "slack"
		self.logger = logger

		self.validate()
	
	
	def validate(self):
		try:
			assert isinstance(self.logger, logging.Logger), "self.logger must be an instance of logging.Logger"
		except AssertionError as ae:
			raise ValidationError(f"{ae}")


	async def authorize(self):
		pass


	async def post_message(self, channel_id: str, message: object, msg_type: str ="text"):
		"""Posts a message to a Slack Channel using a Slack API call

		Args:
			channel_id (str): Channel ID
			message (object): Message Content
			msg_type (str, optional): Type of the message. Defaults to "text".
		
		Raises:
			SlackApiError: If there is an error when sending the message to Slack
		"""
		if msg_type == "text":
			self.body = message
			message_blocks = [
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": f"{getattr(self, attr)}",
					}
				} for attr in ["title", "body",] if hasattr(self, attr) and getattr(self, attr) not in [None, ""]
			]
			_ = await self.client.chat_postMessage(username=self.bot_name, channel=channel_id, text=message, blocks=message_blocks)
		
		elif msg_type == "json":				
			message_blocks = message["messageBlocks"]
			content = "Please upgrade your Slack client to view this message"
			_ = await self.client.chat_postMessage(username=self.bot_name, channel=channel_id, text=content, blocks=message_blocks)
			self.logger.info(f"Slack message sent!")


	def parse_message(self, message: object, msg_type: str ="text"):
		"""
		Parses a Slack message to be sent to a slack channel.
		A slack message must have a `title`, followed by a `body`.
		"""
		if msg_type == "json":
			self.msg_type = msg_type
			self.body = message
			self.message = self.body
		else:
			self.message = message
			self.msg_type = msg_type

	
	async def send(self, channel_id: str, message: object, msg_type: str ="text"):
		"""Sends a message to a Slack channel.

		Args:
			channel_id (str): Channel ID
			state (State): Represents the state of the system
			message (object) : Can be a string (text) or a Dictionary (JSON payload)
			msg_type (str, optional): [description]. Defaults to "text".
		"""
		self.parse_message(message, msg_type=msg_type)		
		await self.post_message(
			channel_id, self.message, msg_type=self.msg_type
		)

	async def close(self):
		pass
