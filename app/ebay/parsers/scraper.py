from random import choice

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

PROXY = 'http://api.buyproxies.org/?a=showProxies&pid=153073&key=1b1d55ec3b1c3caad772aa4692f26bc4&port=12345'


def get_proxies_from_url(url):
    proxies = requests.get(url + '&format=2').text.strip()
    proxies = proxies.split('\n')
    return [x for x in proxies if x.strip()]


# PROXIES = get_proxies_from_url(PROXY)

PROXIES = [
    {'proxy': 'parts:parts0109@192.3.147.50:12345', "is_used": False},
    # {'proxy': 'parts:parts0109@107.174.149.221:12345', "is_used": False},
    {'proxy': 'parts:parts0109@104.206.203.130:12345', "is_used": False},
    # {'proxy': 'parts:parts0109@196.196.112.214:12345', "is_used": False},
    {'proxy': 'parts:parts0109@107.175.58.17:12345', "is_used": False},
    {'proxy': 'parts:parts0109@192.3.147.52:12345', "is_used": False},
    {'proxy': 'parts:parts0109@107.175.58.24:12345', "is_used": False},
    {'proxy': 'parts:parts0109@192.3.147.55:12345', "is_used": False},
]


def set_proxy_status(proxy, status):
    for x in PROXIES:
        if proxy.get('proxy') == x.get('proxy'):
            x['is_used'] = status
            break


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
        # chromedriver = r'/root/ygo_scripts/ygo-scraper/chromedriver/chromedriver'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(f'user-agent={userAgent}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.binary_location = '/usr/bin/google-chrome'
        options = {
            'proxy': proxies
        }
        print('------------------------------')
        print(proxies)
        # chrome = webdriver.Chrome(options=chrome_options, executable_path=chromedriver, seleniumwire_options=options)
        chrome = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options, seleniumwire_options=options)
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
        # 'parts:parts0109@192.3.147.50:12345'
        # 'parts:parts0109@107.174.149.221:12345',
        # 'parts:parts0109@104.206.203.130:12345',  # dont work
        # # 'parts:parts0109@172.245.195.154:12345',#dont work
        # 'parts:parts0109@196.196.112.214:12345',
        # # 'parts:parts0109@104.206.203.10:12345',#dont work
        # 'parts:parts0109@107.175.58.17:12345',
        # 'parts:parts0109@192.3.147.52:12345',
        # 'parts:parts0109@107.175.58.24:12345',
        # 'parts:parts0109@192.3.147.55:12345']
        proxy = choice(PROXIES)
        while proxy.get('is_used'):
            proxy = choice(PROXIES)
        set_proxy_status(proxy, True)
        return {
                   'http': 'http://' + proxy.get('proxy'),
                   'https': 'http://' + proxy.get('proxy')
               }, proxy
