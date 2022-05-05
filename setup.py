from setuptools import setup, find_packages

setup(
    name='quickhost',
    version='0.0.1',
    package_dir={'':'src'},
    packages=find_packages(where='src/quickhost'),
    install_requires=[
        'boto3'
    ],
    scripts=['src/scripts/main.py']
)