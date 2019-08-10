from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import sys
import time
import socket
import re


class SearchLinks:

    def __init__(self, ip):
        socket.setdefaulttimeout(30)
        self.ua_generator = UserAgent()
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--incognito")
        # UserAgent.chrome will generate random Chrome user-agent
        self.options.add_argument(f'user-agent={self.ua_generator.chrome}')
        self.options.add_argument('--proxy-server=http://' + ip)
        self.driver = webdriver.Chrome('resources/chromedriver', options=self.options)
        self.driver.get('http://patents.google.com/advanced')
        self.prefix = 'https://patents.google.com/patent/'
        self.number_of_results = None
        self.links = []
        self.titles = []

    def search(self, search_terms):
        try:
            # presence_of_element_located doesn't mean it was displayed
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.ID, 'searchInput')))
        except:
            print('Error loading https://patents.google.com/advanced')
            sys.exit()
        time.sleep(3)
        self.driver.find_element_by_id('searchInput').send_keys(search_terms)
        time.sleep(3)
        self.driver.find_element_by_id('searchButton').click()
        time.sleep(3)
        # set Results/page to 100, so we can perform less "Next page"
        try:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.XPATH, '//dropdown-menu[@label="Results / page"]')))
            self.driver.find_element_by_xpath('//dropdown-menu[@label="Results / page"]').click()
            self.driver.find_element_by_xpath('//dropdown-menu[@label="Results / page"]/'
                                              'iron-dropdown/div/div/div/div[4]').click()
        except:
            print('Error selecting 100 results/page')
            sys.exit()

    def check_page_loaded(self):
        try:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((
                    By.XPATH, '//paper-tab/div[@class="tab-content style-scope paper-tab"]')))
        except:
            print('Error loading searching results page')
            sys.exit()

    def search_links(self):
        self.check_page_loaded()
        if not self.number_of_results:
            # \d+ means one or more digits
            self.number_of_results = int(
                re.search('\\b\\d+\\b', self.driver.find_element_by_id('numResultsLabel').text).group())
        link_elements = self.driver.find_elements_by_xpath(
            '//search-result-item//article//h4[@class="metadata style-scope search-result-item"]//'
            'span[@class="bullet-before style-scope search-result-item"]//'
            'span[@class="style-scope search-result-item"]')
        title_elements = self.driver.find_elements_by_xpath(
            '//search-result-item//article//state-modifier//a//h3//span')
        self.links.extend([e.text for e in link_elements if e.text is not ''])
        self.titles.extend([e.text for e in title_elements if e.text is not ''])

    def collect_links(self):
        while True:
            time.sleep(3)
            self.search_links()
            try:
                WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, '//iron-icon[@id="icon"]')))
                next_btn = self.driver.find_elements_by_xpath('//iron-icon[@id="icon"]')[1]
                if next_btn.is_displayed():
                    next_btn.click()
                else:
                    raise ValueError
            except:
                print('Final page reach!')
            break

        return self.links, self.titles
