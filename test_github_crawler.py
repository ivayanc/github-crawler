import unittest
from unittest.mock import patch, MagicMock
import requests
from src.github_crawler import GitHubCrawler, GitHubCrawlerError, SearchType


class TestGitHubCrawler(unittest.TestCase):

    def setUp(self):
        self.keywords = ["python", "crawler"]
        self.search_type = SearchType.REPOSITORIES
        self.proxies = ["http://proxy1.com:8080", "http://proxy2.com:8080"]
        self.crawler = GitHubCrawler(self.keywords, self.search_type.value, self.proxies)

    def test_init(self):
        self.assertEqual(self.crawler.keywords, ["python", "crawler"])
        self.assertEqual(self.crawler.search_type, SearchType.REPOSITORIES)
        self.assertIn(self.crawler.proxy, self.proxies)

    @patch('requests.Session.get')
    def test_make_request(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = self.crawler._make_request("https://github.com/search")

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

    @patch('requests.Session.get')
    def test_make_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Error")

        with self.assertRaises(GitHubCrawlerError):
            self.crawler._make_request("https://github.com/search")

    @patch('src.github_crawler.GitHubCrawler._make_request')
    @patch('src.github_crawler.GitHubCrawler._get_extra_info')
    def test_search(self, mock_get_extra_info, mock_make_request):
        mock_response = MagicMock()
        mock_response.text = """
        <html><body>
            <div class='search-title'><a href='/repo1'>Repo 1</a></div>
            <div class='search-title'><a href='/repo2'>Repo 2</a></div>
        </body></html>
        """
        mock_make_request.return_value = mock_response
        mock_get_extra_info.return_value = {'owner': 'test_owner', 'language_stats': {'Python': 100.0}}

        result = self.crawler.search()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['url'], '/repo1')
        self.assertEqual(result[0]['extra'], {'owner': 'test_owner', 'language_stats': {'Python': 100.0}})
        self.assertEqual(result[1]['url'], '/repo2')
        self.assertEqual(result[1]['extra'], {'owner': 'test_owner', 'language_stats': {'Python': 100.0}})

    @patch('src.github_crawler.GitHubCrawler._make_request')
    def test_get_extra_info(self, mock_make_request):
        mock_response = MagicMock()
        mock_response.text = """
        <html><body>
            <div class="Layout-sidebar">
                <li class='d-inline'><span>Python</span><span>80%</span></li>
                <li class='d-inline'><span>JavaScript</span><span>20%</span></li>
            </div>
        </body></html>
        """
        mock_make_request.return_value = mock_response

        extra_info = self.crawler._get_extra_info('/owner/repo')

        self.assertEqual(extra_info['owner'], 'owner')
        self.assertEqual(extra_info['language_stats'], {'Python': 80.0, 'JavaScript': 20.0})

    @patch('src.github_crawler.GitHubCrawler._make_request')
    def test_get_extra_info_no_languages(self, mock_make_request):
        mock_response = MagicMock()
        mock_response.text = """
        <html><body>
            <div class="Layout-sidebar">
            </div>
        </body></html>
        """
        mock_make_request.return_value = mock_response

        extra_info = self.crawler._get_extra_info('/owner/repo')

        self.assertEqual(extra_info['owner'], 'owner')
        self.assertEqual(extra_info['language_stats'], {})

    @patch('src.github_crawler.GitHubCrawler.search')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_run(self, mock_open, mock_search):
        mock_search.return_value = [{'url': '/repo1'}, {'url': '/repo2'}]

        self.crawler.run()

        mock_open.assert_called_once_with('crawler_result.json', 'w')
        mock_open().write.assert_called_once()

    def test_invalid_search_type(self):
        with self.assertRaises(ValueError):
            GitHubCrawler(self.keywords, "invalid_type", self.proxies)

    def test_empty_proxies(self):
        with self.assertRaises(IndexError):
            GitHubCrawler(self.keywords, self.search_type.value, [])


if __name__ == '__main__':
    unittest.main()
