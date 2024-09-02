from setuptools import find_packages, setup

# Read the dependencies from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="music_bot",
    version="0.0.1",
    author="Komal",
    author_email="komalfsds2022@gmail.com",
    packages=find_packages(),
    install_requires=requirements,
)