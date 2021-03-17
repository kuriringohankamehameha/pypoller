import asyncio
import json
import os
import random
import sys
from copy import deepcopy
from string import ascii_letters

import aiobotocore
import botocore.exceptions
import motor.motor_asyncio
from dotenv import load_dotenv
from pypoller.communicators.producers.sqs import SQSProducer
from pypoller.utils import create_logger

logger = create_logger('producer')

template = {
    "field1": "",
    "field2": "",
}


def make_message():
    message = deepcopy(template)
    message["field1"] = ''.join([random.choice(ascii_letters) for _ in range(random.randint(8, 15))])
    message["field2"] = random.choice(["A", "B"])
    return message


async def callback(msg):
    logger.info(f" [x] Received: {msg}")


async def produce(producer):
    while True:
        try:
            await producer.produce()
            await asyncio.sleep(10)
            # await asyncio.sleep(random.randint(1, 4))
        except KeyboardInterrupt:
            break


def main():
    load_dotenv()
    
    QUEUE_NAME = os.environ['MESSAGE_QUEUE_HOST'].split('/')[-1]

    try:
        loop = asyncio.get_event_loop()
        producer = SQSProducer(QUEUE_NAME, make_message, logger, callbacks=[callback], sqs_region=os.environ['AWS_REGION'])    
        loop.run_until_complete(produce(producer))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
