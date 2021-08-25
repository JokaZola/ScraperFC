import datetime
from   IPython.display import clear_output
import numpy as np
import pandas as pd
from   ScraperFC.shared_functions import check_season
from   selenium import webdriver
from   selenium.webdriver.chrome.options import Options
from   webdriver_manager.chrome import ChromeDriverManager

class FBRef:
    
    def __init__(self):
        options = Options()
        options.headless = True
        options.add_argument("window-size=1400,600")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        clear_output()
      
        
    def close(self):
        self.driver.close()
        self.driver.quit()

    
    def get_season_link(self, year, league):
        if league == 'EPL':
            url = 'https://fbref.com/en/comps/9/history/Premier-League-Seasons'
            if year >= 2008:
                finder = 'Premier-League-Stats'
            else:
                finder = 'Premiership-Stats'

        elif league == 'La Liga':
            url = 'https://fbref.com/en/comps/12/history/La-Liga-Seasons'
            finder = 'La-Liga-Stats'

        elif league == "Bundesliga":
            url = "https://fbref.com/en/comps/20/history/Bundesliga-Seasons"
            finder = "Bundesliga-Stats"

        elif league == "Serie A":
            url = "https://fbref.com/en/comps/11/history/Serie-A-Seasons"
            finder = "Serie-A-Stats"

        elif league == "Ligue 1":
            url = "https://fbref.com/en/comps/13/history/Ligue-1-Seasons"
            if year >= 2003:
                finder = 'Ligue-1'
            else:
                finder = 'Division-1'

        elif league == "MLS":
            url = "https://fbref.com/en/comps/22/history/Major-League-Soccer-Seasons"
            finder = "Major-League-Soccer-Stats"
        
        else:
            print('ERROR: League not found. Options are \"EPL\", \"La Liga\", '+
                  '\"Bundesliga\", \"Serie A\", \"Ligue 1\"')
            return -1
        self.driver.get(url)
        if league != "MLS":
            season = str(year-1)+'-'+str(year)
        else:
            season = str(year)
        for element in self.driver.find_elements_by_link_text(season):
            if finder in element.get_attribute('href'):
                return element.get_attribute('href')
            else:
                print('ERROR: Season not found.')
                return -1
    

    def get_match_links(self, year, league):
        print('Gathering match links.')
        url = self.get_season_link(year, league)
        
        # go to the scores and fixtures page
        url = url.split('/')
        first_half = '/'.join(url[:-1])
        second_half = url[-1].split('-')
        second_half = '-'.join(second_half[:-1])+'-Score-and-Fixtures'
        url = first_half+'/schedule/'+second_half
        self.driver.get(url)
        
        # Get links to all of the matches in that season
        if league == 'EPL':
            if year >= 2008:
                finder = '-Premier-League'
            else:
                finder = '-Premiership'
        elif league == 'La Liga':
            finder = '-La-Liga'
        elif league == 'Bundesliga':
            finder = '-Bundesliga'
        elif league == 'Serie A':
            finder = '-Serie-A'
        elif league == 'Ligue 1':
            if year >= 2003:
                finder = '-Ligue-1'
            else:
                finder = '-Division-1'
        elif league == "MLS":
            finder = "-Major-League-Soccer"
        else:
            print('ERROR: League not found. Options are \"EPL\", \"La Liga\", '+
                  '\"Bundesliga\", \"Serie A\", \"Ligue 1\", \"MLS\".')
            return -1
        
        links = set()
        # only get match links from the fixtures table
        for table in self.driver.find_elements_by_tag_name('table'):
            if table.get_attribute('id')!='' and table.get_attribute('class')!='':
                # find the match links
                for element in table.find_elements_by_tag_name('a'):
                    href = element.get_attribute('href')
                    if (href) and ('/matches/' in href) and (href.endswith(finder)):
                        links.add(href)
        clear_output()
        
        return list(links)
    

    def add_team_ids(self, df, insert_index, url, tag_name):
        self.driver.get(url)
        team_ids = list()
        for el in self.driver.find_elements_by_xpath('//{}[@data-stat="squad"]'.format(tag_name)):
            if el.text != '' and el.text != 'Squad':
                team_id = el.find_element_by_tag_name('a') \
                    .get_attribute('href') \
                    .split('/squads/')[-1] \
                    .split('/')[0]
                team_ids.append(team_id)
        df.insert(insert_index, 'team_id', team_ids)
        return df

    
    def add_player_ids(self, df, url):
        self.driver.get(url)
        player_ids = list()
        for el in self.driver.find_elements_by_xpath('//td[@data-stat="player"]'):
            if el.text != '' and el.text != 'Player':
                team_id = el.find_element_by_tag_name('a') \
                    .get_attribute('href') \
                    .split('/players/')[-1] \
                    .split('/')[0]
                player_ids.append(team_id)
        df.insert(2, 'player_id', player_ids)
        return df


    def scrape_league_table(self, year, league, normalize=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        df = pd.read_html(url)
        lg_tbl = df[0].copy()
        #### Drop columns and normalize
        if year >= 2018:
            lg_tbl.drop(columns=["xGD/90"], inplace=True)
        if normalize and year >= 2018:
            lg_tbl.iloc[:,3:13] = lg_tbl.iloc[:,3:13].divide(lg_tbl["MP"], axis="rows")
        elif normalize and year < 2018:
            lg_tbl.iloc[:,3:10] = lg_tbl.iloc[:,3:10].divide(lg_tbl["MP"], axis="rows")
        #### Scrape western conference if MLS
        if league == "MLS":
            west_tbl = df[2].copy()
            if year >= 2018:
                west_tbl.drop(columns=["xGD/90"], inplace=True)
            if normalize and year >= 2018:
                west_tbl.iloc[:,3:13] = west_tbl.iloc[:,3:13].divide(west_tbl["MP"], axis="rows")
            elif normalize and year < 2018:
                west_tbl.iloc[:,3:10] = west_tbl.iloc[:,3:10].divide(west_tbl["MP"], axis="rows")
            return (lg_tbl, west_tbl)
        lg_tbl = self.add_team_ids(lg_tbl, 2, url, 'td') # Get team IDs
        return lg_tbl
    

    def scrape_standard(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/stats/' + new[-1]
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_standard_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_standard").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(columns="Per 90 Minutes", level=0, inplace=True)
            df.drop(columns="Matches", level=1, inplace=True)
            # convert some column types from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            # add some calculated columns
            df[("Performance","G+A")] = df[("Performance","Gls")] - df[("Performance","Ast")]
            df[("Performance","G+A-PK")] = df[("Performance","G+A")] - df[("Performance","PK")]
            if year >= 2018:
                df[("Expected","xG+xA")] = df[("Expected","xG")] + df[("Expected","xA")]
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            drop_cols = squad.xs("Per 90 Minutes", axis=1, level=0, drop_level=False).columns
            squad.drop(columns=drop_cols, inplace=True)
            vs.drop(columns=drop_cols, inplace=True)
            if normalize:
                squad.iloc[:,8:] = squad.iloc[:,8:].divide(squad[("Playing Time","90s")], axis="rows")
                vs.iloc[:,8:] = vs.iloc[:,8:].divide(vs[("Playing Time","90s")], axis="rows")
            col = ("Performance","G+A")
            squad[col] = squad[("Performance","Gls")] - squad[("Performance","Ast")]
            vs[col] = vs[("Performance","Gls")] + vs[("Performance","Ast")]
            col = ("Performance","G+A-PK")
            squad[col] = squad[("Performance","G+A")] - squad[("Performance","PK")]
            vs[col] = vs[("Performance","G+A")] - vs[("Performance","PK")]
            if year >= 2018:
                col = ("Expected","xG+xA")
                squad[col] = squad[("Expected","xG")] + squad[("Expected","xA")]
                vs[col] = vs[("Expected","xG")] + vs[("Expected","xA")]
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_gk(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        elif league in['La Liga','Bundesliga','Ligue 1'] and year<2000:
            print('Goalkeeping stats not available from',league,'before 1999/2000 season.')
            return -1
        elif league=='Serie A' and year<1999:
            print('Goalkeeping stats not available from Serie A before 1998/99 season.')
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/keepers/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_keeper_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_keeper").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(columns=("Performance","GA90"), inplace=True)
            df.drop(columns="Matches", level=1, inplace=True)
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            squad.drop(columns=("Performance","GA90"), inplace=True)
            vs.drop(columns=("Performance","GA90"), inplace=True)
            if normalize:
                keep_cols = [("Performance","Save%"), ("Performance","CS%"), ("Penalty Kicks","Save%")]
                keep = squad[keep_cols]
                squad.iloc[:,6:] = squad.iloc[:,6:].divide(squad[("Playing Time","90s")], axis="rows")
                squad[keep_cols] = keep
                keep = vs[keep_cols]
                vs.iloc[:,6:] = vs.iloc[:,6:].divide(vs[("Playing Time","90s")], axis="rows")
                vs[keep_cols] = keep
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_adv_gk(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        elif year < 2018:
            print("Advanced goalkeeping stats not available from before the 2017/18 season.")
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/keepersadv/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_keeper_adv_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_keeper_adv").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(columns=["Matches", "#OPA/90", "/90"], level=1, inplace=True)
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            squad.drop(columns=[("Expected","/90"), ("Sweeper","#OPA/90")], inplace=True)
            vs.drop(columns=[("Expected","/90"), ("Sweeper","#OPA/90")], inplace=True)
            if normalize:
                keep_cols = [("Launched","Cmp%"),
                             ("Passes","Launch%"), ("Passes","AvgLen"),
                             ("Goal Kicks","Launch%"), ("Goal Kicks", "AvgLen"), 
                             ("Crosses","Stp%"), ("Sweeper","AvgDist")]
                keep = squad[keep_cols]
                squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
                squad[keep_cols] = keep
                keep = vs[keep_cols]
                vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
                vs[keep_cols] = keep
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_shooting(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/shooting/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_shooting_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_shooting").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(columns=[("Standard","Sh/90"),("Standard","SoT/90")], inplace=True)
            df.drop(columns="Matches", level=1, inplace=True)
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            squad.drop(
                columns=[("Standard","Sh/90"), ("Standard","SoT/90")], 
                inplace=True
            )
            vs.drop(
                columns=[("Standard","Sh/90"), ("Standard","SoT/90")], 
                inplace=True
            )
            if normalize:
                keep_cols = [("Standard","SoT%"), ("Standard","Dist")]
                keep = squad[keep_cols]
                squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
                squad[keep_cols] = keep
                keep = vs[keep_cols]
                vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
                vs[keep_cols] = keep
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_passing(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        elif year < 2018:
            print("Passing stats not available from before the 2017/18 season.")
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/passing/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_passing_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_passing").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(
                columns=[("Unnamed: 30_level_0","Matches")],
                inplace=True
            )
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            if normalize:
                keep_cols = [("Total","Cmp%"), ("Short","Cmp%"), ("Medium","Cmp%"), ("Long","Cmp%")]
                keep = squad[keep_cols]
                squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
                squad[keep_cols] = keep
                keep = vs[keep_cols]
                vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
                vs[keep_cols] = keep
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_passing_types(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        elif year < 2018:
            print("Passing type stats not available from before the 2017/18 season.")
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/passing_types/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_passing_types_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_passing_types").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(
                columns=[("Unnamed: 33_level_0","Matches")],
                inplace=True
            )
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            if normalize:
                squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
                vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_goal_shot_creation(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        elif year < 2018:
            print("Goal and shot creation stats not available from before the 2017/18 season.")
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/gca/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_gca_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_gca").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            # df.drop(columns=[("SCA","SCA90"), ("GCA","GCA90")], inplace=True)
            df.drop(columns=["SCA90", "GCA90", "Matches"], level=1, inplace=True)
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            squad.drop(columns=[("SCA","SCA90"), ("GCA","GCA90")], inplace=True)
            vs.drop(columns=[("SCA","SCA90"), ("GCA","GCA90")], inplace=True)
            if normalize:
                squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
                vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_defensive(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        elif year < 2018:
            print("Defensive stats not available from before the 2017/18 season.")
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/defense/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_defense_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_defense").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(
                columns=[("Unnamed: 31_level_0","Matches")],
                inplace=True
            )
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            if normalize:
                keep_cols = [("Vs Dribbles","Tkl%"), ("Pressures","%")]
                keep = squad[keep_cols]
                squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
                squad[keep_cols] = keep
                keep = vs[keep_cols]
                vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
                vs[keep_cols] = keep
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_possession(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        elif year < 2018:
            print("Possession stats not available from before the 2017/18 season.")
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/possession/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_possession_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_possession").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(
                columns=[("Unnamed: 32_level_0","Matches")],
                inplace=True
            )
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            if normalize:
                keep_cols = [("Dribbles","Succ%"),("Receiving","Rec%")]
                keep = squad[keep_cols]
                squad.iloc[:,4:] = squad.iloc[:,4:].divide(squad[("Unnamed: 3_level_0","90s")], axis="rows")
                squad[keep_cols] = keep
                keep = vs[keep_cols]
                vs.iloc[:,4:] = vs.iloc[:,4:].divide(vs[("Unnamed: 3_level_0","90s")], axis="rows")
                vs[keep_cols] = keep
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_playing_time(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/playingtime/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_playing_time_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_playing_time").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(columns=("Team Success","+/-90"), inplace=True)
            df.drop(columns="Matches", level=1, inplace=True)
            if year >= 2018:
                df.drop(columns="xG+/-90", level=1, inplace=True)
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            squad.drop(columns=("Team Success","+/-90"), inplace=True)
            vs.drop(columns=("Team Success","+/-90"), inplace=True)
            if year >= 2018:
                squad.drop(columns=("Team Success (xG)","xG+/-90"), inplace=True)
                vs.drop(columns=("Team Success (xG)","xG+/-90"), inplace=True)
            if normalize:
                keep_cols = [("Playing Time","Mn/MP"), ("Playing Time","Min%"),
                             ("Playing Time","90s"), ("Starts","Mn/Start")]
                keep = squad[keep_cols]
                squad.iloc[:,4:] = squad.iloc[:,4:].divide(squad[("Playing Time","MP")], axis="rows")
                squad[keep_cols] = keep
                keep = vs[keep_cols]
                vs.iloc[:,4:] = vs.iloc[:,4:].divide(vs[("Playing Time","MP")], axis="rows")
                vs[keep_cols] = keep
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
    

    def scrape_misc(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/misc/' + new[-1]
        new = new.replace("https","http")
        if player:
            self.driver.get(new)
            if normalize:
                button = self.driver.find_element_by_xpath("//*[@id=\"stats_misc_per_match_toggle\"]")
                self.driver.execute_script("arguments[0].click()",button)
            # get html and scrape table
            html = self.driver.find_element_by_id("stats_misc").get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # drop duplicate header rows and link to match logs
            df = df[df[("Unnamed: 0_level_0","Rk")]!="Rk"].reset_index(drop=True)
            df.drop(columns="Matches", level=1, inplace=True)
            # convert type from str to float
            for col in list(df.columns.get_level_values(0)):
                if 'Unnamed' not in col:
                    df[col] = df[col].astype("float")
            df = self.add_player_ids(df, new) # get player IDs
            return df
        else:
            df = pd.read_html(new)
            squad = df[0].copy()
            vs = df[1].copy()
            if normalize:
                if year >= 2018:
                    keep_cols = [("Aerial Duels","Won%")]
                    keep = squad[keep_cols]
                    squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
                    squad[keep_cols] = keep
                    keep = vs[keep_cols]
                    vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
                    vs[keep_cols] = keep
                else:
                    squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
                    vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
            # Get team IDs
            squad = self.add_team_ids(squad, 1, new, 'th') 
            vs = self.add_team_ids(vs, 1, new, 'th')
            return squad, vs
        

    def scrape_season(self, year, league, normalize=False, player=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        if year >= 2018:
            out = {
                "League Table":         self.scrape_league_table(year,league,normalize),
                "Standard":             self.scrape_standard(year,league,normalize,player),
                "Goalkeeping":          self.scrape_gk(year,league,normalize,player),
                "Advanced Goalkeeping": self.scrape_adv_gk(year,league,normalize,player),
                "Shooting":             self.scrape_shooting(year,league,normalize,player),
                "Passing":              self.scrape_passing(year,league,normalize,player),
                "Pass Types":           self.scrape_passing_types(year,league,normalize,player),
                "GCA":                  self.scrape_goal_shot_creation(year,league,normalize,player),
                "Defensive":            self.scrape_defensive(year,league,normalize,player),
                "Possession":           self.scrape_possession(year,league,normalize,player),
                "Playing Time":         self.scrape_playing_time(year,league,normalize,player),
                "Misc":                 self.scrape_misc(year,league,normalize,player)
            }
        else:
            out = {
                "League Table":         self.scrape_league_table(year,league,normalize),
                "Standard":             self.scrape_standard(year,league,normalize,player),
                "Goalkeeping":          self.scrape_gk(year,league,normalize,player),
                "Shooting":             self.scrape_shooting(year,league,normalize,player),
                "Playing Time":         self.scrape_playing_time(year,league,normalize,player),
                "Misc":                 self.scrape_misc(year,league,normalize,player)
            }
        return out


    def scrape_matches(self, year, league, save=False):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        season = str(year-1)+'-'+str(year)
        links = self.get_match_links(year,league)
        failures = []
        
        # initialize df
        if year >= 2018:
            cols = ['Date','Home Team','Away Team','Home Goals','Away Goals',
                    'Home Ast','Away Ast','FBRef Home xG','FBRef Away xG','FBRef Home npxG',
                    'FBRef Away npxG','FBRef Home xA','FBRef Away xA','FBRef Home psxG',
                    'FBRef Away psxG', 'Home Player Stats', 'Away Player Stats']
        else:
            cols = ['Date','Home Team','Away Team','Home Goals','Away Goals']
        matches = pd.DataFrame(columns=cols)
        
        # scrape match data
        for i,link in enumerate(links):
            print('Scraping match ' + str(i+1) + '/' + str(len(links)) +
                  ' from FBRef in the ' + season + ' ' + league + ' season.')
            
            try:
                match = self.scrape_match(link, year, league)
                matches = matches.append(match, ignore_index=True)
            except Exception as e:
                failures.append([link, e])
            clear_output()
            
        # sort df by match date
        matches = matches.sort_values(by='Date').reset_index(drop=True)
            
        # Print out the failed scrapes
        if len(failures) > 0:
            print('Unable to scrape match data from')
            for failure in failures:
                print(failure, '\n')
        
        # save to CSV if requested by user
        if save:
            filename = '{}_{}_FBRef_matches.csv'.format(season, league.replace(' ','_'))
            matches.to_csv(path_or_buf=filename, index=False)
            print('Matches dataframe saved to ' + filename)
            return filename
        else:
            return matches
        
        
    def scrape_match(self, link, year, league):
        err, valid = check_season(year,league,'FBRef')
        if not valid:
            print(err)
            return -1
        df = pd.read_html(link)
        
        """
        Earlier than 2017/18 tables
        0) home lineup
        1) away lineup
        2) team stats (possession, pass acc, sot, saves)
        3) home sumary
        4) home gk
        5) away summary
        6) away gk
        
        2017/18 or later tables
        read_html returns 17 dataframes for each match link
        0) home lineup
        1) away lineup
        2) team stats (possession, pass acc, sot, saves)
        3) home summary
        4) home passing
        5) home pass types
        6) home def actions
        7) home possession
        8) home misc
        9) home gk
        10) away summary
        11) away passing
        12) away pass types
        13) away def actions
        14) away possession
        15) away misc
        16) away gk
        17) list of shots - both teams
        18) list of shots - home team
        19) list of shots - away team
        """
        
        if league == 'EPL':
            if year >= 2008:
                spliton = '-Premier-League'
            else:
                spliton = '-Premiership'
        elif league == 'La Liga':
            spliton = '-La-Liga'
        elif league == 'Bundesliga':
            spliton = '-Bundesliga'
        elif league == 'Serie A':
            spliton = '-Serie-A'
        elif league == 'Ligue 1':
            if year >= 2003:
                spliton = '-Ligue-1'
            else:
                spliton = '-Division-1'
        
        # Get date of the match
        try:
            # Try this first. Assumes league name is one word
            date_elements = link.split("/")[-1].split("-")[-4:-1]
            date = '-'.join(date_elements)
            date = datetime.datetime.strptime(date,'%B-%d-%Y').date()
        except:
            # Assumes league name is two words
            date_elements = link.split("/")[-1].split("-")[-5:-2]
            date = '-'.join(date_elements)
            date = datetime.datetime.strptime(date,'%B-%d-%Y').date()
        
        match = pd.Series()
        match['Date'] = str(date)
        match['Home Team'] = df[2].columns[0][0]
        match['Away Team'] = df[2].columns[1][0]
        match["Home Formation"] = df[0].columns[0].split("(")[-1].split(")")[0]
        match["Away Formation"] = df[1].columns[0].split("(")[-1].split(")")[0]
        
        if year >= 2018:
            match['Home Goals'] = np.array(df[3][('Performance','Gls')])[-1]
            match['Away Goals'] = np.array(df[10][('Performance','Gls')])[-1]
            match['Home Ast'] = np.array(df[3][('Performance','Ast')])[-1]
            match['Away Ast'] = np.array(df[10][('Performance','Ast')])[-1]
            
            match['FBRef Home xG'] = np.array(df[3][('Expected','xG')])[-1]
            match['FBRef Away xG'] = np.array(df[10][('Expected','xG')])[-1]
            match['FBRef Home npxG'] = np.array(df[3][('Expected','npxG')])[-1]
            match['FBRef Away npxG'] = np.array(df[10][('Expected','npxG')])[-1]
            match['FBRef Home xA'] = np.array(df[3][('Expected','xA')])[-1]
            match['FBRef Away xA'] = np.array(df[10][('Expected','xA')])[-1]
            match['FBRef Home psxG'] = np.array(df[16][('Shot Stopping','PSxG')])[-1]
            match['FBRef Away psxG'] = np.array(df[9][('Shot Stopping','PSxG')])[-1]
            
            match["Home Player Stats"] = pd.Series(
                {
                    "Team Sheet": df[0],
                    "Summary": df[3],
                    "Passing": df[4],
                    "Pass Types": df[5],
                    "Defensive": df[6],
                    "Possession": df[7],
                    "Misc": df[8],
                    "GK": df[9]
                }
            )
            match["Away Player Stats"] = pd.Series(
                {
                    "Team Sheet": df[1],
                    "Summary": df[10],
                    "Passing": df[11],
                    "Pass Types": df[12],
                    "Defensive": df[13],
                    "Possession": df[14],
                    "Misc": df[15],
                    "GK": df[16]
                }
            )      
        else:
            match['Home Goals'] = np.array(df[3][('Performance','Gls')])[-1]
            match['Away Goals'] = np.array(df[5][('Performance','Gls')])[-1]
            match['Home Ast'] = np.array(df[3][('Performance','Ast')])[-1]
            match['Away Ast'] = np.array(df[5][('Performance','Ast')])[-1]
            
        return match 
        