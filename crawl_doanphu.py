from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
import time


class CommentCrawl(object):
    browser: WebDriver
    wait: WebDriverWait

    def open_browser(self):
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, 10)
        try:
            self.browser.implicitly_wait(10)
        except:
            print('The page could not be loaded and the crawl operation could not be started!')

    def get_category_urls(self):
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
                f'/html/body/div[4]/div/div[9]/div[1]/div[2]/div/div/div/div[3]/div[1]/div[{i + 1}]')
            s = s.text
            s = s.split('\n')
            s = s[2:-2]
            s = ' '.join(s)
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
        time.sleep(3)
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

    def crawl_page(self, url):
        time.sleep(5)
        self.browser.get(url)
        self.jump_to_comment()
        texts, stars = self.get_data()

        return texts, stars

    def crawl_agent(self, url):
        self.open_browser()
        self.browser.get(url)
        categories, urls = self.get_category_urls()
        data = dict()

        for i, url in enumerate(urls):
            all_category_feedbacks = []
            self.browser.get(url)

            element_urls = []
            elements = self.browser.find_elements_by_xpath('/html/body/div[3]/div/div[3]/div[1]/div/div[1]/div[2]/div')
            for j in range(len(elements)):
                element_url = self.browser.find_element_by_xpath(
                    f'/html/body/div[3]/div/div[3]/div[1]/div/div[1]/div[2]/div[{j+1}]/div/div/div[1]/div[1]/a')
                element_urls.append(element_url.get_attribute('href'))

            for element_url in element_urls:
                user_feedbacks = self.crawl_page(element_url)
                all_category_feedbacks.extend(user_feedbacks)
                print('Complete one page!')
                time.sleep(30)

            data[categories[i]] = all_category_feedbacks

            print('Complete!')


if __name__ == '__main__':
    crawl_agent = CommentCrawl()
    crawl_agent.crawl_agent('https://www.lazada.vn/?spm=a2o4n.home.header.dhome.22f7e182U11eMP')
    pass