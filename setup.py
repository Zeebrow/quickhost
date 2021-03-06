from setuptools import setup, find_packages
from pathlib import Path

print(f"setup.py=====> {find_packages(where=str(Path('src/quickhost')))}")
setup(
    name='quickhost',
    version='0.0.1',
    package_dir={'':str(Path('src'))},
    packages=find_packages(where=str(Path('src/quickhost'))),
    install_requires=[
        'boto3'
    ],
    scripts=[str(Path('src/scripts/main.py'))]
)
