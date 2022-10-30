#!/usr/bin/env python

# Copyright (c) 2022 Guillaume Charbonnier.
# All Rights Reserved.

from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="ansible-runner-nats",
    version="0.1.0",
    author="Guillaume Charbonnier",
    url="https://github.com/charbonnierg/ansible-runner-nats",
    license="Apache",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "nats-py",
    ],
    extras_require={
        "nkeys": ["nats-py[nkeys]"],
        "websocket": ["aiohttp"],
        "tests": [
            "ansible-runner",
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
        ],
        "dev": ["black", "isort", "flake8", "mypy"],
        "ansible": ["ansible"],
    },
    entry_points={"ansible_runner.plugins": "nats = ansible_runner_nats"},
    zip_safe=False,
)
