import asyncio
import json
import logging
import os
import sys
from string import Template

import aiobotocore
import botocore.exceptions
from pypoller.communicators.email.client import EmailClient
from pypoller.communicators.pollers.base import BasePoller
from pypoller.communicators.slack.client import SlackClient
from pypoller.exceptions import ValidationError


class SQSPoller(BasePoller):
    """
    SQS Poller class which performs long-polling and triggers asynchronous callbacks when a message is present.
    All the callback functions (`callbacks`) must be of the form:
    ```
    async def callback(msg):
        pass
    ```
    """
    
    callback_results = None # Variable for retrieving the callback results

    def __init__(self, queue_name: str,
    logger: logging.Logger, period=30, 
    callbacks: list = [], sqs_region: str = 'ap-south-1',
    sqs_wait_time: int = 1, sqs_max_msgs: int = 10,
    interrupt_exceptions = KeyboardInterrupt,
    ):
        """Create the SQS poller instance. Must contain the SQS queue_name, a logging.Logger object.

        Args:
            queue_name (str): The SQS queue name
            logger (logging.Logger): A logger for the poller
            period (int, optional): Polling interval. Defaults to 30.
            callbacks (list, optional): List of all `async` callback functions. All callback functions must be of the form:
            ```
            async def callback(msg):
                pass
            ```
            sqs_region (str, optional): SQS region. Defaults to 'ap-south-1'.
            sqs_wait_time (int, optional): SQS wait time. Defaults to 1.
            sqs_max_msgs (int, optional): Maximum number of SQS messages to be gathered from a single AWS API call. Defaults to 10.
        """
        self.queue_name = queue_name
        self.logger = logger
        self.callbacks = callbacks
        self.sqs_region = sqs_region
        self.sqs_wait_time = sqs_wait_time
        self.sqs_max_msgs = sqs_max_msgs
        self.period = period
        self.interrupt_exceptions = interrupt_exceptions

        self.validate()


    def validate(self):
        """Runs validation on the newly created poller instance

        Raises:
            ValidationError: When there is an invalid parameter format
        """
        try:
            assert isinstance(self.logger, logging.Logger), "self.logger must be an instance of logging.Logger"
            assert self.sqs_wait_time >= 0, "SQS wait time must be non-negative"
            assert self.sqs_max_msgs >= 1 and self.sqs_max_msgs <= 10, "Can only fetch between [1, 10] messages from a single SQS call"
            assert self.period >= 0, "Polling interval must be non-negative"
            assert issubclass(self.interrupt_exceptions, BaseException) or isinstance(self.interrupt_exceptions, tuple), "self.interrupt_exceptions must be an subclass / tuple of BaseException"
        except AssertionError as ae:
            raise ValidationError(f"{ae}")
    

    async def poll(self):
        """
        Coroutine for running the long polling consumer.
        Periodically polls from the SQS for any messages, and performs callbacks from `self.callbacks` whenever a message is present.
        """
        session = aiobotocore.get_session()

        async with session.create_client('sqs', region_name=self.sqs_region) as client:
            try:
                response = await client.get_queue_url(QueueName=self.queue_name)
            except botocore.exceptions.ClientError as err:
                if err.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                    self.logger.critical("Queue {0} does not exist".format(self.queue_name))
                    raise
                else:
                    raise

            queue_url = response['QueueUrl']

            self.logger.info('Pulling messages off the queue')

            while True:
                try:
                    response = await client.receive_message(
                        QueueUrl=queue_url,
                        WaitTimeSeconds=self.sqs_wait_time,
                        MaxNumberOfMessages=self.sqs_max_msgs,
                    )

                    if 'Messages' in response:
                        while 'Messages' in response and len(response['Messages']) > 0:
                            for msg in response['Messages']:
                                # self.logger.info(f'Got msg "{msg["Body"]}"')

                                # Now perform all necessary non-blocking callbacks
                                payload = msg["Body"]
                                self.callback_results = await self.trigger(payload, self.callbacks)

                                # Need to remove msg from queue or else it'll reappear
                                await client.delete_message(
                                    QueueUrl=queue_url,
                                    ReceiptHandle=msg['ReceiptHandle']
                                )
                            
                            response = await client.receive_message(
                                QueueUrl=queue_url,
                                WaitTimeSeconds=self.sqs_wait_time,
                                MaxNumberOfMessages=self.sqs_max_msgs,
                            )
                    else:
                        self.logger.info('No messages in queue')
                    
                    await asyncio.sleep(self.period)

                except self.interrupt_exceptions:
                    break

            self.logger.info('Finished')


    async def close(self):
        pass
