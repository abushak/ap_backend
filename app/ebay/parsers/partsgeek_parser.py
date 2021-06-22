import re

from ebay.parsers.scraper import Scraper


def get_data(item, url):
    return {
        "url": url,
        "brand": item.find('span', {'itemprop': 'brand'}).text,
        "title": item.find("div", {"class": "product-title"}).text.strip(),
        "price": item.find("span", {'itemprop': 'price'}).text,
        "thumbnail_url": item.find("img", {"class": "pg-image-popover"})['src'],
        "part_number": item.find("span", {'itemprop': 'sku'}).text,

    }


def is_relevant(title, keywords):
    return all(x in title.lower() for x in keywords.split())


def get_car_part_by_keywords(keywords):
    pattern1 = "\d{1}[\,\.]{1}\d{1}l?L?"
    pattern2 = "\d{4}"
    if bool(re.search(pattern1, keywords)):
        mod_keyword = re.split(pattern1, keywords)
        mod_keyword = mod_keyword[1].strip().lower()
    else:
        if bool(re.search(pattern2, keywords)):
            mod_keyword = re.split(pattern2, keywords)
            mod_keyword = mod_keyword[1].strip().lower()
        else:
            mod_keyword = keywords
    return mod_keyword


class PartsGeek(Scraper):
    """ partsgeek.com Scraping class"""

    def find_goods(self, url, keywords):
        """
        Goes to website and finds goods
        """
        link = url + keywords
        link = link.replace(" ", "+")
        self.url = link
        soup = Scraper.make_request(self.url)
        if not soup:
            return
        '''Pagination doesn't work properly on this site'''
        # items = []
        # if soup.find("ul", {"class": "pagination"}):
        #     items.append(soup.find_all("div", {"class": "product"}))
        #     for i in range(2, 6):
        #         soup = Scraper.make_request(self.url + "&page={}".format(i))
        #         items.append(soup.find_all("div", {"class": "product"}))
        #     items = [item for sublist in items for item in sublist]
        # else:
        #     items = soup.find_all("div", {"class": "product"})
        items = soup.find_all("div", {"class": "product"})
        result = [get_data(item, url + keywords) for item in items]
        car_part = get_car_part_by_keywords(keywords)
        result = [item for item in result if is_relevant(item['title'], car_part)]
        return result
