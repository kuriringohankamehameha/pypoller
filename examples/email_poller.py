import asyncio
import json
import os

from dotenv import load_dotenv
from pypoller.communicators.email.client import EmailClient
from pypoller.communicators.pollers.sqs import SQSPoller
from pypoller.utils import create_logger

logger = create_logger('poller')

def main():
    load_dotenv()
    QUEUE_NAME = os.environ['MESSAGE_QUEUE_HOST'].split('/')[-1]

    email_client = EmailClient(os.environ['EMAIL_HOST_USER'], os.environ['EMAIL_HOST_PASSWORD'], logger=logger)

    async def callback(msg):
        logger.info(f" [x] Callback Received: {msg}")
        await email_client.send([os.environ['EMAIL_RECEIVER_ADDRESS']], json.loads(msg), msg_type="json")

    poller = SQSPoller(QUEUE_NAME, logger, callbacks=[callback], sqs_region=os.environ['AWS_REGION'])
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(poller.poll())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
