from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import pandas as pd
import numpy as np
import datetime
from IPython.display import clear_output
import re
from ScraperFC.shared_functions import check_season


class Understat:
    
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        clear_output()
        
        
    def close(self):
        self.driver.close()
        self.driver.quit()
        
        
    def get_match_links(self, year, league):
        if not check_season(year,league,'Understat'):
            return -1
#         base_url = 'https://understat.com/match/'
#         starts = {
#             # EPL
#             ("EPL",2015): 4749,
#             ("EPL",2016): 81,
#             ("EPL",2017): 461,
#             ("EPL",2018): 7119,
#             ("EPL",2019): 9197,
#             ("EPL",2020): 11643,
#             ("EPL",2021): 14086,
#             # La Liga
#             ("La Liga",2015): 5826,
#             ("La Liga",2016): 1399,
#             ("La Liga",2017): 1779,
#             ("La Liga",2018): 7879,
#             ("La Liga",2019): 9957,
#             ("La Liga",2020): 12026,
#             ("La Liga",2021): 14136,
#             # Bundesliga
#             ("Bundesliga",2015): 5447,
#             ("Bundesliga",2016): 1021,
#             ("Bundesliga",2017): 1327,
#             ("Bundesliga",2018): 8259,
#             ("Bundesliga",2019): 10337,
#             ("Bundesliga",2020): 12403,
#             ("Bundesliga",2021): 14173,
#             # Serie A
#             ("Serie A",2015): 5149,
#             ("Serie A",2016): 551,
#             ("Serie A",2017): 931,
#             ("Serie A",2018): 7499,
#             ("Serie A",2019): 9577,
#             ("Serie A",2020): 13089,
#             ("Serie A",2021): 14116,
#             # Ligue 1
#             ("Ligue 1",2015): 6185,
#             ("Ligue 1",2016): 1869,
#             ("Ligue 1",2017): 2249,
#             ("Ligue 1",2018): 8565,
#             ("Ligue 1",2019): 10643,
#             ("Ligue 1",2020): 12709,
#             ("Ligue 1",2021): 13977
#         }
#         start_id = starts[(league,year)]
#         if league in ["EPL","La Liga","Serie A","Ligue 1"]:
#             games_in_season = 380
#         elif league == "Bundesliga":
#             games_in_season = 306
#         links = []
#         for id in range(start_id, start_id+games_in_season):
#             links.append(base_url+str(id))
        base_url = "https://understat.com/"
        lg = league.replace(" ","_")
        url = base_url+"league/"+lg+"/"+str(year-1)
        self.driver.get(url)
        btn = self.driver.find_element_by_class_name("calendar-prev")
        links = []
        for el in self.driver.find_elements_by_class_name("match-info"):
            links.append(el.get_attribute("href"))
        done = False
        while not done:
            btn.click()
            for el in self.driver.find_elements_by_class_name("match-info"):
                href = el.get_attribute("href")
                if href not in links:
                    links.append(href)
                else:
                    done = True
        return links
        
        
    def scrape_match(self, link):
        self.driver.get(link)
        elements = []
        for element in self.driver.find_elements_by_class_name('progress-value'):
            elements.append(element.get_attribute('innerHTML'))

        match = pd.Series()
        for element in self.driver.find_elements_by_class_name('breadcrumb'):
            date = element.find_elements_by_tag_name('li')[2]
            date = date.text
        date = datetime.datetime.strptime(date,'%b %d %Y').date()
        match['Date'] = date
            
        match['Home Team'] = elements[0]
        match['Away Team'] = elements[1]
        
        for element in self.driver.find_elements_by_class_name('block-match-result'):
             score = element.get_attribute("innerHTML")
             score = score.split("</a>")[1]
             score = score.split("<a")[0].strip()
             score = score.split(" - ")
        assert len(score) == 2
        match['Home Goals'] = int(score[0])
        match['Away Goals'] = int(score[1])

        hxg = elements[7]
        axg = elements[8]

        ha = self.driver.find_elements_by_xpath('/html/body/div[1]/div[3]/div[4]/div/div[2]/table/tbody[2]/tr/td[8]')
        ha = int(ha[0].text)
        hxa = self.driver.find_elements_by_xpath('/html/body/div[1]/div[3]/div[4]/div/div[2]/table/tbody[2]/tr/td[10]')
        hxa = hxa[0].text.replace('+','-')
        # click button to away team stats
        button = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[4]/div/div[1]/div/label[2]')
        button.click()
        aa = self.driver.find_elements_by_xpath('/html/body/div[1]/div[3]/div[4]/div/div[2]/table/tbody[2]/tr/td[8]')
        aa = int(aa[0].text)
        axa = self.driver.find_elements_by_xpath('/html/body/div[1]/div[3]/div[4]/div/div[2]/table/tbody[2]/tr/td[10]')
        axa = axa[0].text.replace('+','-')
        
        match['Home Ast'] = ha
        match['Away Ast'] = aa
        match['Understat Home xG'] = float(hxg.split('<')[0] + hxg.split('>')[1].split('<')[0])
        match['Understat Away xG'] = float(axg.split('<')[0] + axg.split('>')[1].split('<')[0])
        match['Understat Home xA'] = float(hxa.split('-')[0])
        match['Understat Away xA'] = float(axa.split('-')[0])

        string = elements[17]
        match['Home xPts'] = float(string.split('<')[0] + string.split('>')[1].split('<')[0])
        string = elements[18]
        match['Away xPts'] = float(string.split('<')[0] + string.split('>')[1].split('<')[0])
        
        return match
        
        
    def scrape_matches(self, year, league, save=False):
        if not check_season(year,'EPL','Understat'):
            return -1
        
        season = str(year-1)+'-'+str(year)
        links = self.get_match_links(year, league)
        cols = ['Date','Home Team','Away Team','Home Goals','Away Goals',
                'Home Ast','Away Ast','Understat Home xG','Understat Away xG',
                'Understat Home xA','Understat Away xA','Home xPts','Away xPts']
        matches = pd.DataFrame(columns=cols)
        
        for i,link in enumerate(links):
            print('Scraping match ' + str(i+1) + '/' + str(len(links)) + ' from Understat in the ' + season + ' season.')
            print(link)
            match = self.scrape_match(link)
            matches = matches.append(match, ignore_index=True)
            clear_output()
        
        # save to CSV if requested by user
        if save:
            filename = 'EPL_matches_'+season+'_Understat.csv'
            matches.to_csv(path_or_buf=filename, index=False)
            print('Matches dataframe saved to ' + filename)
            return filename
        else:
            return matches
            
        