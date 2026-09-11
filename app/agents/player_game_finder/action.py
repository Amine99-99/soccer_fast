from ...models import Team,User,Player,ReqJoinTeamGame,ReqJoinTeam  
from ...core.debs import session_db 
from sqlmodel import select
from ..base.event import Event    





def  acting(decision:list):
    teams = decision 
    
    return teams