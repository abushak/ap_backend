import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.ebay.parsers.scraper import Scraper


def get_data(li):
    return {
        "url": li.find_element_by_css_selector("a.link").get_attribute("href"),
        "brand": li.find_element_by_css_selector("span.title").text,
        "title": li.find_element_by_css_selector("span.sub-title").text,
        "price": li.find_element_by_css_selector("span.autoc-today-price").text.replace('$', ''),
    }


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


class CarId(Scraper):
    """ carid.com Scraping class"""

    def get_part_number(self, item, driver):
        driver.get(item.get("url"))
        res = []
        parent = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(),'Part Number')]"))
        )
        content_div = parent.find_element_by_xpath("./following-sibling::div")
        part_numbers = content_div.find_elements_by_xpath(".//*")
        if len(part_numbers) > 0:
            for part_number in part_numbers:
                res.append(part_number.text)
        else:
            res.append(content_div.text)
        item.update({"part_number": res})
        return item

    def find_goods(self, url, keywords):
        """
        Goes to website and finds goods
        """
        driver, proxy = CarId.make_selenium_request(self, url)
        if not driver:
            return
        # Search for products using the search box
        search_bar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[4]/div/header/div[1]/div/div[2]/div"))
        )
        search_bar.click()
        inputElement = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[9]/div[2]/div/div[1]/div[1]/div/form/div[2]/div/input"))
        )
        inputElement.send_keys(keywords)
        time.sleep(4)
        try:
            show_more_products_btn = driver.find_element_by_xpath(
                "/html/body/div[9]/div[2]/div/div[1]/div[1]/div/form/div[3]/div/div/div[3]/div/div/div/a")
        except NoSuchElementException:
            show_more_products_btn = None
        if show_more_products_btn is None:
            ul = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[9]/div[2]/div/div[1]/div[1]/div/form/div[3]/div/div/div[3]/div/ul"))
            )
            all_li = ul.find_elements_by_tag_name("li")
            result = [get_data(li) for li in all_li]
            # result = [self.get_part_number(item, driver) for item in items]
        else:
            result = []
            show_more_products_btn.click()
            # Selecting the number of products to display
            items_count = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="prod-list"]/div[2]/div[1]/div[1]/div[1]/ul/li[3]/label'))
            )
            items_count.click()
            ul = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="prod-list"]/div[2]/div[3]/ul'))
            )
            all_li = ul.find_elements_by_tag_name("li")
            car_part = get_car_part_by_keywords(keywords)
            for li in all_li:
                pattern = r'[0-9]'
                org_title = li.find_element_by_css_selector("span.lst-a-name").text
                title = re.sub(pattern, '', org_title)
                if not all(ele in title.lower() for ele in car_part.lower().split()):
                    continue
                res = {
                    'title': org_title,
                    'brand': li.find_element_by_css_selector("b.lst-a-name").text,
                    'url': li.find_element_by_css_selector("a.lst_a").get_attribute('href'),
                    'thumbnail_url': li.find_element_by_css_selector("img.lst_ic").get_attribute('data-src'),
                    'price': li.find_element_by_css_selector("span.lst_prc").text.replace('$', ''),
                }
                result.append(res)
            # result = [self.get_part_number(item, driver) for item in result]
        driver.quit()

        return result
