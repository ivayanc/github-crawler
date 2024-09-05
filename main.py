import json
import logging
from github_crawler import GitHubCrawler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    with open('input_data.json', 'r') as f:
        input_data = json.load(f)
    keywords = input_data.get('keywords', [])
    search_type = input_data.get('type', '')
    proxies = input_data.get('proxies', [])

    logger.info(f"Initializing GitHubCrawler with keywords: {keywords}, search type: {search_type}")
    crawler = GitHubCrawler(keywords=keywords, search_type=search_type, proxies=proxies, logger=logger)
    crawler.run()
