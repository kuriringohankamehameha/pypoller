from distutils.core import setup

# from setuptools import setup, find_packages

setup(
    name = 'pypoller',
    version = '0.0.1',
    package_dir = {'pypoller': '.'},
    packages = [
        'pypoller', 'pypoller.communicators', 'pypoller.communicators.templates',
        'pypoller.examples',
        'pypoller.communicators.pollers',
        'pypoller.communicators.producers',
        'pypoller.communicators.email', 'pypoller.communicators.slack',
    ],
    package_data = {'pypoller.communicators.templates': ['*', '*/*', '*/*/*'],}, # Template Directory structure
    python_requires = '>=3.6',
    author = 'Vijay Krishna',
    author_email = 'accornition@gmail.com',
    description = 'A Generic Library for incorporating asynchronous polling in Python',
    url = "https://github.com/kuriringohankamehameha/pypoller",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
