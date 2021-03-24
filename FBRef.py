from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import pandas as pd
import numpy as np
import datetime
from IPython.display import clear_output
from ScraperFC.shared_functions import check_season

class FBRef:
    
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        clear_output()
        
        
    def close(self):
        self.driver.close()
        self.driver.quit()
        
        
    def get_season_link(self, year, league):
        if league == 'EPL':
            url = 'https://fbref.com/en/comps/9/history/Premier-League-Seasons'
            finder = 'Premier-League-Stats'
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
            finder = "Ligue-1-Stats"
        else:
            print('ERROR: League not found. Options are \"EPL\", \"La Liga\"')
            return -1
        self.driver.get(url)
        season = str(year-1)+'-'+str(year)
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
        first_half = '/'.join(url[:7])
        second_half = url[7:][0].split('-')
        second_half = '-'.join(second_half[:4])+'-Score-and-Fixtures'
        url = first_half+'/schedule/'+second_half
        self.driver.get(url)
        # Get links to all of the matches in that season
        if league == 'EPL':
            finder = '-Premier-League'
        elif league == 'La Liga':
            finder = '-La-Liga'
        links = []
        for element in self.driver.find_elements_by_tag_name('a'):
            href = element.get_attribute('href')
            if (href) and ('/matches/' in href) and (finder in href) and (href not in links):
                links.append(href)
        clear_output()
        return links
    
    
    def scrape_league_table(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        df = pd.read_html(url)
        lg_tbl = df[0].copy()
        lg_tbl.drop(columns=["xGD/90"], inplace=True)
        if normalize:
            lg_tbl.iloc[:,3:14] = lg_tbl.iloc[:,3:14].divide(lg_tbl["MP"], axis="rows")
        return df
    
    
    def scrape_standard(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/stats/' + new[-1]
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
        vs[col] = vs[("Performance","Gls")] - vs[("Performance","Ast")]
        col = ("Performance","G+A-PK")
        squad[col] = squad[("Performance","G+A")] - squad[("Performance","PK")]
        vs[col] = vs[("Performance","G+A")] - vs[("Performance","PK")]
        col = ("Expected","xG+xA")
        squad[col] = squad[("Expected","xG")] + squad[("Expected","xA")]
        vs[col] = vs[("Expected","xG")] + vs[("Expected","xA")]
        return squad, vs
        
    
    def scrape_gk(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/keepers/' + new[-1]
        new = new.replace("https","http")
        df = pd.read_html(new)
        squad = df[0].copy()
        vs = df[1].copy()
        squad.drop(columns=[("Performance","GA90")], inplace=True)
        vs.drop(columns=[("Performance","GA90")], inplace=True)
        if normalize:
            keep_cols = [("Performance","Save%"), ("Performance","CS%"), ("Penalty Kicks","Save%")]
            keep = squad[keep_cols]
            squad.iloc[:,6:] = squad.iloc[:,6:].divide(squad[("Playing Time","90s")], axis="rows")
            squad[keep_cols] = keep
            keep = vs[keep_cols]
            vs.iloc[:,6:] = vs.iloc[:,6:].divide(vs[("Playing Time","90s")], axis="rows")
            vs[keep_cols] = keep
        return squad, vs
    
    
    def scrape_adv_gk(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/keepersadv/' + new[-1]
        new = new.replace("https","http")
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
        return squad, vs
    
    
    def scrape_shooting(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/shooting/' + new[-1]
        new = new.replace("https","http")
        df = pd.read_html(new)
        squad = df[0].copy()
        vs = df[1].copy()
        squad.drop(columns=[("Standard","Sh/90"), ("Standard","SoT/90"), ], inplace=True)
        vs.drop(columns=[("Standard","Sh/90"), ("Standard","SoT/90"), ], inplace=True)
        if normalize:
            keep_cols = [("Standard","SoT%"), ("Standard","Dist")]
            keep = squad[keep_cols]
            squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
            squad[keep_cols] = keep
            keep = vs[keep_cols]
            vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
            vs[keep_cols] = keep
        return squad, vs
    
    
    def scrape_passing(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/passing/' + new[-1]
        new = new.replace("https","http")
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
        return squad, vs
    
    
    def scrape_passing_types(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/passing_types/' + new[-1]
        new = new.replace("https","http")
        df = pd.read_html(new)
        squad = df[0].copy()
        vs = df[1].copy()
        if normalize:
            squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
            vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
        return squad, vs
    
    
    def scrape_goal_shot_creation(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/gca/' + new[-1]
        new = new.replace("https","http")
        df = pd.read_html(new)
        squad = df[0].copy()
        vs = df[1].copy()
        squad.drop(columns=[("SCA","SCA90"), ("GCA","GCA90")], inplace=True)
        vs.drop(columns=[("SCA","SCA90"), ("GCA","GCA90")], inplace=True)
        if normalize:
            squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
            vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
        return squad, vs
    
    
    def scrape_defensive(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/defense/' + new[-1]
        new = new.replace("https","http")
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
        return squad, vs
    
    
    def scrape_possession(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/possession/' + new[-1]
        new = new.replace("https","http")
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
        return squad, vs
    
    
    def scrape_playing_time(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/playingtime/' + new[-1]
        new = new.replace("https","http")
        df = pd.read_html(new)
        squad = df[0].copy()
        vs = df[1].copy()
        squad.drop(columns=[("Team Success","+/-90"), ("Team Success (xG)","xG+/-90")], inplace=True)
        vs.drop(columns=[("Team Success","+/-90"), ("Team Success (xG)","xG+/-90")], inplace=True)
        if normalize:
            keep_cols = [("Playing Time","Mn/MP"), ("Playing Time","Min%"),
                         ("Playing Time","90s"), ("Starts","Mn/Start")]
            keep = squad[keep_cols]
            squad.iloc[:,4:] = squad.iloc[:,4:].divide(squad[("Playing Time","MP")], axis="rows")
            squad[keep_cols] = keep
            keep = vs[keep_cols]
            vs.iloc[:,4:] = vs.iloc[:,4:].divide(vs[("Playing Time","MP")], axis="rows")
            vs[keep_cols] = keep
        return squad, vs
    
    
    
    def scrape_misc(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)# go the link to the right season
        new = url.split('/')
        new = '/'.join(new[:-1]) + '/misc/' + new[-1]
        new = new.replace("https","http")
        df = pd.read_html(new)
        squad = df[0].copy()
        vs = df[1].copy()
        if normalize:
            keep_cols = [("Aerial Duels","Won%")]
            keep = squad[keep_cols]
            squad.iloc[:,3:] = squad.iloc[:,3:].divide(squad[("Unnamed: 2_level_0","90s")], axis="rows")
            squad[keep_cols] = keep
            keep = vs[keep_cols]
            vs.iloc[:,3:] = vs.iloc[:,3:].divide(vs[("Unnamed: 2_level_0","90s")], axis="rows")
            vs[keep_cols] = keep
        return squad, vs
    
        
    def scrape_season(self, year, league, normalize=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        url = self.get_season_link(year,league)   
        lg_tbl = self.scrape_league_table(year,league,normalize)
        std_for, std_vs = self.scrape_standard(year,league,normalize)
        gk_for, gk_vs = self.scrape_gk(year,league,normalize)
        adv_gk_for, adv_gk_vs = self.scrape_adv_gk(year,league,normalize)
        shoot_for, shoot_vs = self.scrape_shooting(year,league,normalize)
        pass_for, pass_vs = self.scrape_passing(year,league,normalize)
        pass_type_for, pass_type_vs = self.scrape_passing_types(year,league,normalize)
        gca_for, gca_vs = self.scrape_goal_shot_creation(year,league,normalize)
        def_for, def_vs = self.scrape_defensive(year,league,normalize)
        poss_for, poss_vs = self.scrape_possession(year,league,normalize)
        play_time_for, play_time_vs = self.scrape.scrape_playing_time(year,league,normalize)
        misc_for, misc_vs = self.scrape_misc(year,league,normalize)
        out = {
            "League Table": lg_tbl,
            "Standard": (std_for, std_vs),
            "Goalkeeping": (gk_for, gk_vs),
            "Advanced Goalkeeping": (adv_gk_for, adv_gk_vs),
            "Shooting": (shoot_for, shoot_vs),
            "Passing": (pass_for, pass_vs),
            "Pass Types": (pass_type_for, pass_type_vs),
            "GCA": (gca_for, gca_vs),
            "Defensive": (def_for, def_vs),
            "Possession": (poss_for, poss_vs),
            "Playing Time": (play_time_for, play_time_vs),
            "Misc": (misc_for, misc_vs)
        }
        return out
    
    
    def scrape_match(self, link, league):
        df = pd.read_html(link)
        """
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
        """
        if league == 'EPL':
            spliton = '-Premier-League'
        elif league == 'La Liga':
            spliton = '-La-Liga'
        match = pd.Series()
        date = link.split(spliton)[0].split('-')[-3:]
        date = '-'.join(date)
        date = datetime.datetime.strptime(date,'%B-%d-%Y').date()
        match['Date'] = str(date)
        match['Home Team'] = df[2].columns[0][0]
        match['Away Team'] = df[2].columns[1][0]
        match['Home Goals'] = np.array(df[3][('Performance','Gls')])[-1]
        match['Away Goals'] = np.array(df[10][('Performance','Gls')])[-1]
        match['Home Ast'] = np.array(df[3][('Performance','Ast')])[-1]
        match['Away Ast'] = np.array(df[10][('Performance','Ast')])[-1]
        match['FBRef Home xG'] = np.array(df[3][('Expected','xG')])[-1]
        match['FBRef Away xG'] = np.array(df[10][('Expected','xG')])[-1]
        match['Home npxG'] = np.array(df[3][('Expected','npxG')])[-1]
        match['Away npxG'] = np.array(df[10][('Expected','npxG')])[-1]
        match['FBRef Home xA'] = np.array(df[3][('Expected','xA')])[-1]
        match['FBRef Away xA'] = np.array(df[10][('Expected','xA')])[-1]
        match['Home psxG'] = np.array(df[16][('Shot Stopping','PSxG')])[-1]
        match['Away psxG'] = np.array(df[9][('Shot Stopping','PSxG')])[-1]
        return match
    
    
    def scrape_matches(self, year, league, save=False):
        if not check_season(year,league,'FBRef'):
            return -1
        season = str(year-1)+'-'+str(year)
        links = self.get_match_links(year,league)
        # scrape match data
        cols = ['Date','Home Team','Away Team','Home Goals','Away Goals',
                'Home Ast','Away Ast','FBRef Home xG','FBRef Away xG','Home npxG',
                'Away npxG','FBRef Home xA','FBRef Away xA','Home psxG','Away psxG']
        matches = pd.DataFrame(columns=cols)
        for i,link in enumerate(links):
            print('Scraping match ' + str(i+1) + '/' + str(len(links)) +
                  ' from FBRef in the ' + season + ' ' + league + ' season.')
            link = links[i]
            match = self.scrape_match(link,league)
            matches = matches.append(match, ignore_index=True)
            clear_output()
        # save to CSV if requested by user
        if save:
            if league == 'EPL':
                prefix = 'EPL_'
            elif league == 'La Liga':
                prefix = 'La_Liga_'
            filename = prefix+season+'_FBRef.csv'
            matches.to_csv(path_or_buf=filename, index=False)
            print('Matches dataframe saved to ' + filename)
            return filename
        else:
            return matches
        