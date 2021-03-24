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
        self.driver.quit()
        
        
    def get_match_links(self, year):
        
        base_url = 'https://understat.com/match/'
        starts = {
            2020: 11643,
            2019: 9197,
            2018: 7119,
            2017: 461,
            2016: 81,
            2015: 4749
        }
        start_id = starts[year]
        links = []
        for id in range(start_id, start_id+380):
            links.append(base_url+str(id))
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
            score = [i for i in element.text if i.isdigit()]
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
        
        
    def scrape_matches(self, year, save=False):
        
        if not check_season(year,'EPL','Understat'):
            return -1
        
        season = str(year-1)+'-'+str(year)
        links = self.get_match_links(year)
        cols = ['Date','Home Team','Away Team','Home Goals','Away Goals',
                'Home Ast','Away Ast','Understat Home xG','Understat Away xG',
                'Understat Home xA','Understat Away xA','Home xPts','Away xPts']
        matches = pd.DataFrame(columns=cols)
        
        for i,link in enumerate(links):
            
            print('Scraping match ' + str(i+1) + '/' + str(len(links)) + ' from Understat in the ' + season + ' season.')
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
            
        