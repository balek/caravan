#!/usr/bin/env python

from setuptools import setup

setup(name = 'caravan',
    version = '0.0.1',
    description = 'Home automation framework',
    author = 'Alexey Balekhov',
    author_email = 'a@balek.ru',
    packages = ['caravan'],
    entry_points = {
        'autobahn.twisted.wamplet': [ 'props = caravan.props:AppSession' ]
    })