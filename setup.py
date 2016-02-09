#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='gib_detect',
    version='0.1.0',
    packages=find_packages(),
    include_package_data = True,
    license='MIT license',
    description='gib_detect.is_gibberish(text): return True if text is gibberish',
    long_description=open('README.rst').read() + "\n\n",
    entry_points = {
        'console_scripts': [
            'train_gib_detect=gib_detect:train_cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
