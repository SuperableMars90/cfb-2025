### Imports

import pandas as pd
import os
import json
os.chdir('C:\\Users\\zcroc\\CFB_competition\\source\\')
import cfbd_api_utils as cfbd
import roster_utils
import team_utils
import team_utils
os.chdir('C:\\Users\\zcroc\\CFB_competition\\')

def create_schedule_data(year,week_0_gameIDs=[],conf_priority_mapping='data/conference_priority_file.json'):
    '''
    Function to create the schedule df. Can be called separately from writing to allow customization
    '''
    games_EP = 'https://api.collegefootballdata.com/games?year={year}&classification=fbs'
    games_data = cfbd.request_json(games_EP)
    schedule  = {}
    conference_priority = json.load(open(conf_priority_mapping))
    for game in games_data:
        if game['id'] in week_0_gameIDs:
            week = 0
        else:
            week = game['week']
        neutral = game['neutralSite']
        for team in ['home','away']:
            name = game[f"{team}Team"]
            isConf = game['conferenceGame']
            conf = game[f"{team}Conference"]
            div = game[f"{team}Classification"]
            if team=='away':
                if neutral == False:
                    opp = f"@ {game['homeTeam']}"
                elif neutral == True:
                    opp = game['homeTeam']
            elif team=='home':
                opp = game['awayTeam']
            else:
                print('problem')
                print(game)
                print('----------------')
            if neutral == True:
                opp += '\\neutral'
            if isConf == True:
                opp = opp.upper()
            try:
                priority = conference_priority[conf]
                if name in schedule:
                    schedule[name][f"Week {week}"]=opp
                else:
                    schedule[name]={
                        'Conference':conf,
                        'priority':priority,
                        f"Week {week}":opp}
            except:
                print(conf)
    return schedule

def create_df(schedule):
   df = pd.DataFrame.from_dict(schedule,orient='index')
   df.fillna('Bye',inplace=True)
   df.sort_values('priority',inplace=True)
   df = df[['Conference', 'Week 0', 'Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12', 'Week 13', 'Week 14',  'Week 16']]
   return df
                
week_0_gameIDs = [401760371,401756846,401756847,401757218,401754516]
schedule = create_schedule_data(2025,week_0_gameIDs=week_0_gameIDs)
df = create_df(schedule)