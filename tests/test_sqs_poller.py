import asyncio
import os

from dotenv import load_dotenv
from pypoller.communicators.pollers.sqs import SQSPoller
from pypoller.utils import create_logger


def main():
    load_dotenv()
    QUEUE_NAME = os.environ['MESSAGE_QUEUE_HOST'].split('/')[-1]

    logger = create_logger('pollers')

    async def callback(msg):
        logger.info(f" [x] Received {msg}")

    poller = SQSPoller(QUEUE_NAME, logger, callbacks=[callback], sqs_region=os.environ['AWS_REGION'])
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(poller.poll())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
