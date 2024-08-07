# wcesapi

wcesapi is a Python wrapper for Watermark's Course Evaluations and Surveys (CES) API. This library simplifies the process of interacting with the CES API, allowing developers to leverages object relationships within the API to efficiently retrieve and manipulate course evaluation data.

## Installation

Currently, wcesapi is not available on PyPI. To use it, you'll need to clone the repository:

```bash
git clone https://github.com/ts3448/wcesapi.git
cd wcesapi
pip install -e .
```

## Getting Started

The library centers around a primary class, `CES`, which serves as the entrypoint to the API.

Instantiate a new `CES` object by providing your CES instance's API URL and a valid API key:

```python
# Import the CES class
from wcesapi import CES

# CES API URL
API_URL = "https://your-ces-instance.evaluationkit.com"

# CES API token
API_TOKEN = "your-access-token"

# Initialize a new CES object
ces_client = CES(API_URL, API_KEY)
```

## API Scope and Access

Many institutions use child instances of a parent CES installation, which impacts the base URL you should use and the data you can access. 
You should use the specific domain or subdomain associated with your API token. For example:

- Parent instance: `school.evaluationkit.com`
- Your institution's child instance where the API token was generated: `subaccount-school.evaluationkit.com`

Attempting to use the root URL of the parent instance may result in insufficient permissions errors.

In this case, you would initialize the CES client like this:

```python
API_URL = "https://subaccount-school.evaluationkit.com"
ces_client = CES(API_URL, API_KEY)
```

## Navigating CES Entities

wcesapi transforms the CES API's JSON responses into Python objects backed by pandas DataFrames. This approach offers powerful data manipulation capabilities and simplifies data visualization.

### Exploring Courses

Fetch and analyze course data:

```python
# Retrieve all courses
courses = ces_client.list_courses()

# View the courses as a DataFrame
print(courses.df)

# Access a specific column for all courses
print(courses.title)

# Filter courses based on a condition
fall_courses = courses[courses.title.str.contains('Fall 2023')]
```

### Unique Feature: Automatic Method Application

One of the most powerful features of wcesapi is its ability to automatically apply methods to all entries in a DataFrame. When you call a method on response object (Course, Survey, Project, etc.), it's applied to every row in the underlying DataFrame, returning a new object with the combined results.

For example:

```python
# Get projects for all courses in one operation
>>> course_projects = courses.list_projects()
```

This single line effectively does the following:
1. Calls list_projects() for each course
2. Combines all the results into a single DataFrame
3. Returns a new Project instance containing all projects for all courses

## Acknowledgements

### Independent Project

wcesapi is an independent project and is not officially associated with or endorsed by Watermark Insights. It is designed as a third-party tool to facilitate interaction with the Watermark Course Evaluations and Surveys (CES) API.

### Inspiration

This project was heavily inspired by the [canvasapi](https://github.com/ucfopen/canvasapi/) library created by the University of Central Florida - Open Source team. We are grateful for their work, which provided a valuable model for creating an intuitive and powerful API wrapper.

### Disclaimer

While we strive to maintain accuracy and compatibility with the Watermark CES API, users should be aware that this is an unofficial tool. Always refer to the official Watermark CES API documentation for the most up-to-date and authoritative information.


### License

This project is licensed under the MIT License. Please see the LICENSE file in the repository for full details.
