#!/usr/bin/env python3
"""
Setup script for generated system
Allows installation as package for development and deployment
"""
from setuptools import setup, find_packages

# Read requirements
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="phase8_test_api",
    version="1.0.0",
    description="Generated system by Autocoder 5.1",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "phase8_test_api=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
