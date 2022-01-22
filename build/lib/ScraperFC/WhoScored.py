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
import os


class WhoScored():

    def __init__(self):
        options = Options()
        # whoscored scraper CANNOT be headless
        options.add_argument('window-size=700,600')
        proxy = get_proxy() # Use proxy
        options.add_argument('--proxy-server="http={};https={}"'.format(proxy, proxy))
        prefs = {'profile.managed_default_content_settings.images': 2} # don't load images to make faster
        options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options) # create driver
        clear_output()

        
    ############################################################################
    def close(self):
        self.driver.close()
        self.driver.quit()

        
    ############################################################################
    def get_season_link(self, year, league):
        error, valid = check_season(year, league, 'WhoScored')
        if not valid:
            print(error)
            return -1
        
        links = {
            'EPL': 'https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League',
            'La Liga': 'https://www.whoscored.com/Regions/206/Tournaments/4/Spain-LaLiga',
            'Bundesliga': 'https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga',
            'Serie A': 'https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A',
            'Ligue 1': 'https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1',
            'Argentina Liga Profesional': 'https://www.whoscored.com/Regions/11/Tournaments/68/Argentina-Liga-Profesional',
            'EFL Championship': 'https://www.whoscored.com/Regions/252/Tournaments/7/England-Championship',
            'EFL1': 'https://www.whoscored.com/Regions/252/Tournaments/8/England-League-One',
            'EFL2': 'https://www.whoscored.com/Regions/252/Tournaments/9/England-League-Two',
            # Edd Webster added these leagues (twitter: https://twitter.com/eddwebster)
            'Liga Nos': 'https://www.whoscored.com/Regions/177/Tournaments/21/Portugal-Liga-NOS',
            'Eredivisie': 'https://www.whoscored.com/Regions/155/Tournaments/13/Netherlands-Eredivisie',
            'Russian Premier League': 'https://www.whoscored.com/Regions/182/Tournaments/77/Russia-Premier-League',
            'Brasileirao': 'https://www.whoscored.com/Regions/31/Tournaments/95/Brazil-Brasileir%C3%A3o',
            'MLS': 'https://www.whoscored.com/Regions/233/Tournaments/85/USA-Major-League-Soccer',
            'Super Lig': 'https://www.whoscored.com/Regions/225/Tournaments/17/Turkey-Super-Lig',
            'Jupiler Pro League': 'https://www.whoscored.com/Regions/22/Tournaments/18/Belgium-Jupiler-Pro-League',
            'Bundesliga II': 'https://www.whoscored.com/Regions/81/Tournaments/6/Germany-Bundesliga-II',
            'Champions League': 'https://www.whoscored.com/Regions/250/Tournaments/12/Europe-Champions-League',
            'Europa League': 'https://www.whoscored.com/Regions/250/Tournaments/30/Europe-Europa-League',
            'FA Cup': 'https://www.whoscored.com/Regions/252/Tournaments/29/England-League-Cup',
            'League Cup': 'https://www.whoscored.com/Regions/252/Tournaments/29/England-League-Cup',
            'World Cup': 'https://www.whoscored.com/Regions/247/Tournaments/36/International-FIFA-World-Cup',
            'European Championship': 'https://www.whoscored.com/Regions/247/Tournaments/124/International-European-Championship',
            'AFCON': 'https://www.whoscored.com/Regions/247/Tournaments/104/International-Africa-Cup-of-Nations'
            # End of Edd Webster leagues
        }
        
        if (league=='Argentina Liga Profesional' and year in [2016,2021]) \
                or league in ['Brasileirao','MLS','World Cup','European Championship','AFCON']:
            year_str = str(year)
        else:
            year_str = '{}/{}'.format(year-1, year)
        
        # Repeatedly try to get the league's homepage
        done = False
        while not done:
            try:
                self.driver.get(links[league])
                done = True
            except:
                self.close()
                self.__init__()
                time.sleep(5)
        print('League page status: {}'.format(self.driver.execute_script('return document.readyState')))
        
        # Wait for season dropdown to be accessible, then find the link to the chosen season
        for el in self.driver.find_elements(By.TAG_NAME, 'select'):
            if el.get_attribute('id') == 'seasons':
                for subel in el.find_elements(By.TAG_NAME, 'option'):
                    if subel.text==year_str:
                        return 'https://www.whoscored.com'+subel.get_attribute('value')
        return -1


    ############################################################################
    def get_match_links(self, year, league):
        error, valid = check_season(year, league, 'WhoScored')
        if not valid:
            print(error)
            return -1
       
        # Go to season page
        season_link = self.get_season_link(year, league)
        if season_link == -1:
            print("Failed to get season link.")
            return -1
        
        # Repeatedly try to get to the season's homepage
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
        
        # Gather the links. Make this a set to avoid repeat match links. (e.g. for World Cup)
        links = set()

        # Get the season stages and their URLs
        stage_dropdown_xpath = '//*[@id="stages"]'
        stage_elements = self.driver.find_elements(By.XPATH, '{}/{}'.format(stage_dropdown_xpath, 'option'))
        stage_urls = ['https://www.whoscored.com'+el.get_attribute('value') for el in stage_elements]
        if len(stage_urls) == 0: # if no stages in dropdown, then the current url is the only stage
            stage_urls = [self.driver.current_url, ]

        # Iterate through the stages
        for stage_url in stage_urls:

            # Go to the stage
            self.driver.get(stage_url)
            
            """
            # Go to the fixtures
            fixtures_button = WebDriverWait(
                self.driver, 
                10, 
                ignored_exceptions=[TimeoutException]
            ).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#sub-navigation > ul:nth-child(1) > li:nth-child(2) > a:nth-child(1)")
            ))
            self.driver.execute_script('arguments[0].click()', fixtures_button)
            """
        
            print('{} status: {}'.format(stage_url, 
                                         self.driver.execute_script('return document.readyState')))

            # Gather links for the stage
            done = False
            while not done:
                # Get match links from current month
                time.sleep(5)
                for el in self.driver.find_elements_by_tag_name('a'):
                    if el.get_attribute('class') == 'result-1 rc':
                        links.add(el.get_attribute('href'))
                
                # Determine if there is a previous or not
                prev_week_button = self.driver.find_element(By.CSS_SELECTOR, '.previous')
                if 'No data for previous' in prev_week_button.get_attribute('title'):
                    done = True
                else:
                    self.driver.execute_script('arguments[0].click()', prev_week_button)
                    time.sleep(5)
                    prev_week_button = WebDriverWait(
                        self.driver, 
                        20
                    ).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.previous')))
        
        # Convert the set of links to a dict
        match_data_just_links = dict()
        for link in links:
            match_data_just_links[link] = ''
        
        # Save match data dict to json file
        save_filename = '{}_{}_match_data.json'.format(league, year).replace(' ','_')
        with open(save_filename, 'w') as f:
            f.write(json.dumps(match_data_just_links, indent=2))
        print('Match links saved to {}'.format(save_filename))
        
        return match_data_just_links

    ############################################################################
    def scrape_matches(self, year, league):
        error, valid = check_season(year, league, 'WhoScored')
        if not valid:
            print(error)
            return -1

        # Read match links from file or get them with selenium
        save_filename = '{}_{}_match_data.json'.format(league, year).replace(' ','_')
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
                    print('\n\nError encountered. Saving output and restarting webdriver.')
                    with open(save_filename, 'w') as f:
                        f.write(json.dumps(match_data))
                    self.close()
                    self.__init__()
                    time.sleep(5)
        
        # save output
        with open(save_filename, 'w') as f:
            f.write(json.dumps(match_data))
        return match_data

    ############################################################################
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
