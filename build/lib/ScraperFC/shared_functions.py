from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from IPython.display import clear_output
import random


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
    return error, yr_valid


def get_proxy():
    options = Options()
    options.headless = True
    options.add_argument("window-size=1400,600")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    clear_output()

    driver.get("https://sslproxies.org/")
    driver.execute_script(
        "return arguments[0].scrollIntoView(true);", 
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//table[@class='table table-striped table-bordered dataTable']//th[contains(., 'IP Address')]"
            ))
        )
    )
    ips = list()
    ips = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered dataTable']//tbody//tr[@role='row']/td[position() = 1]")))]
    ports = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered dataTable']//tbody//tr[@role='row']/td[position() = 2]")))]
    driver.quit()
    proxies = list()
    for i in range(len(ips)):
        proxies.append('{}:{}'.format(ips[i], ports[i]))
    i = random.randint(0, len(proxies))
    return proxies[i]
