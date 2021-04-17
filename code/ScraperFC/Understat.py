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

import time


class Understat:
    
    def __init__(self):
        options = Options()
        options.headless = True
        options.add_argument("window-size=1400,600")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        clear_output()
        
        
    def close(self):
        self.driver.close()
        self.driver.quit()
        
        
    def get_match_links(self, year, league):
        if not check_season(year,league,'Understat'):
            return -1
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
    
    
    def remove_diff(self, string):
        string = string.split("-")[0]
        return float(string.split("+")[0])
        
        
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
                'Understat Home xA','Understat Away xA','Understat Home xPts','Understat Away xPts']
        matches = pd.DataFrame(columns=cols)
        
        for i,link in enumerate(links):
            print('Scraping match ' + str(i+1) + '/' + str(len(links)) + ' from Understat in the ' + season + ' season.')
#             print(link)
            match = self.scrape_match(link)
            matches = matches.append(match, ignore_index=True)
            clear_output()
        
        # save to CSV if requested by user
        if save:
            filename = season+"_"+league+"_Understat_matches.csv"
            matches.to_csv(path_or_buf=filename, index=False)
            print('Matches dataframe saved to ' + filename)
            return filename
        else:
            return matches
        
        
    def scrape_league_table(self, year, league, normalize=False):
        if not check_season(year,league,'Understat'):
            return -1
        
        base_url = "https://understat.com/"
        lg = league.replace(" ","_")
        url = base_url+"league/"+lg+"/"+str(year-1)
        self.driver.get(url)

        time.sleep(1)
        self.driver.find_elements_by_class_name("options-button")[0].click()
        time.sleep(1)
        # npxG
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]"+
                                     "/div/div[2]/div/div[2]/div[2]/"+
                                     "div/div[11]/div[2]/label").click()
        time.sleep(1)
        # npxGA
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]"+
                                     "/div/div[2]/div/div[2]/div[2]/"+
                                     "div/div[13]/div[2]/label").click()
        time.sleep(1)
        # npxGD
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]"+
                                     "/div/div[2]/div/div[2]/div[2]/"+
                                     "div/div[14]/div[2]/label").click()
        time.sleep(1)
        # PPDA
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]"+
                                     "/div/div[2]/div/div[2]/div[2]/"+
                                     "div/div[15]/div[2]/label").click()
        time.sleep(1)
        # OPPDA
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]"+
                                     "/div/div[2]/div/div[2]/div[2]"+
                                     "/div/div[16]/div[2]/label").click()
        time.sleep(1)
        # DC
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]"+
                                     "/div/div[2]/div/div[2]/div[2]"+
                                     "/div/div[17]/div[2]/label").click()
        time.sleep(1)
        # ODC
        self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]"+
                                     "/div/div[2]/div/div[2]/div[2]"+
                                     "/div/div[18]/div[2]/label").click()
        time.sleep(1)

        self.driver.find_elements_by_class_name("button-apply")[0].click() # apply button
        time.sleep(1)

        # parse df out of HTML
        table = self.driver.find_elements_by_tag_name("table")[0].get_attribute("innerHTML")
        table = "<table>\n"+table+"</table>"
        df = pd.read_html(table)[0]
        df.drop(columns='№', inplace=True)
        
        # remove performance differential text from some columns
        for i in range(df.shape[0]):
            df.loc[i,"xG"] = self.remove_diff(df.loc[i,"xG"])
            df.loc[i,"xGA"] = self.remove_diff(df.loc[i,"xGA"])
            df.loc[i,"xPTS"] = self.remove_diff(df.loc[i,"xPTS"])
            
        if normalize:
            df.iloc[:,2:] = df.iloc[:,2:].divide(df["M"], axis="rows")
        
        return df
            
        