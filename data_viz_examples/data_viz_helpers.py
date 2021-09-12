import matplotlib.pyplot as plt
from   matplotlib.patches import Arc
import numpy as np
import pandas as pd
import ScraperFC as sfc
import traceback


def plot_field(ax):
    """ Taken from https://fcpython.com/visualisation/drawing-pass-map-python """
    #Pitch Outline & Centre Line
    ax.plot([0,0],[0,90], color="black")
    ax.plot([0,130],[90,90], color="black")
    ax.plot([130,130],[90,0], color="black")
    ax.plot([130,0],[0,0], color="black")
    ax.plot([65,65],[0,90], color="black")

    #Left Penalty Area
    ax.plot([16.5,16.5],[65,25],color="black")
    ax.plot([0,16.5],[65,65],color="black")
    ax.plot([16.5,0],[25,25],color="black")

    #Right Penalty Area
    ax.plot([130,113.5],[65,65],color="black")
    ax.plot([113.5,113.5],[65,25],color="black")
    ax.plot([113.5,130],[25,25],color="black")

    #Left 6-yard Box
    ax.plot([0,5.5],[54,54],color="black")
    ax.plot([5.5,5.5],[54,36],color="black")
    ax.plot([5.5,0.5],[36,36],color="black")

    #Right 6-yard Box
    ax.plot([130,124.5],[54,54],color="black")
    ax.plot([124.5,124.5],[54,36],color="black")
    ax.plot([124.5,130],[36,36],color="black")

    #Prepare Circles
    centreCircle = plt.Circle((65,45),9.15,color="black",fill=False)
    centreSpot = plt.Circle((65,45),0.8,color="black")
    leftPenSpot = plt.Circle((11,45),0.8,color="black")
    rightPenSpot = plt.Circle((119,45),0.8,color="black")

    #Draw Circles
    ax.add_patch(centreCircle)
    ax.add_patch(centreSpot)
    ax.add_patch(leftPenSpot)
    ax.add_patch(rightPenSpot)

    #Prepare Arcs
    leftArc = Arc((11,45),height=18.3,width=18.3,angle=0,theta1=310,theta2=50,color="black")
    rightArc = Arc((119,45),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color="black")

    #Draw Arcs
    ax.add_patch(leftArc)
    ax.add_patch(rightArc)

    #Tidy Axes
    plt.axis('off')
    
    return ax


