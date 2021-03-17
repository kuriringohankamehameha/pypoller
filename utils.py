import logging
import logging.handlers
import os
import re
import types
from collections import OrderedDict


def is_function(obj):
    """Predicate to check if `obj` is a function
    """
    return isinstance(obj, (types.FunctionType, types.LambdaType))


def create_logger(app_name: str) -> logging.Logger:
    """Creates the logger for the current application

    Args:
        app_name (str): The name of the application

    Returns:
        logging.Logger: A logger object for that application
    """
    logger = logging.getLogger(f"{app_name}-logger")
    logger.setLevel(logging.DEBUG)

    # Also add a StreamHandler for printing to stderr
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    
    return logger


def insert_template_placeholders(template: str, data: dict):
    """Performs a regex replacement of a template string from the data.

    Notice that the template *MUST* be of the form `{{ key }}`.

    Example: `"Hello {{ name }}"` with `{"name": "xyz"}` -> `"Hello xyz"`
    """
    pattern = r"\{\{\s([A-Za-z0-9_]+)\s\}\}"
    matches = OrderedDict() # Use an ordered dict to preserve match occurence order
    
    def replace_function(match):
        # Strip away the '{{\s' and '\s}}' from the match string
        match = match.group()[3:-3]
        matches[match] = None
        return str(data.get(match, ""))
    
    message = re.sub(pattern, replace_function, template)
    return message, list(matches.keys())
