import json
import os

from jinja2 import Environment, PackageLoader, meta


class BaseClient():
    """Base Client Class for the communicator module
    """
    def __init__(self, *args, **kwargs):
        self.client_type = "base"

    async def authorize(self, *args, **kwargs):
        raise NotImplementedError("All Clients must override authorize()")

    async def close(self):
        raise NotImplementedError("All Clients must override close()")
