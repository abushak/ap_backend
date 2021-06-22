import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        self.url = ""

    @staticmethod
    def make_request(url: str, headers=None, verify=True) -> BeautifulSoup:
        """
        makes HTTP get request
        :param verify:
        :param headers:
        :param url: url to make the request to
        :return: BeautifulSoup object
        """
        try:
            response = requests.get(url, verify=verify)
        except Exception as e:
            print(e, url)
            return None
        status = response.status_code
        if status == 200:
            return BeautifulSoup(response.text, 'html.parser')
        elif status != 404:
            print(status, url)
            return Scraper.make_request(url, headers, verify)
        print(url, status)
