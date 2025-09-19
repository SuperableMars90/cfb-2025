import pandas as pd
import json
from datetime import datetime
from pprint import pprint

# drop = 'Arkansas State'
# add = 'Colorado'
# owner = 'Jacob'
# check = 0
# addclass = 'P5'
# addconf = 'Big 12'

def check_teamnum(teammap,create=False,print_num=False):
    if create:
        unique_teams_map = {i:[] for i in teammap}
    for player in teammap:
        teams = []
        for conference in teammap[player]:
            for team in teammap[player][conference]:
                if team not in teams:
                    teams.append(team)
        if create:
            unique_teams_map[player]=teams
        if len(teams)!=26:
            print(f'Improper number of teams for: {player}')
        else:
            check = 0
        if print_num:
            print(len(teams))
    if create:
        return unique_teams_map
    else:
        return check
    
    
def check_drop(unique_teams_map,player,drop):
    check = 0
    if drop not in unique_teams_map[player]:
        check+=1
    else:
        print('Drop error')
    return check

def check_add(unique_teams_map,owner,add):
    check = 0 
    for player in unique_teams_map:
        if player!=owner:
            if add in unique_teams_map[player]:
                check+=1
            else:
                print('Add error')

    return check

def drop_team(team,player,teammap):
    drops = []
    passes = []
    for conference in teammap[player]:
        try:
            teammap[player][conference].remove(team)
            drops.append(conference)
        except:
            #print(conference)
            #print(teammap[player][conference])
            #print('------------')
            passes.append(conference)
    print(f'Dropped teams from {drops}')
    print(f'Team not found in {passes}')
    return teammap

def add_team(add,owner,teammap,teamconf):
    g5ind = ['American Athletic','Conference USA','Mid-American','Mountain West','Sun Belt','G5 Flex']
    p4ind = ['ACC','Big 10','Big 12','SEC','P4 Flex']
    if teamconf in g5ind:
        addclass = 'G5'
    elif teamconf in p4ind:
        addclass = 'P4'
    else:
        addclass = teamconf
    #print(teamconf)
    if addclass == 'P4':
        teammap[owner][teamconf].append(add)
        teammap[owner]['P4 Flex'].append(add)
    elif addclass == 'G5':
        teammap[owner][teamconf].append(add)
        teammap[owner]['G5 Flex'].append(add)
    elif addclass == 'P4 Independent':
        for conference in p4ind:
            teammap[owner][conference].append(add)
            teammap[owner]['P4 Flex'].append(add)
    elif addclass == 'G5 Independent':
        for conference in g5ind:
            teammap[owner][conference].append(add)
            teammap[owner]['G5 Flex'].append(add)
    else:
        print('Whoops, there was an error. Incorrect classification')
    teammap[owner]['Wild Card'].append(add)
    return teammap

def rewrite_json(data,jsonfile_path):
    with open(jsonfile_path,'w+') as f:
        json.dump(data,f)

def drop_add(drop,add,owner,addconf,teammap,mappath,log,logpath):
    unique_teams_map = check_teamnum(teammap,create=True)
    check = 0
    check+=check_drop(unique_teams_map,owner,drop)
    check+=check_add(unique_teams_map,owner,add)
    if check == 0:
        teammap = drop_team(drop,owner,teammap)
        teammap = add_team(add,owner,teammap,addconf)
    else:
        print('Check error')
    check += check_teamnum(teammap,create=False)
    if check == 0:
        rewrite_json(teammap,mappath)
        now = datetime.now()
        formatted = now.strftime("%Y/%m/%d %H:%M:%S")
        move = {
            'player':owner,
            'drop':drop,
            'add':add,
            'timestamp':formatted
        }
        log.append(move)
        rewrite_json(log,logpath)
    else:
        print('Error on new team update team count.')