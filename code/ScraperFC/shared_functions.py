def check_season(year,league,source):
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
    
    lg_valid = False
    if league in ["EPL","La Liga","Serie A","Ligue 1","Bundesliga"]:
        lg_valid = True
    
    if not (yr_valid and lg_valid):
        print("ERROR: Invalid season chosen for source "+source,".")
        if not yr_valid:
            print("ERROR: Invalid year.")
        if not lg_valid:
            print("ERROR: Invalid league.")
    
    return (yr_valid and lg_valid)
        