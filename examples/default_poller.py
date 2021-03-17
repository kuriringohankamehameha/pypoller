import asyncio
import json
import logging
import os
import sys
from string import Template

import aiobotocore
import botocore.exceptions
from dotenv import load_dotenv
from pypoller.communicators.pollers.sqs import SQSPoller
from pypoller.utils import create_logger

logger = create_logger('consumer')


async def callback(msg):
    logger.info(f" [x] Received {msg}")


def main():
    load_dotenv()
    QUEUE_NAME = os.environ['MESSAGE_QUEUE_HOST'].split('/')[-1]

    poller = SQSPoller(QUEUE_NAME, logger, callbacks=[callback], sqs_region=os.environ['AWS_REGION'])
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(poller.poll())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
