import asyncio


class BaseProducer():
    """Base Class for all Producers. Any Class subclassing this must implement the following methods:
    1. validate() -> Blocking method
    2. produce() -> Non Blocking coroutine
    3. close() -> Non Blocking coroutine
    """

    def __init__(self, *args, **kwargs):
        pass

    def validate(self, *args, **kwargs):
        raise NotImplementedError("All Producer classes must override validate()")

    async def produce(self, *args, **kwargs):
        raise NotImplementedError("All Producer classes must override produce()")

    async def close(self, *args, **kwargs):
        raise NotImplementedError("All Producer classes must override close()")

    async def trigger(self, payload, callbacks):
        """Triggers calls to a list of asynchronous callback functions with the same payload as input.
        """
        input_coroutines = [callback(payload) for callback in callbacks]
        return await asyncio.gather(*input_coroutines, return_exceptions=True)
