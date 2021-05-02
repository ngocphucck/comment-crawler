from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException, ElementClickInterceptedException
import pandas as pd
import time


class CommentCrawl(object):
    browser: WebDriver
    wait: WebDriverWait

    def open_browser(self, url):
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, 10)
        try:
            self.browser.implicitly_wait(10)
        except:
            print('The page could not be loaded and the crawl operation could not be started!')

        self.browser.get(url)

    def get_category_urls(self, url):
        self.open_browser(url)
        time.sleep(5)
        self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight/2)')
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_DOWN)
        category_urls = self.browser.find_elements_by_xpath('/html/body/div[5]/div[7]/div[2]/div/div')

        urls = []
        categories = []
        for i in range(len(category_urls)):
            category_url = self.browser.find_element_by_xpath(f'/html/body/div[5]/div[7]/div[2]/div/div[{i+1}]/a')
            urls.append(category_url.get_attribute('href'))
            category_name = self.browser.find_element_by_xpath(f'/html/body/div[5]/div[7]/div[2]/div/div[{i+1}]/a/div[2]/span')
            categories.append(category_name.text)

        time.sleep(5)

        return categories, urls

    def get_data(self):
        texts = []
        stars = []

        comments = self.browser.find_elements_by_xpath(
            '/html/body/div[4]/div/div[9]/div[1]/div[2]/div/div/div/div[3]/div[1]/div')
        for i in range(len(comments)):
            s = self.browser.find_element_by_xpath(
                f'/html/body/div[4]/div/div[9]/div[1]/div[2]/div/div/div/div[3]/div[1]/div[{i + 1}]/div[3]/div[1]')
            s = s.text
            texts.append(s)

            star_symbols = self.browser.find_elements_by_xpath(
                f'/html/body/div[4]/div/div[9]/div[1]/div[2]/div/div/div/div[3]/div[1]/div[{i + 1}]/div[1]/div/img')
            star_srcs = [symbol.get_attribute('src') for symbol in star_symbols]
            stars.append(self.get_star(star_srcs))

        return texts, stars

    def jump_to_comment(self):
        element = self.browser.find_element_by_xpath(
            '//a[@class="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-review-summary__link"]')
        element.click()
        time.sleep(6)
        element = self.browser.find_element_by_xpath('//*')
        element.send_keys(Keys.HOME)
        time.sleep(3)
        element = self.browser.find_element_by_xpath(
            '//a[@class="pdp-link pdp-link_size_s pdp-link_theme_blue pdp-review-summary__link"]')
        element.click()
        time.sleep(2)

    def get_star(self, image_links):
        for i in range(len(image_links)):
            if i == 4 or image_links[i] != image_links[i + 1]:
                return i + 1

    def switch_page(self):
        self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight/2)')
        self.browser.find_element_by_xpath('/html/body/div[3]/div/div[3]/div[1]/div/div[1]/div[3]/div/ul/li[9]/a').click()
        self.fake_action()

    def crawl_page(self, url):
        time.sleep(5)
        self.browser.get(url)
        time.sleep(5)
        self.jump_to_comment()
        texts, stars = self.get_data()

        self.fake_action()
        return texts, stars

    def crawl_agent(self, categories, urls):

        for i, url in enumerate(urls):
            self.open_browser(url)

            all_category_feedbacks = [[], [], []]

            element_urls = []
            for _ in range(50):
                self.fake_action()
                elements = self.browser.find_elements_by_xpath('/html/body/div[3]/div/div[3]/div[1]/div/div[1]/div[2]/div')
                for j in range(len(elements)):
                    element_url = self.browser.find_element_by_xpath(
                        f'/html/body/div[3]/div/div[3]/div[1]/div/div[1]/div[2]/div[{j+1}]/div/div/div[1]/div[1]/a')
                    element_urls.append(element_url.get_attribute('href'))

                if len(element_urls) > 200:
                    break
                self.switch_page()
            time.sleep(5)
            for element_url in element_urls:
                try:
                    feedbacks, stars = self.crawl_page(element_url)

                    all_category_feedbacks[0].extend([categories[i]] * len(stars))
                    all_category_feedbacks[1].extend(feedbacks)
                    all_category_feedbacks[2].extend(stars)

                    data = {'category': all_category_feedbacks[0],
                            'comment': all_category_feedbacks[1],
                            'rate': all_category_feedbacks[2]}
                    df = pd.DataFrame(data, columns=['category', 'comment', 'rate'])
                    df.to_csv(f'{categories[i]}.csv')

                    print(feedbacks)
                    print(stars)
                    print('Complete one page!')

                except ElementNotVisibleException:
                    print('Ignore 1 page')
                    time.sleep(60)
                except ElementClickInterceptedException:
                    print('Ignore 1 page')
                    time.sleep(60)

            self.terminate()
            print('Complete!')

    def terminate(self):
        self.browser.close()

    def fake_action(self):
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_DOWN)
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_DOWN)
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_DOWN)
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_DOWN)
        time.sleep(3)
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_UP)
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_UP)
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_UP)
        self.browser.find_element_by_xpath('//*').send_keys(Keys.ARROW_UP)


if __name__ == '__main__':
    crawl_agent = CommentCrawl()
    crawl_agent.crawl_agent('https://www.lazada.vn/?spm=a2o4n.home.header.dhome.22f7e182U11eMP')
    pass
