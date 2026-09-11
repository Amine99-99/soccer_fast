from ...models import Team,User,Player,ReqJoinTeamGame,ReqJoinTeam  
from ...core.debs import session_db 
from sqlmodel import select
from ..base.event import Event  
from .observation import memory_long_term
from ...models import User




'''
reqs of player how rejected wich team reson team state at my request how long took to return answer 
teams state of ech team on time of event  


'''


def teams_valid(observation:dict):
    teams = observation['teams']
    player = observation['player']
    teams = [ t for t in teams if t.confirmed_players<t.number_of_players]
    teams  = [
        t for t in teams if not any(p.position== player.position  for p in t.players )
    ]
    print('te',teams)
    return teams 




def requested_teams(observation: dict):

    teams = teams_valid(observation=observation)

    filtered_teams = []

    for t in teams:
        pending = [r for r in t.reqs_team if r.status_req == 'pending']
        print(t.reqs_team,'requests')
        pending_rate = len(pending)
        print(pending_rate)

        remaining_slots = int(t.number_of_players) - int(t.confirmed_players)
        print('remai',remaining_slots)

        if (remaining_slots-pending_rate) > 3:
            filtered_teams.append(t)

    print('teams', filtered_teams)
    print(len(filtered_teams), 'length 2')

    return filtered_teams

    
    
def non_requested_teams(observation:dict):
    teams = teams_valid(observation=observation)
    teams = [t for t in teams if len(t.reqs_team)==0]
    return teams 

def teams_final(observation:dict,session:session_db,event:Event):
    memory_list = memory_long_term(session=session,event=event)

    teams_1 = non_requested_teams(observation=observation)
    teams_2 = requested_teams(observation=observation)


    last_list = teams_1 + teams_2
    final_list = [t for t in last_list if not any(m.status_response=='denied' for m in memory_list)]
    print('last team',final_list)

    return final_list



