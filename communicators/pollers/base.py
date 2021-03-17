import asyncio


class BasePoller():
    """Base Class for all Pollers. Any Class subclassing this must implement the following methods:
    1. validate() -> Blocking method
    2. poll() -> Non Blocking coroutine
    3. close() -> Non Blocking coroutine
    """

    def __init__(self, *args, **kwargs):
        pass

    def validate(self, *args, **kwargs):
        raise NotImplementedError("All Poller classes must override validate()")

    async def poll(self, *args, **kwargs):
        raise NotImplementedError("All Poller classes must override poll()")

    async def close(self, *args, **kwargs):
        raise NotImplementedError("All Poller classes must override close()")

    async def trigger(self, payload, callbacks):
        """Triggers calls to a list of asynchronous callback functions with the same payload as input.
        """
        input_coroutines = [callback(payload) for callback in callbacks]
        return await asyncio.gather(*input_coroutines, return_exceptions=True)
