def check_season(year,league,source):
    assert source in ['FBRef','Understat','FiveThirtyEight','All']
    error = None
    
    # make sure year is an int
    if type(year) != int:
        error = "Year needs to be an integer."
        return error, False
    
    # make sure league is a valid string
    if type(league) != str or league not in ["EPL","La Liga","Serie A","Ligue 1","Bundesliga"]:
        error = "League needs to be a string. Options are \"EPL\", \"La Liga\", \"Bundesliga\", \"Serie A\", \"Ligue 1\"."
        return error, False
    
    # make sure year is valid for a given source
    yr_valid = True
    if source=='FBRef':
        if league=='EPL' and year<1993:
            error = 'Year invalid for source FBRef, EPL. Must be 1992/93 or later.'
            yr_valid = False
        elif league=='La Liga' and year<1989:
            error = 'Year invalid for source FBRef, La Liga. Must be 1988/89 or later.'
            yr_valid=False
        elif league=='Bundesliga' and year<1989:
            error = 'Year invalid for source FBRef, Bundesliga. Must be 1988/89 or later.'
            yr_valid=False
        elif league=='Serie A' and year<1989:
            error = 'Year invalid for source FBRef, Serie A. Must be 1988/89 or later.'
            yr_valid=False
        elif league=='Ligue 1' and year<1996:
            error = 'Year invalid for source FBRef, Ligue 1. Must be 1995/96 or later.'
            yr_valid=False
    elif source=='Understat' and year<2015:
        error = 'Year invalid for source Understat. Must be 2014/15 or later.'
        yr_valid = False
    elif source=='FiveThirtyEight' and year<2017:
        error = 'Year invalid for source FiveThirtyEight. Must be 2016/17 or later.'
        yr_valid = False
    return error, yr_valid
        