def check_season(year,league,source):
    
    # make sure year and league are right type
    if type(year) != int:
        print("Year needs to be an integer.")
        return False
    elif type(league) != str:
        print("League needs to be a string. Options are \"EPL\", \"La Liga\","+
              "\"Bundesliga\", \"Serie A\", \"Ligue 1\".")
        return False
    
    # make sure year has the columns I think they will.
    # for now, this is just seasons with xG data
    yr_valid = False
    assert source in ['FBRef','Understat','FiveThirtyEight','All']
    # Make sure data is available from the requested season/source
    if (source == 'FBRef') and (year >= 2018):
        yr_valid = True
    elif (source == 'Understat') and (year >= 2015):
        yr_valid = True
    elif (source == 'FiveThirtyEight') and (year >= 2017):
        yr_valid = True
    else: # all sources case
        if year >= 2018:
            yr_valid = True
    
    # make sure the entered league is one that can be scraped
    lg_valid = False
    if league in ["EPL","La Liga","Serie A","Ligue 1","Bundesliga"]:
        lg_valid = True
    
    # print reasons for failing
    if not (yr_valid and lg_valid):
        print("ERROR: Invalid season chosen for source "+source,".")
        if not yr_valid:
            print("ERROR: Invalid year.")
        if not lg_valid:
            print("ERROR: Invalid league. Options are \"EPL\", \"La Liga\","+
              "\"Bundesliga\", \"Serie A\", \"Ligue 1\".")
    
    return (yr_valid and lg_valid)
        