import sys
import pandas as pd
import time

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import json
import os


class Crawler(object):
    def __init__(self, n_processes=1, web_link='https://www.dienmayxanh.com/'):
        super(Crawler, self).__init__()
        self.browser = webdriver.Firefox()
        self.n_processes = n_processes
        self.web_link = web_link
        self.category_links = 'data/category_links.json'
        self.product_links = 'data/product_links.json'
        self.action = ActionChains(self.browser)

    def __get_category_links(self):
        self.browser.get(self.web_link)
        categories = self.browser.find_elements_by_xpath('//*[@id="menu2017"]/li')
        category_links = list()

        for i in range(len(categories)):
            hrefs = self.browser.find_elements_by_xpath(f'/html/body/header/div[2]/div/div[1]/nav/ul/li[{i+1}]/span/a')

            for j in range(len(hrefs)):
                keyword = self.browser.find_element_by_xpath(
                    f'/html/body/header/div[2]/div/div[1]/nav/ul/li[{i+1}]/span/a[{j+1}]')
                category_links.append(keyword.get_attribute('href'))

        with open(self.category_links, 'w') as f:
            json.dump(category_links, f)

        self.browser.close()
        print(f'Found {len(category_links)} category links and save in {self.category_links}')
        return category_links

    def __get_products_link(self, category_link):
        self.browser.get(category_link)
        product_links = list()

        while True:
            self.action.send_keys(Keys.END).perform()
            time.sleep(2)
            self.action.key_down(Keys.SHIFT).send_keys(Keys.SPACE).key_up(Keys.SHIFT).perform()
            time.sleep(2)
            try:
                self.browser.find_element_by_class_name('viewmore').click()
            except selenium.common.exceptions.NoSuchElementException:
                break
            except selenium.common.exceptions.ElementClickInterceptedException:
                break
            time.sleep(4)

        self.action.send_keys(Keys.HOME).perform()
        time.sleep(1)
        products = self.browser.find_elements_by_xpath('//*[@id="product-list"]/div')

        for i in range(len(products)):
            try:
                rate = int(self.browser.find_element_by_xpath(
                    f'//*[@id="product-list"]/div[{i+1}]/div/a[2]/p/span[2]').text.split()[0])
                if rate <= 5:
                    continue
            except selenium.common.exceptions.NoSuchElementException:
                continue

            product = self.browser.find_element_by_xpath(f'//*[@id="product-list"]/div[{i+1}]/div/a[2]')
            product_links.append(product.get_attribute('href'))

        save_path = os.path.join('data', category_link.split('/')[-1] + '.product_links.json')
        with open(save_path, 'w') as f:
            json.dump(product_links, f)

        print(f'Found {len(product_links)} product links and save in {save_path}')
        return product_links

    def __get_data_from_link(self, link):
        self.browser.get(link)
        self.browser.find_element_by_xpath('/html/body/section[1]/div[2]/a').click()
        time.sleep(2)

        # For method 2:
        self.action.send_keys(Keys.SPACE).perform()
        time.sleep(4)
        self.browser.find_element_by_class_name('rtpLnk').click()
        stars = self.browser.find_elements_by_class_name('star-line')
        star_links = dict()
        all_comments = list()
        all_rates = list()

        for rate, star in enumerate(stars):
            if star.get_attribute('onclick') == '':
              continue
            star_links[rate] = star
            # star_links[rate] = star.get_attribute('onclick')[13:-2]

        for rate, star_link in star_links.items():
            # self.browser.get(star_link)
            star_link.click()
            n_pages = 0
            while True:
                time.sleep(3)
                comments = self.browser.find_elements_by_xpath('/html/body/section[1]/div[1]/aside[1]/div[2]/ul/li')
                for i in range(len(comments)):
                    try:
                        comment = self.browser.find_element_by_xpath(
                            f'/html/body/section[1]/div[1]/aside[1]/div[2]/ul/li[{i+1}]/div[2]/p/i')
                        if comment.text == '':
                            continue
                        all_comments.append(comment.text)
                        all_rates.append(5 - rate)

                    except selenium.common.exceptions.NoSuchElementException:
                        continue
                self.action.send_keys(Keys.END).perform()
                time.sleep(3)
                self.action.key_down(Keys.SHIFT).send_keys(Keys.SPACE).key_up(Keys.SHIFT).perform()
                time.sleep(3)
                list_page_button = self.browser.find_elements_by_xpath(
                    '/html/body/section[1]/div[1]/aside[1]/div[2]/div[3]/div/a')
                n_pages += 1
                if n_pages >= len(list_page_button):
                    break
                self.browser.find_element_by_xpath(
                    f'/html/body/section[1]/div[1]/aside[1]/div[2]/div[3]/div/a[{len(list_page_button)}]').click()

                time.sleep(3)
        return all_comments, all_rates

    def crawl(self, get_product_links=False):
        if get_product_links is True:
            if not os.path.isfile(self.category_links):
                self.__get_category_links()
            self.__get_products_link(self.category_links)

        for product_path in os.listdir('data'):
            categories = list()
            comments = list()
            rates = list()

            if product_path.endswith('.product_links.json'):
                with open(os.path.join(os.getcwd(), 'data', product_path), 'r') as f:
                    product_links = json.load(f)
                category = product_path.split('.')[0]
                print('############' + ' '.join(category.split('-')) + '##################################')
                data_save_path = os.path.join(os.getcwd(), 'data', category + '.csv')

                for product_link in product_links:
                    data = self.__get_data_from_link(product_link)
                    comments += data[0]
                    rates += data[1]
                    categories += [category] * len(data[0])

                    df = pd.DataFrame.from_dict(
                        {
                            'category': categories,
                            'comment': comments,
                            'rate': rates
                        }
                    )
                    df.to_csv(data_save_path, columns=['category', 'comment', 'rate'])
                    print(f'Found {len(comments)} comments and save in {data_save_path}')
                    time.sleep(3)


if __name__ == '__main__':
    crawler = Crawler()
    crawler.crawl()
