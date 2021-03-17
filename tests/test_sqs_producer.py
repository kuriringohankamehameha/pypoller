import asyncio
import os

from dotenv import load_dotenv
from pypoller.communicators.producers.sqs import SQSProducer
from pypoller.utils import create_logger


def generate_msg():
    return {
        "field": "value"
    }


def main():
    load_dotenv()
    QUEUE_NAME = os.environ['MESSAGE_QUEUE_HOST'].split('/')[-1]

    logger = create_logger("producers")

    producer = SQSProducer(QUEUE_NAME, generate_msg, logger, sqs_region=os.environ['AWS_REGION'])
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(producer.produce())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
