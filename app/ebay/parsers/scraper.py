import re
from random import choice

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from seleniumwire import webdriver
from django.conf import settings


PROXY = 'http://api.buyproxies.org/?a=showProxies&pid=153073&key=1b1d55ec3b1c3caad772aa4692f26bc4&port=12345'


def get_proxies_from_url(url):
    proxies = requests.get(url + '&format=2').text.strip()
    proxies = proxies.split('\n')
    return [x for x in proxies if x.strip()]


PROXIES = get_proxies_from_url(PROXY)


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

    @staticmethod
    def get_chrome_selenium():
        proxies, proxy = Scraper.get_random_proxy() if PROXIES else {}
        ua = UserAgent()
        userAgent = ua.random
        pattern1 = r'Firefox\/?(.*)'
        pattern2 = r'Chrome\/?(.*)'
        pattern3 = r'Safari\/?(.*)'
        userAgent = re.sub(pattern1, 'Firefox/87.0', userAgent)
        userAgent = re.sub(pattern2, 'Chrome/91.0.4472.106', userAgent)
        userAgent = re.sub(pattern3, 'Safari/605.1.15', userAgent)
        # TODO: need to change this path, because of the deletion of this directory in the future

        # chromedriver = r'/home/auto/sites/findcar.parts/delete_this/chromedriver'
        chromedriver = settings.CHROME_PATH
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(f'user-agent={userAgent}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        options = {
            'proxy': proxies
        }
        chrome = webdriver.Chrome(options=chrome_options, executable_path=chromedriver, seleniumwire_options=options)
        # chrome = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options, seleniumwire_options=options)
        chrome.set_window_size(1440, 900)
        return chrome, proxy

    def make_selenium_request(self, url: str):
        chrome, proxy = self.get_chrome_selenium()
        try:
            chrome.get(url)
            print('ok')
        except Exception as e:
            print('not ok')
            print(e, url)
            chrome.quit()
            return None, proxy
        return chrome, proxy

    @staticmethod
    def get_random_proxy():
        proxy = choice(PROXIES)
        return {
                   'http': 'http://' + proxy,
                   'https': 'http://' + proxy
               }, proxy
