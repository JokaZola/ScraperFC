from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from IPython.display import clear_output
import random
import pandas as pd
import numpy as np


def check_season(year,league,source):
    assert source in ['FBRef','Understat','FiveThirtyEight','All', "SofaScore", "WhoScored"]
    error = None
    
    # make sure year is an int
    if type(year) != int:
        error = "Year needs to be an integer."
        return error, False
    
    # make sure league is a valid string
    if type(league) != str or league not in ["EPL","La Liga","Serie A","Ligue 1","Bundesliga", "USL League One", "MLS"]:
        error = "League needs to be a string. Options are \"EPL\", \"La Liga\", \"Bundesliga\", \"Serie A\", " + \
            "\"Ligue 1\", \"USL League One\", \"MLS\"."
        return error, False
    
    # make sure year is valid for a given source
    yr_valid = True
    if source=='FBRef':
        if league=='EPL' and year<1993:
            error = 'Year invalid for source FBRef, EPL. Must be 1993 or later.'
            yr_valid = False
        elif league=='La Liga' and year<1989:
            error = 'Year invalid for source FBRef, La Liga. Must be 1989 or later.'
            yr_valid=False
        elif league=='Bundesliga' and year<1989:
            error = 'Year invalid for source FBRef, Bundesliga. Must be 1989 or later.'
            yr_valid=False
        elif league=='Serie A' and year<1989:
            error = 'Year invalid for source FBRef, Serie A. Must be 1989 or later.'
            yr_valid=False
        elif league=='Ligue 1' and year<1996:
            error = 'Year invalid for source FBRef, Ligue 1. Must be 1996 or later.'
            yr_valid=False
        elif league=="MLS" and year<1996:
            error = 'Year invalid for source FBRef, MLS. Must be 1996 or later.'
            yr_valid=False

    elif source=='Understat' and year<2015:
        error = 'Year invalid for source Understat. Must be 2015 or later.'
        yr_valid = False

    elif source=='FiveThirtyEight' and year<2017:
        error = 'Year invalid for source FiveThirtyEight. Must be 2017 or later.'
        yr_valid = False

    elif source=="SofaScore":
        if league=="USL League One" and year<2019:
            error = "Year invalid for source SofaScore and league USL League One. Year must be 2019 or later."
            yr_valid = False

    elif source == "WhoScored":
        if league in ["EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1"] and year<2010:
            error = "Year invalid for source WhoScored and league {}. Year must be 2010 or later.".format(league)
            yr_valid = False
    return error, yr_valid


def get_proxy():
    """ Adapted from https://stackoverflow.com/questions/59409418/how-to-rotate-selenium-webrowser-ip-address """
    options = Options()
    options.headless = True
    options.add_argument("window-size=700,600")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    clear_output()
    
    try:
        driver.get("https://sslproxies.org/")
        # on some machines the xpath is "//table[@class='table table-striped table-bordered dataTable']"???
#         table = driver.find_element_by_xpath("//table[@class='table table-striped table-bordered']")
        table = driver.find_elements_by_tag_name('table')[0]
        df = pd.read_html(table.get_attribute('outerHTML'))[0]
        df = df.iloc[np.where(~np.isnan(df['Port']))[0],:] # ignore nans

        ips = df['IP Address'].values
        ports = df['Port'].astype('int').values

        driver.quit()
        proxies = list()
        for i in range(len(ips)):
            proxies.append('{}:{}'.format(ips[i], ports[i]))
        i = random.randint(0, len(proxies)-1)
        return proxies[i]
    except Exception as e:
        driver.close()
        driver.quit()
        raise e
