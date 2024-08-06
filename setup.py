import re
from setuptools import setup
from os import path

# Get version number
with open("src/courseeval/__init__.py", "r") as fd:
    match = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    )
    if match:
        version = match.group(1)
    else:
        raise RuntimeError("Cannot find version information")


# Get the  package info from the readme
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wcesapi",
    version=version,
    author="Tristan Shippen",
    author_email="tshippen@barnard.edu",
    description="API wrapper for Watermark's Course Evaluations and Surveys API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ts3448/wcesapi",
    packages=["wcesapi"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Education",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "pandas",
    ],
    extras_require={
        "dev": ["pytest", "requests-mock", "flake8", "black"],
    },
)
