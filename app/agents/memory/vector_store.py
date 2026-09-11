from sqlmodel import SQLModel ,Field 
import uuid 
from ..base.event import Event 
from typing import List

from ...core.debs import session_db
from ...models import Player
from sqlalchemy import Column, JSON, ForeignKey
from uuid import UUID
from datetime import datetime
from sqlmodel import select




def mem(event:Event,result:list,session:session_db):
    user_id = UUID(event.payload['player_id'])
    player= session.exec(select(Player).where(Player.user_id==user_id)).first()
    player_id=player.id
    print('player_id',player_id,player)
    

    print('result',result)
    
    result_serialized = [
    {
        "id": str(t.id),
        "team_name": t.team_name,
        "team_coach": t.coach_name,
        "number_of_players": t.number_of_players,
        "confirmed_players": t.confirmed_players
    }
    for t in result
]
    event_id=event.event_id
    new_event_user = SearchEvent(player_id=player_id,result=result_serialized,event_id=event_id)
    session.add(new_event_user)
    session.commit()
    session.refresh(new_event_user)
    print('new event user',new_event_user.id,'id',new_event_user.result)
    return new_event_user







class PlayerEvent(SQLModel,table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    player_id:uuid.UUID
    event_id:str 
    desicion:str
    rate:float

    
class SearchEvent(SQLModel,table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    player_id:uuid.UUID 
    result:List[dict]= Field(sa_column=Column(JSON))
    event_id:str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RequestD(SQLModel,table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    req_id:uuid.UUID 
    team_id:uuid.UUID
    event_id:str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MemoryResponse(SQLModel,table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    response_status:str
    team_id:uuid.UUID 
    req_id:uuid.UUID
    player_id:uuid.UUID
    event_id:str
    created_at: datetime = Field(default_factory=datetime.utcnow)






'''


'''




