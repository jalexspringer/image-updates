#!/usr/bin/env python

from setuptools import setup

setup(
    name="image-updates",
    version='0.1',
    py_modules=['updates'],
    install_requires=[
        'Click',
        'matplotlib',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        image-update=updates:plot_updates
    ''',
)
