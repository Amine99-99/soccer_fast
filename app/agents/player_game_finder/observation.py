from ...models import Team,User,Player,ReqJoinTeamGame,ReqJoinTeam  
from ...core.debs import session_db 
from sqlmodel import select
from ..base.event import Event
from ..memory.vector_store import EventUser,SearchEvent
from uuid import UUID
from ..memory.vector_store import RequestD,MemoryResponse
from sqlalchemy.orm import selectinload





def get_player_user(session:session_db,event:Event):
    print("ALL PLAYERS:", session.exec(select(Player)).all())
    print('event',event.event_type)
    print(event.payload,'payload')
    stmt = select(Player).options(selectinload(Player.reqs_team)).where(Player.user_id==UUID(event.payload['player_id']))
    player = session.exec(stmt).first()
    print(player,'player')
    return player



def get_teams_finder(session:session_db,event):
    print('hi')
    print('payload',event.payload)
    
   
    city = event.payload['city']


   

    statement = select(Team).options(selectinload(Team.reqs_team)).join(Team.user).where(User.city==city)
    teams = session.exec(statement).all()
    print('teams',teams)
    return teams

def get_request_team(session:session_db,event:Event):
    player_id=event.payload['player_id']
    print('player_id',player_id)
    req_id = event.payload['req_id']
    team_id = event.payload['team_id']
    event_user = session.exec(select(SearchEvent).where(SearchEvent.player_id == UUID(player_id)).order_by(SearchEvent.created_at.desc())
).first()
    print(event_user,'user event')
    team = next((team for team in event_user.result if team['id']== team_id ),None)
    print('team',team)
    if team :
        req_ob = RequestD(req_id=UUID(req_id),team_id=UUID(team_id),event_id=event.event_id)
        print(req_ob,'req')
        session.add(req_ob)
        session.commit()
        session.refresh(req_ob)
        return req_ob
    else :
        return None

def get_response(session:session_db,event:Event):
    req_id = event.payload['req_id']
    req = session.get(ReqJoinTeam,UUID(req_id))
    req_status = req.status_req 
    team_id = req.team_id
    memory_db = MemoryResponse(team_id=team_id,response_status=req_status,req_id=req_id,player_id=req.player_id)
    return memory_db



def memory_long_term(session:session_db,event:Event):
    player =session.exec(select(Player).where(Player.user_id==UUID(event.payload['player_id']))).first()
    memory_list = session.exec(select(MemoryResponse).where(MemoryResponse.player_id==player.id)).all()
    print('memory_list',memory_list)
    return memory_list
  






    '''
    get reqs for team not in game  
    get reqs for team in game 
    player reqs 
    teams reqs 
    if number of players === confirmed players deny team 
    player position actual team state 
    teams fetched 
    player
    get historic player request 
    get each team record reqs 
    request by playr based on suggestion by agent get all requests by player and add it to a list  
    response get all response and add to a list then store all that in memeory list or db Memory 
    user search use has id name 
    teams list has id player city 
    agent look to search list ,he has memory of teams already suggested in past  
    the gent take actions based on data 
    why all this happening 
    user could request to join many teams 
    and user could just request one team most probably request to join one team and wait response 
    teams instance is short living processable 
    could be completed in just two hours  
    



    '''


