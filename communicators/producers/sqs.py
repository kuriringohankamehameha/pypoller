import asyncio
import json
import logging
import os
import random
import sys
from copy import deepcopy
from string import Template, ascii_letters

import aiobotocore
import botocore.exceptions
from pypoller.communicators.producers.base import BaseProducer
from pypoller.exceptions import ValidationError
from pypoller.utils import create_logger, is_function


class SQSProducer(BaseProducer):
    """
    SQS Producer Class that performs long-polling and triggers asynchronous callbacks when a message is sent.
    All the callback functions (`callbacks`) must be of the form:
    ```
    async def callback(msg):
        pass
    ```
    """
    
    def __init__(
        self, queue_name: str, msg_generator,
        logger: logging.Logger, sqs_session = None,
        sqs_region: str = 'ap-south-1',
        callbacks: list = [],
        interrupt_exceptions = KeyboardInterrupt,
    ):
        """Create the SQS poller instance. Must contain the SQS queue_name, a logging.Logger object.

        Args:
            queue_name (str): The SQS queue name
            msg_generator (function): The message generator function.
            logger (logging.Logger): A logger for the poller
            sqs_region (str, optional): SQS region. Defaults to 'ap-south-1'.
            callbacks (list, optional): List of all `async` callback functions. All callback functions must be of the form:
            ```
            async def callback(msg):
                pass
            ```
        """
        self.queue_name = queue_name
        self.logger = logger
        self.sqs_region = sqs_region
        self.msg_generator = msg_generator
        self.callbacks = callbacks
        self.sqs_session = sqs_session
        self.interrupt_exceptions = interrupt_exceptions

        self.validate()


    def validate(self):
        """Runs validation on the newly created producer instance

        Raises:
            ValidationError: When there is an invalid parameter format
        """
        try:
            assert is_function(self.msg_generator), "msg_generator must a function or a lambda"
            assert issubclass(self.interrupt_exceptions, BaseException) or isinstance(self.interrupt_exceptions, tuple), "self.interrupt_exceptions must be an subclass / tuple of BaseException"
        except AssertionError as ae:
            raise ValidationError(f"{ae}")


    async def produce(self):
        """
        Coroutine for running a producer.
        Periodically pushes a message to the SQS.
        This will be stopped when a `KeyBoardInterrupt` exception occurs.
        """
        if self.sqs_session is None:
            self.sqs_session = aiobotocore.get_session()
        
        async with self.sqs_session.create_client('sqs', region_name=self.sqs_region) as client:
            try:
                response = await client.get_queue_url(QueueName=self.queue_name)
            except botocore.exceptions.ClientError as err:
                if err.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                    self.logger.critical(f"Queue {self.queue_name} does not exist")
                    raise
                else:
                    raise

            queue_url = response['QueueUrl']

            self.logger.info('Putting messages on the queue')

            try:
                # Message Generator Call Here
                msg = self.msg_generator()
                
                msg_body = json.dumps(msg, default=str)
                await client.send_message(
                    QueueUrl=queue_url,
                    MessageBody=msg_body,
                )

                payload = msg_body

                # Trigger all callbacks once sent
                self.callback_results = await self.trigger(payload, self.callbacks)

                self.logger.info(f'Pushed "{msg_body}" to queue')
            except self.interrupt_exceptions:
                pass

            self.logger.info('Finished')


    async def close(self):
        pass
