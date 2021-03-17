import asyncio
import os

from dotenv import load_dotenv
from pypoller.communicators.slack.client import SlackClient
from pypoller.utils import create_logger

if __name__ == '__main__':
	load_dotenv() # Load the environment from .env

	bot_token = os.environ['SLACK_BOT_TOKEN']
	channel_id = os.environ['SLACK_CHANNEL_ID']
	
	body = {
		"messageBlocks": [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": "<no-reply> {{ first_name }} | New User has joined\n"
				}
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "\nThis is an automated message. Please *DO NOT* reply."
				}
			}
		]
	}

	logger = create_logger('slack-client')

	slack_client = SlackClient(bot_token, logger=logger, channel_id=channel_id)

	loop = asyncio.get_event_loop()
	loop.run_until_complete(slack_client.send(channel_id, message="Hello World!", msg_type="text"))
	loop.run_until_complete(slack_client.send(channel_id, message=body, msg_type="json"))
