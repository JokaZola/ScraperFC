from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from IPython.display import clear_output
from ScraperFC.shared_functions import *
import json
import pandas as pd
import os
import traceback


class WhoScored():

    def __init__(self):
        options = Options()
#         options.add_argument('--headless')
        options.add_argument('window-size=700,600')
#         options.add_argument("--log-level=0")
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('disable-infobars')
#         options.add_argument('--disable-extensions')
        # Use proxy
        proxy = get_proxy()
        options.add_argument('--proxy-server="http={};https={}"'.format(proxy, proxy))
        # don't load images
        prefs = {'profile.managed_default_content_settings.images': 2}
        options.add_experimental_option('prefs', prefs)
        # create driver
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        clear_output()


    def close(self):
        self.driver.close()
        self.driver.quit()


    def get_season_link(self, year, league):
        links = {'EPL': 'https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League',
                 'La Liga': 'https://www.whoscored.com/Regions/206/Tournaments/4/Spain-LaLiga',
                 'Bundesliga': 'https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga',
                 'Serie A': 'https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A',
                 'Ligue 1': 'https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1'}
        year_str = '{}/{}'.format(year-1, year)
        done = False
        while not done:
            try:
                self.driver.get(links[league])
                done = True
            except:
                import traceback
                traceback.print_exc()
                return -1
#                 self.close()
#                 self.__init__()
#                 time.sleep(5)
        print('League page status: {}'.format(self.driver.execute_script('return document.readyState')))
        # Wait for season dropdown to be accessible
#         season_dropdown = WebDriverWait(self.driver, 10, ignored_exceptions=['TimeoutException']) \
#             .until(EC.presence_of_element_located((By.ID, 'seasons')))
        for el in self.driver.find_elements_by_tag_name('select'):
            if el.get_attribute('id') == 'seasons':
                for subel in el.find_elements_by_tag_name("option"):
                    if subel.text == year_str:
                        return 'https://www.whoscored.com'+subel.get_attribute('value')
        return -1



    def get_match_links(self, year, league):
        # Go to season page
        season_link = self.get_season_link(year, league)
        if season_link == -1:
            print("Failed to get season link.")
            return -1
        done = False
        while not done:
            try:
                self.driver.get(season_link)
                done = True
            except:
                self.close()
                self.__init__()
                time.sleep(5)
        print('Season page status: {}'.format(self.driver.execute_script('return document.readyState')))
        # Go to the fixtures page
        fixtures_button = WebDriverWait(self.driver, 10, ignored_exceptions=[TimeoutException]) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
                                               "#sub-navigation > ul:nth-child(1) > li:nth-child(2) > a:nth-child(1)")))
        self.driver.execute_script('arguments[0].click()', fixtures_button)
        print('Fixtures page status: {}'.format(self.driver.execute_script('return document.readyState')))
        # Gather links
        links = set()
        done = False
        while not done:
            # Get match links from current month
            time.sleep(5)
            for el in self.driver.find_elements_by_tag_name('a'):
                if el.get_attribute('class') == 'result-1 rc':
                    links.add(el.get_attribute('href'))
            # Determine if there is a previous month or not
            prev_month_button = self.driver.find_element_by_css_selector('.previous')
            if prev_month_button.get_attribute('title') == 'No data for previous month':
                done = True
            else:
                self.driver.execute_script('arguments[0].click()', prev_month_button)
                time.sleep(5)
                prev_month_button = WebDriverWait(self.driver, 10) \
                    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.previous')))
        # set of links to dict
        match_data_just_links = dict()
        for link in links:
            match_data_just_links[link] = ''
        # save match data dict to json file
        save_filename = '{}_{}_match_data.json'.format(league, year)
        if not os.path.exists(save_filename):
            with open(save_filename, 'w') as f:
                f.write(json.dumps(match_data_just_links, indent=2))
                print('Match links saved to {}'.format(save_filename))
        return match_data_just_links


    def scrape_matches(self, year, league):
        error, valid = check_season(year, league, 'WhoScored')
        if not valid:
            print(error)
            return -1
        # Read match links from file or get them with selenium
        save_filename = '{}_{}_match_data.json'.format(league, year)
        if os.path.exists(save_filename):
            with open(save_filename, 'r') as f:
                match_data = json.loads(f.read())
        else:
            match_data = self.get_match_links(year, league)
            if match_data == -1:
                return -1
        # Scrape match data for each link
        i = 0
        for link in match_data:
            i += 1
            try_count = 0
            while match_data[link] == '':
                try_count += 1
                if try_count > 10:
                    print('Failed to scrape match {}/{} from {}'.format(i, len(match_data), link))
                    return -1
                try:
                    print('{}\rScraping match data for match {}/{} in the {}-{} {} season from {}' \
                              .format(' '*500, i, len(match_data), year-1, year, league, link), end='\r')
                    match_data[link] = self.scrape_match(link)
                except:
                    print('Error encountered. Saving output and restarting webdriver.')
                    with open(save_filename, 'w') as f:
                        f.write(json.dumps(match_data))
                    self.close()
                    self.__init__()
                    time.sleep(5)
        # save output
        with open(save_filename, 'w') as f:
            f.write(json.dumps(match_data))
        return match_data


    def scrape_match(self, link):
        self.driver.get(link)
        scripts = list()
        for el in self.driver.find_elements_by_tag_name('script'):
            scripts.append(el.get_attribute('innerHTML'))
        for script in scripts:
            if 'require.config.params["args"]' in script:
                match_data_string = script
        match_data_string = match_data_string.split(' = ')[1] \
                .replace('matchId', '"matchId"') \
                .replace('matchCentreData', '"matchCentreData"') \
                .replace('matchCentreEventTypeJson', '"matchCentreEventTypeJson"') \
                .replace('formationIdNameMappings', '"formationIdNameMappings"') \
                .replace(';', '')
        match_data = json.loads(match_data_string)
        return match_data
