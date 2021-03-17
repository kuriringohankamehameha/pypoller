import asyncio
import json
import os
import random
from string import ascii_letters

from dotenv import load_dotenv
from pypoller.communicators.pollers.sqs import SQSPoller
from pypoller.communicators.slack.client import SlackClient
from pypoller.utils import create_logger

logger = create_logger('poller')

def main():
    load_dotenv()
    QUEUE_NAME = os.environ['MESSAGE_QUEUE_HOST'].split('/')[-1]

    slack_client = SlackClient(os.environ['SLACK_BOT_TOKEN'], logger=logger, channel_id=os.environ['SLACK_CHANNEL_ID'])

    async def callback(msg):
        logger.info(f" [x] Callback Received: {msg}")
        await slack_client.send(slack_client.channel_id, json.loads(msg), "json")


    poller = SQSPoller(QUEUE_NAME, logger, callbacks=[callback], sqs_region=os.environ['AWS_REGION'])
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(poller.poll())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
