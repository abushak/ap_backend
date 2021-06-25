import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.ebay.parsers.scraper import Scraper


def get_data(item, content):
    return {
        "url": item.find_elements_by_tag_name('a')[0].get_attribute("href"),
        "thumbnail_url": item.find_elements_by_tag_name("img")[0].get_attribute("src"),
        "brand": content.splitlines()[0],
        "title": content.splitlines()[1],
        "part_number": content.splitlines()[2].split()[-1],
        "price": content.splitlines()[5].replace("$", ''),
    }


class CarParts(Scraper):
    """ carparts.com Scraping class"""

    def find_goods(self, url, keywords):
        """
        Goes to website and finds goods
        """
        driver, proxy = CarParts.make_selenium_request(self, url)
        if not driver:
            return
        if ' ' in keywords:
            pattern = r'\d{1}[\,\.]{1}\d{1}l?'
            # Remove the volume of the motor if it is specified in the search query
            mod_keyword = re.sub(pattern, '', keywords)
        else:
            mod_keyword = keywords
        search_bar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.ID, "searchBox"))
        )
        search_bar.click()
        search_bar.send_keys(mod_keyword)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(4)
        all_items = driver.find_elements_by_xpath("//div[contains(@id, 'sectionCard-')]")
        result = [get_data(item, item.text) for item in all_items]

        driver.close()
        driver.quit()

        return result
