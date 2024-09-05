# GitHub Crawler

## Overview

GitHub Crawler is a Python-based tool designed to perform targeted searches on GitHub and retrieve relevant search results. It supports searching for repositories, issues, and wiki pages, utilizing proxy servers for request management.

## Features

- Executes GitHub searches based on user-defined keywords
- Supports three search types: repositories, issues, and wikis
- Implements proxy server usage for HTTP requests
- Retrieves additional metadata for repository results (owner, language statistics)
- Outputs search results in JSON format

## Prerequisites

- Python 3.9+
- Required libraries as specified in `requirements.txt`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/ivayanc/github-crawler.git
   cd github-crawler
   ```

2. Set up a virtual environment:
   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Configure the search parameters in `input_data.json`:
   ```json
   {
    "keywords": ["openstack", "nova", "css"],
    "proxies": ["88.216.34.140:50100", "89.117.250.68:50100"],
    "type": "Repositories"
   }
   ```

   Input Data Specifications:
   - `keywords`: An array of strings representing search terms
   - `proxies`: An array of strings in IP:PORT format
   - `type`: A string specifying the search type. Valid options are:
     - `"Repositories"`: For repository searches
     - `"Issues"`: For issue searches
     - `"Wikis"`: For wiki page searches

2. Execute the script:
   ```
   python main.py
   ```

3. Retrieve results from `crawler_result.json`

## Project Structure

- `main.py`: Entry point for the application
- `github_crawler.py`: Core logic implementation
- `test_github_crawler.py`: Unit test suite
- `input_data.json`: Configuration file for search parameters
- `requirements.txt`: Project dependencies

## Testing

Execute the test suite:
```
python -m unittest test_github_crawler.py
```

For code coverage analysis:
```
coverage run -m unittest test_github_crawler.py
coverage report -m
```

## Limitations

- The crawler processes only the first page of search results

## Notes

- The provided proxy servers are examples and may not be operational.
