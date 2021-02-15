from setuptools import setup
from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='AirThings-API',
    version='0.1.2',
    description='Python Wrappers for AirThings API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Benjamin Raibaud',
    author_email='braibaud@gmail.com',
    url='https://github.com/braibaud/airthings-api',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'aiohttp>=3.7.0',
    ],
    python_requires='>=3.7',
    packages=find_packages())