import re
from setuptools import setup, find_packages

# Get version number
with open("src/courseeval/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

if not version:
    raise RuntimeError("Cannot find version information")

# Read the contents of your README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="courseeval",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="API wrapper for the Course Evaluations and Surveys API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/courseeval",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
    python_requires='>=3.7',
    install_requires=[
        "requests",
        "pandas",
    ],
    extras_require={
        "dev": ["pytest", "requests-mock", "flake8", "black"],
    },
)