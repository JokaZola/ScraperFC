from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import pandas as pd
import numpy as np
import datetime
from IPython.display import clear_output
from zipfile import ZipFile
from shared_functions import check_season

class FiveThirtyEight:
    
    def __init__(self):
        options = Options()
        options.headless = True
        prefs = {"download.default_directory" : os.getcwd()}
        options.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        clear_output()
        
        
    def close(self):
        self.driver.quit()
        
        
    def up_season(self,string):
        integer = int(string)
        up1 = integer + 1
        return str(up1)
        
        
    def scrape_matches(self, year, save=False):
        if not check_season(year,'EPL','FiveThirtyEight'):
            return -1
        
        url = 'https://data.fivethirtyeight.com/#soccer-spi'
        self.driver.get(url)
        
        for element in self.driver.find_elements_by_class_name("download-link"):
            if element.get_attribute("dataset-name") == "soccer-spi":
                element.click()
                
        while not os.path.exists('soccer-spi.zip'):
            pass
        
        with ZipFile('soccer-spi.zip') as zf:
            with zf.open('soccer-spi/spi_matches.csv') as f:
                df = pd.read_csv(f)
        os.remove('soccer-spi.zip')
        
        df = df[df['league'] == 'Barclays Premier League'] # only keep premier league matches
        
        df['season'] = df['season'].apply(self.up_season) # add one to season column
        
        # only keep the season requested
        df = df[df['season']==str(year)]
        
        # only keep some cols
        keep = ['date','team1','team2','score1','score2','xg1','xg2',
                'nsxg1','nsxg2','adj_score1','adj_score2']
        df = df[keep]
        # rename cols
        cols = ['Date','Home Team','Away Team','Home Goals','Away Goals',
                'FTE Home xG','FTE Away xG','Home nsxG','Away nsxG',
                'Home Adj Score','Away Adj Score']
        df.columns = cols
        df = df.reset_index(drop=True)
        
        # save to CSV if requested by user
        if save:
            filename = 'EPL_matches_'+season+'_FiveThirtyEight.csv'
            df.to_csv(path_or_buf=filename, index=False)
            print('Matches dataframe saved to ' + filename)
            return filename
        else:
            return df
        