#!/usr/bin/env python3
"""
Setup script to install multi-agent system as a Python package
"""
from setuptools import setup, find_packages

setup(
    name="multi-agent-system",
    version="1.0.0",
    description="Multi-agent development system for 100/100 quality implementations",
    author="Autocoder Team",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "pathlib",
        "typing-extensions"
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'multi-agent=multi_agent_system.cli:main',
        ],
    },
    package_data={
        'multi_agent_system': [
            'templates/*.md',
            'examples/*.py'
        ]
    }
)