from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os

class EnergyScraper:

    '''
    Overview of this class's purpose

    '''

    def __init__(self, directory=None):
        self.url = 'http://s35695.mini.alsoenergy.com/Dashboard/2a5669735065572f4a42454b772b714d3d'
        if directory:
            self.pref = {'download.default_directory': directory}
        else: 
            self.pref = {'download.default_directory': os.getcwd()}
        EnergyScraper.driver = self.create_driver()
        EnergyScraper.driver.get(self.url)
    
    def create_driver(self):
        driver = chromedriver_autoinstaller.install(cwd=True)
        options = Options() 
        options.add_argument('--headless')
        options.add_experimental_option('prefs', self.pref)
        driver = webdriver.Chrome(driver, 
                                options=options)
        return driver 

    
    def next_page(self):
        '''Clicks button on webpage to move driver to next page'''
        EnergyScraper.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/table/tbody/tr/td[2]/div/div[1]/div/div/nav/ul/li[1]/div/a[2]').click()

    def download(self):
        ''''''
        EnergyScraper.driver.find_element_by_class_name('highcharts-button').click()
        EnergyScraper.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/table/tbody/tr/td[2]/div/div[2]/div[1]/div/div[1]/div/div/div[3]/div/div[2]').click()

    def download_files(self, start_date, end_date):
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        date = pd.to_datetime(EnergyScraper.driver.find_element_by_class_name('highcharts-xaxis-title').text)

        days_to_end = (date - end).days
        days_to_start = (end - start).days

        for _ in range(days_to_end):
            self.next_page()

        for _ in range(days_to_start + 1):
            attempts = 0
            while attempts < 2:
                try:
                    self.download()
                    break
                except:
                    attempts += 1

            self.next_page()
        
    def close_driver(self):
        EnergyScraper.driver.close()