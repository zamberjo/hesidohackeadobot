#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from glob import glob
from setuptools import find_packages, setup
from os.path import join, dirname

setup(
    name = 'HeSidoHackeadoBot',
    packages = ['hesidohackeadobot'],
    version = '1.0',
    description = 'Bot telegram para uso de la API de www.hesidohackeado.com',
    url='https://github.com/zamberjo/hesidohackeadobot',
    author='Jose Zambudio Bernabeu',
    author_email='zamberjo@gmail.com',
    license='LGPL-3',
    scripts=['hshbot.py'],
    install_requires=[
        'pyTelegramBotAPI >= 0.3.9',
        'pymongo >= 3.0.3',
        'python-crontab >= 1.9.3',
        'ndg-httpsclient >= 0.4.0',
        'pyasn1 >= 0.1.9',
        'pyOpenSSL >= 0.13',
        'configparser',
    ],
    # classifiers=[
    #     'Programming Language :: Python',
    #     'Programming Language :: Python :: 2.7',
    #     'License :: OSI Approved :: GNU General Public License (GPL)',
    #     'Operating System :: OS Independent',
    #     'Development Status :: 1 - Planning',
    #     'Environment :: Console',
    #     'Intended Audience :: Science/Research',
    #     'Topic :: Scientific/Engineering :: GIS'
    # ]
)
