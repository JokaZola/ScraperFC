from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from IPython.display import clear_output
from ScraperFC.shared_functions import *
import json


class WhoScored():

    def __init__(self):
        options = Options()
        options.headless = True
        options.add_argument("window-size=1400,600")
        proxy = get_proxy()
        options.add_argument('--proxy-server={}'.format(proxy))
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        clear_output()


    def close(self):
        self.driver.close()
        self.driver.quit()


    def get_season_link(self, year, league):
        links = {
            "EPL": "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League",
            "La Liga": "https://www.whoscored.com/Regions/206/Tournaments/4/Spain-LaLiga",
            "Bundesliga": "https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga",
            "Serie A": "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A",
            "Ligue 1": "https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1"
        }
        year_str = "{}/{}".format(year-1, year)
        try:
            self.driver.get(links[league])
        except:
            self.close()
            self.__init__()
            self.driver.get(links[league])
        # Wait for season dropdown to be accessible
        season_dropdown = WebDriverWait(self.driver, timeout=10, ignored_exceptions=['TimeoutException']) \
            .until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#seasons')
            ))
        for el in self.driver.find_elements_by_tag_name("select"):
            if el.get_attribute("id") == "seasons":
                for subel in el.find_elements_by_tag_name("option"):
                    if subel.text == year_str:
                        return "https://www.whoscored.com"+subel.get_attribute("value")
        return -1



    def get_match_links(self, year, league):
        # Go to season page
        season_link = self.get_season_link(year, league)
        if season_link == -1:
            print("Failed to get season link.")
            return -1
        self.driver.get(season_link)
        fixtures_button = WebDriverWait(self.driver, 10) \
            .until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#sub-navigation > ul:nth-child(1) > li:nth-child(2) > a:nth-child(1)")
            ))
        fixtures_button.click()
        # Get button to prev month matches
        links = set()
        done = False
        # prev_month_button = WebDriverWait(self.driver, 10) \
        #     .until(EC.element_to_be_clickable(
        #         (By.CSS_SELECTOR, ".previous")
        #     ))
        while not done:
            # Get match links of curr month
            for el in self.driver.find_elements_by_tag_name("a"):
                if el.get_attribute("class") == "result-1 rc":
                    links.add(el.get_attribute("href"))
                    print('Added link {}'.format(el.get_attribute('href')))
            # Determine if there is a previous month or not
            prev_month_button = self.driver.find_element_by_css_selector('.previous')
            if prev_month_button.get_attribute("title") == "No data for previous month":
                done = True
            else:
                prev_month_button.click()
                print('Previous month button clicked.')
                time.sleep(3)
                clear_output()
                prev_month_button = WebDriverWait(self.driver, 10) \
                    .until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, ".previous")
                    ))
        return list(links)
        # prev_button = None
        # for el in self.driver.find_elements_by_tag_name("a"):
        #     if "previous button ui-state-default" in el.get_attribute("class"):
        #         prev_button = el
        # print(prev_button)
        # if not prev_button:
        #     return -1
        # # Gather the links
        # done = False
        # links = set()
        # while not done:
        #     # Get match links of curr month
        #     for el in self.driver.find_elements_by_tag_name("a"):
        #         if el.get_attribute("class") == "result-1 rc":
        #             links.add(el.get_attribute("href"))
        #             print(el)
        #     # Keep going to previous month, if not data available
        #     if prev_button.get_attribute("title") == "No data for previous month":
        #         done = True
        #     else:
        #         prev_button.click()
        #         time.sleep(2)
        # return list(links)


    def scrape_matches(self, year, league):
        error, valid = check_season(year, league, "WhoScored")
        if not valid:
            print(error)
            return -1
        links = self.get_match_links(year, league)
        if links == -1:
            return -1
        for link in links:
            print(link)
            match_data = self.scrape_match(link)
            return match_data


    def scrape_match(self, link):
        self.driver.get(link)
        scripts = list()
        for el in self.driver.find_elements_by_tag_name("script"):
            scripts.append(el.get_attribute("innerHTML"))
        # match_data_string = scripts[38].split(" = ")[1] \
        #         .replace("matchId", "\"matchId\"") \
        #         .replace("matchCentreData", "\"matchCentreData\"") \
        #         .replace("matchCentreEventTypeJson", "\"matchCentreEventTypeJson\"") \
        #         .replace("formationIdNameMappings", "\"formationIdNameMappings\"") \
        #         .replace(";", "")
        return scripts
