
# Welcome
This is ScraperFC, a Python package that I hope will give more people access to soccer stats. It's still very much a work in progress and I'm currently a full-time grad student so progress may be slow. I am trying to chip away at it though, so please, reach out with any problems you encounter or features you want to see added!

# Installing
ScraperFC can be installed by running "pip install ScraperFC" from the command line.

# Sources
ScraperFC can scrape data from the following websites (all data is open-source and I am not affiliated with any of the sources):
* [FBRef](#FBRef) ([website](https://fbref.com/en/))
	* Match data
		* [scrape_match](#scrape_match)
		* [scrape_matches](#scrape_matches)
	* Squad seasonal stats
		* [scrape_league_table](#scrape_league_table)
		* [scrape_standard](#scrape_standard)
		* [scrape_gk](#scrape_gk)
		* [scrape_adv_gk](#scrape_adv_gk)
		* [scrape_shooting](#scrape_shooting)
		* [scrape_passing](#scrape_passing)
		* [scrape_passing_types](#scrape_passing_types)
		* [scrape_goal_shot_creation](#scrape_goal_shot_creation)
		* [scrape_defensive](#scrape_defensive)
		* [scrape_possession](#scrape_possession)
		* [scrape_playing_time](#scrape_playing_time)
		* [scrape_misc](#scrape_misc)
		* [scrape_season](#scrape_season)
* [Understat](#Understat) ([website](https://understat.com/))
	* Match data
		* scrape_match
		* scrape_matches
* [FiveThirtyEight](#FiveThirtyEight) ([website](https://projects.fivethirtyeight.com/soccer-predictions/))
* [Combined](#Combined)

# FBRef
Data from individual matches, entire seasons of matches, or seasonal squad data can be scraped from FBRef. To use the FBRef module, run 
```
import ScraperFC as sfc
scraper = sfc.FBRef()
# call function(s) with FBRef scraper object
scraper.close() # closes the Selenium webdriver
```
Any FBRef functions can then be called from the scraper object.

## scrape_match
```scrape_match(link, league)```
* Inputs
	* ```link```: URL to the match to be scraped
	* ```league```: The league the match was a part of. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1"
* Outputs
	* Pandas Series containing the data for the scraped match.

## scrape_matches
```scrape_matches(year, league, save)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The league you want data from. Options are "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```save```: A boolean option to save the output dataframe to a CSV. Default value is false.
* Outputs
	* Pandas DataFrame containing all the matches of the scraped season.

## scrape_league_table
```scrape_league_table(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* Pandas DataFrame containing the league table.

## scrape_standard
```scrape_standard(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_gk
```scrape_gk(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_adv_gk
```scrape_adv_gk(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_shooting
```scrape_shooting(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_passing
```scrape_passing(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_passing_types
```scrape_passing_types(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_goal_shot_creation
```scrape_goal_shot_creation(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_defensive
```scrape_defensive(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_possession
```scrape_possession(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_playing_time
```scrape_playing_time(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_misc
```scrape_misc(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* 2 Pandas DataFrames, one containing stats for the squads (e.g. goals for), the other with stats versus the squads (e.g. goals against)

## scrape_season
```scrape_season(year, league, normalize)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```league```: The source league of the data. The only supported leagues are the "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1".
	* ```normalize```: Boolean option to normalize the table to per 90. Default value is false.
* Outputs
	* A dict, containing the outputs of the above functions for scraping squad seasonal data.

# Understat
To use the Understat module:
```
import ScraperFC as sfc
scraper = sfc.Understat()
# call function(s) with Understat scraper object
scraper.close() # closes the Selenium webdriver
```
Only match data from the EPL can be scraped from Understat at this time.

## scrape_match
```scrape_match(link)```
* Inputs
	* ```link```: URL to the match to be scraped
* Ouputs:
	* Pandas Series containing the data for the scraped match.

## scrape_matches
```scrape_matches(year, save)```
* Inputs
	* ```year```: The calendar year the season ended in. E.g. for the 2019/2020 season, enter 2020 (type int, not string).
	* ```save```: A boolean option to save the output dataframe to a CSV. Default value is false.
* Outputs
	* Pandas DataFrame containing all the matches of the scraped season.

# FiveThirtyEight
Not updated yet

# Combined
Not updated yet

# Coming soon
Not updated yet

# Contact
I'd love to hear whatever feedback, advice, criticisim, complaints, problems, errors, or new ideas you have or have come across while using ScraperFC! My email is osmour043@gmail.com.
        
