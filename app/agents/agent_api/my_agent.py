from fastapi import APIRouter ,Query,Depends 

from typing import Annotated,Optional
from ...core.debs import session_db,get_current_active_user
from sqlmodel import select
from datetime import date

from ...models import User,UserField,Player
from ..base.event import Event
from ..memory.vector_store import SearchEvent,PlayerEvent










my_agent=APIRouter()
 
    




@my_agent.get('/my_team_suggestion',status_code=200)
def get_my_agent_list(session:session_db,event_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    
    player = session.exec(select(Player).where(Player.user_id==user.id)).first()
    print('player',player,user.username)
    if not event_id:
        return 
    event_user = session.exec(select(SearchEvent).where(SearchEvent.event_id==event_id)).first()


    print(event_user,'user')
   
    
    
    result = event_user.result
    print('result',result)
    teams_result = [
        {
            'id':t['id'],
            'team_name':t['team_name'],
            'team_coach':t['team_coach']
        }
        for t in result
    ]
   
    
    return teams_result


@my_agent.get('/request_player_agent',status_code=200)
def get_agent_decision_player_req(session:session_db,event_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    player_event = session.exec(select(PlayerEvent).where(PlayerEvent.event_id==event_id)).first()

    return player_event