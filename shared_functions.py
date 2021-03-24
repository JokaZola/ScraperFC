def check_season(year,league,source):
    valid = False
    assert source in ['FBRef','Understat','FiveThirtyEight','All']
    # Make sure data is available from the requested season/source
    if (source == 'FBRef') and (year >= 2018):
        valid = True
    elif (source == 'Understat') and (year >= 2015):
        valid = True
    elif (source == 'FiveThirtyEight') and (year >= 2017):
        valid = True
    else: # all sources case
        if year < 2018:
            valid = True        
    return valid
        