import json
import random
import logging
from enum import Enum
from urllib.parse import urljoin
import concurrent.futures

import requests
from bs4 import BeautifulSoup


class SearchType(Enum):
    REPOSITORIES = 'repositories'
    ISSUES = 'issues'
    WIKIS = 'wikis'


class GitHubCrawlerError(Exception):
    pass


class GitHubCrawler:
    BASE_URL = 'https://github.com'
    SEARCH_URL = urljoin(BASE_URL, 'search')
    REQUEST_TIMEOUT = 10

    def __init__(self, keywords, search_type, proxies, logger):
        self.logger = logger
        self.keywords = keywords
        self.search_type = SearchType(search_type.lower())
        self.proxy = self._get_random_proxy(proxies)
        self.session = requests.Session()
        self.logger.info(
            f"GitHubCrawler initialized with keywords: {self.keywords}, search type: {self.search_type.value}")

    def _get_random_proxy(self, proxies):
        proxy = random.choice(proxies)
        self.logger.info(f"Selected proxy: {proxy}")
        return proxy

    def _make_request(self, url, params=None):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        proxies = {
            'http': self.proxy,
            'https': self.proxy
        }
        try:
            self.logger.info(f"Making request to {url}")
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                proxies=proxies,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            self.logger.info(f"Request successful: {response.status_code}")
            return response
        except requests.RequestException as e:
            self.logger.error(f"Error making request: {e}")
            raise GitHubCrawlerError(f"Error making request: {e}")

    def run(self, filename_to_save='crawler_result.json'):
        self.logger.info("Starting crawler run")
        search_result = self.search()
        with open(filename_to_save, 'w') as f:
            json.dump(search_result, f)
        self.logger.info(f"Crawler run completed. Results saved to {filename_to_save}")

    def search(self):
        params = {
            "q": " ".join(self.keywords),
            "type": self.search_type.value
        }
        self.logger.info(f"Performing search with params: {params}")
        result = self._make_request(url=self.SEARCH_URL, params=params)
        return self._parse_search_result(result)

    def _parse_search_result(self, search_result):
        self.logger.info("Parsing search results")
        soup = BeautifulSoup(search_result.text, 'html.parser')
        divs = soup.find_all('div', class_="search-title")
        urls = [div.find('a').get('href') for div in divs]
        self.logger.info(f"Found {len(urls)} results")

        if self.search_type == SearchType.REPOSITORIES:
            self.logger.info("Fetching extra info for repositories")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                extra_info_list = list(executor.map(self._get_extra_info, urls))
            parsed_result = [{'url': url, 'extra': extra_info} for url, extra_info in zip(urls, extra_info_list)]
        else:
            parsed_result = [{'url': url} for url in urls]

        self.logger.info("Parsing completed")
        return parsed_result

    def _get_extra_info(self, repository_url):
        self.logger.info(f"Fetching extra info for {repository_url}")
        extra_info = {
            'owner': repository_url.split('/')[1],
            'language_stats': {}
        }
        url = urljoin(self.BASE_URL, repository_url)
        result = self._make_request(url)
        soup = BeautifulSoup(result.text, 'html.parser')
        layout_sidebar = soup.find('div', class_="Layout-sidebar")
        languages = layout_sidebar.find_all('li', class_='d-inline')
        for language in languages:
            text, percentage = [language_object.text for language_object in language.find_all('span')]
            percentage = percentage.replace('%', '')
            extra_info['language_stats'][text] = float(percentage)
        self.logger.info(f"Extra info fetched for {repository_url}")
        return extra_info