def plot_goalmouth(ax):
    ax.plot([0,0], [0,8], color='black', linewidth=5) # left post
    ax.plot([0,24], [8,8], color='black', linewidth=5) # crossbar
    ax.plot([24,24], [8,0], color='black', linewidth=5) # right post
    
    ax.set_aspect('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    return ax

def plot_team_avg_positions(whoscored_link):
    ########################################################
    # Scrape match data
    ########################################################
    scraper = sfc.WhoScored()
    try:
        match_data = scraper.scrape_match(whoscored_link)
    except:
        traceback.print_exc()
    scraper.close()
    ########################################################
    # Get home and away player IDs
    ########################################################
    home_ids = [player['playerId'] for player in match_data['matchCentreData']['home']['players']]
    away_ids = [player['playerId'] for player in match_data['matchCentreData']['away']['players']]
    ########################################################
    # Build dicts for the home and away starters
    ########################################################
    home, away = dict(), dict()
    for i in range(11):
        home_id = home_ids[i]
        home[home_id] = dict()
        # Get the player's name and shirt number
        for player in match_data['matchCentreData']['home']['players']:
            if player['playerId'] == home_id:
                home[home_id]['name'] = player['name']
                home[home_id]['number'] = player['shirtNo']
        # add a place to store their events and average position
        home[home_id]['events'] = list()

        away_id = away_ids[i]
        away[away_id] = dict()
        for player in match_data['matchCentreData']['away']['players']:
            if player['playerId'] == away_id:
                away[away_id]['name'] = player['name']
                away[away_id]['number'] = player['shirtNo']
        away[away_id]['events'] = list()
    ########################################################
    # Get the events for each player
    ########################################################
    for event in match_data['matchCentreData']['events']:
        if 'playerId' not in event.keys():
            continue
        elif event['playerId'] in home.keys():
            home[event['playerId']]['events'].append([event['x'], event['y']])
        elif event['playerId'] in away.keys():
            away[event['playerId']]['events'].append([event['x'], event['y']])
    ########################################################
    # get the average position of each players' events
    ########################################################
    for i in range(11):
        ID = list(home.keys())[i]
        avg_pos = np.mean(home[ID]['events'], axis=0) # find the average position of the player
        rescaled_pos = np.multiply(avg_pos, [130/100, 90/100]) # scale to our plotting range
        home[ID]['avg pos'] = rescaled_pos

        ID = list(away.keys())[i]
        avg_pos = np.mean(away[ID]['events'], axis=0)
        # For the away team, we need to flip their locations
        rescaled_pos = np.multiply(avg_pos, [-130/100, -90/100]) # so use -130/100 here
        rescaled_pos = np.add(rescaled_pos, [130, 90]) # and shift their x position to the right
        away[ID]['avg pos'] = rescaled_pos
    ########################################################
    # Plots
    ########################################################
    home_color = (229/255,95/255,33/255)
    away_color = (51/255,134/255,222/255)
    size = 600
    fig, ax = plt.subplots(figsize=[18,12])
    ax = plot_field(ax)
    # home team
    ax.text(1, 86, 
            match_data['matchCentreData']['home']['name'], 
            fontsize=30, 
            color=home_color)
    for i in range(11):
        ID = list(home.keys())[i]
        ax.scatter(home[ID]['avg pos'][0], 
                   home[ID]['avg pos'][1], 
                   s=size,
                   facecolor=home_color, edgecolor=home_color)
        ax.text(home[ID]['avg pos'][0], 
                home[ID]['avg pos'][1], 
                home[ID]['number'], fontsize=12,
                horizontalalignment='center', 
                verticalalignment='center')
        ax.text(-8, 80-7*i, 
                home[ID]['name'], 
                horizontalalignment='right',
                fontsize=20)
        ax.text(-5, 80-7*i,
                home[ID]['number'],
                fontsize=20)
    # away team
    ax.text(129, 86, 
            match_data['matchCentreData']['away']['name'], 
            fontsize=30, 
            color=away_color,
            horizontalalignment='right')
    for i in range(11):
        ID = list(away.keys())[i]
        ax.scatter(away[ID]['avg pos'][0], 
                   away[ID]['avg pos'][1], 
                   s=size,
                   facecolor=away_color, edgecolor=away_color)
        ax.text(away[ID]['avg pos'][0], 
                away[ID]['avg pos'][1], 
                away[ID]['number'], fontsize=12,
                horizontalalignment='center', 
                verticalalignment='center')
        ax.text(138, 80-7*i, 
                away[ID]['name'],
                fontsize=20)
        ax.text(135, 80-7*i,
                away[ID]['number'],
                horizontalalignment='right',
                fontsize=20)
    return ax


def plot_thirds_transitions(whoscored_link):
    ###########################################################
    # scrape data
    ###########################################################
    scraper = sfc.WhoScored()
    try:
        match_data = scraper.scrape_match(whoscored_link)
    except:
        traceback.print_exc()
    scraper.close()
    ###########################################################
    # Get home and away player IDs
    ###########################################################
    home_ids = [player['playerId'] for player in match_data['matchCentreData']['home']['players']]
    away_ids = [player['playerId'] for player in match_data['matchCentreData']['away']['players']]
    ###########################################################
    # Parse out transitions between thirds
    ###########################################################
    col_names = ['desc', 'cross_y', 'x', 'y', 'end_x', 'end_y']
    home_def_to_mid = pd.DataFrame(columns=col_names)
    home_mid_to_att = pd.DataFrame(columns=col_names)
    away_def_to_mid = pd.DataFrame(columns=col_names)
    away_mid_to_att = pd.DataFrame(columns=col_names)
    for event in match_data['matchCentreData']['events']:
        event_desc = event['type']['displayName']
        try:
            player_id = event['playerId']
            m = (event['endY']-event['y']) / (event['endX']-event['x'])
            b = event['y'] - m*event['x']
        except KeyError:
            continue
        except ZeroDivisionError:
            continue
        if player_id in home_ids:
            if event['x']<33.3 and event['endX']>33.3 and event['endX']<66.6 and event_desc!='OffsidePass':
                home_def_to_mid = home_def_to_mid.append(
                    pd.Series({
                        'desc': event_desc,
                        'cross_y': m*33.3 + b,
                        'x': event['x'],
                        'y': event['y'],
                        'end_x': event['endX'],
                        'end_y': event['endY']
                    }),
                    ignore_index=True
                )
            # transition from middle third to attacking third
            elif event['x']<66.6 and event['endX']>66.6 and event['x']>33.3 and event_desc!='OffsidePass':
                home_mid_to_att = home_mid_to_att.append(
                    pd.Series({
                        'desc': event_desc,
                        'cross_y': m*66.6 + b,
                        'x': event['x'],
                        'y': event['y'],
                        'end_x': event['endX'],
                        'end_y': event['endY']
                    }),
                    ignore_index=True
                )
        elif player_id in away_ids:
            if event['x']<33.3 and event['endX']>33.3 and event['endX']<66.6 and event_desc!='OffsidePass':
                away_def_to_mid = away_def_to_mid.append(
                    pd.Series({
                        'desc': event_desc,
                        'cross_y': m*33.3 + b,
                        'x': event['x'],
                        'y': event['y'],
                        'end_x': event['endX'],
                        'end_y': event['endY']
                    }),
                    ignore_index=True
                    )
            # transition from middle third to attacking third
            elif event['x']<66.6 and event['endX']>66.6 and event['x']>33.3 and event_desc!='OffsidePass':
                away_mid_to_att = away_mid_to_att.append(
                    pd.Series({
                        'desc': event_desc,
                        'cross_y': m*66.6 + b,
                        'x': event['x'],
                        'y': event['y'],
                        'end_x': event['endX'],
                        'end_y': event['endY']
                    }),
                    ignore_index=True
                )
    ###########################################################
    # Plots
    ###########################################################
    n_bins = 20
    bins = np.linspace(0,100,n_bins)
    width = 1
    dx_mult = 700
    fig, ax = plt.subplots(figsize=[18,12])
    ax = plot_field(ax)
    #### Labels ####
    ax.set_title('Arrows indicate attacking direction.', y=0.96, fontsize=15)
    ax.text(
        1, 91, 
        match_data['matchCentreData']['home']['name'], 
        fontsize=30, 
        color='darkorange'
    )
    ax.text(
        129, 91, 
        match_data['matchCentreData']['away']['name'], 
        fontsize=30, 
        color='dodgerblue',
        horizontalalignment='right'
    )

    #### Out of defensive third ####
    ax.plot([130/3, 130/3], [0, 90], color='black')
    # Create histograms bins and values for each bin
    vals, _ = np.histogram(home_def_to_mid['cross_y'], bins=bins, density=True)
    # Plot the bins as arrows indicating the attacking direction. Use the values as the lengths
    for i in range(len(vals)):
        if vals[i] == 0:
            continue
        ax.arrow(
            x=130/3, y=(bins[i]+bins[1]/2) * 90/100, 
            dx=vals[i]*dx_mult, dy=0, 
            width=width, color='darkorange'
        )
    ## away team ##
    vals, _ = np.histogram(away_def_to_mid['cross_y'], bins=bins, density=True)
    for i in range(len(vals)):
        if vals[i] == 0:
            continue
        ax.arrow(
            x=130*2/3, 
            # Need to flip and shift away team y values to get them going the other way
            y=(-bins[i]+100-bins[1]/2) * 90/100, 
            dx=-vals[i]*dx_mult, dy=0, 
            width=width, color='dodgerblue'
        )

    #### Into attacking third ####
    ax.plot([130*2/3, 130*2/3], [0, 90], color='black')
    vals, _ = np.histogram(home_mid_to_att['cross_y'], bins=bins, density=True)
    for i in range(len(vals)):
        if vals[i] == 0:
            continue
        ax.arrow(
            x=130*2/3, y=(bins[i]+bins[1]/2) * 90/100, 
            dx=vals[i]*dx_mult, dy=0, 
            width=width, color='darkorange'
        )
    ## away team ##
    vals, _ = np.histogram(away_mid_to_att['cross_y'], bins=bins, density=True)
    for i in range(len(vals)):
        if vals[i] == 0:
            continue
        ax.arrow(
            x=130/3, y=(-bins[i]+100-bins[1]/2) * 90/100, 
            dx=-vals[i]*dx_mult, dy=0, 
            width=width, color='dodgerblue'
        )
    return ax