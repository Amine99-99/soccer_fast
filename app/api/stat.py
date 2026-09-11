from datetime import datetime 
from fastapi import APIRouter,HTTPException,Depends,Form,UploadFile 
from ..core.debs import session_db ,get_current_active_user
from ..models import Game,User,UserField,GameRegisterStat,GameStat,GameRegisterStatDisciplinary
from typing import Annotated
from ..helper_stat import set_players_stat,set_players_disciplinary_stat





stat = APIRouter()

@stat.post('/game_stat',status_code=201)
def build_stat(session:session_db,game:GameRegisterStat,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    stats_players = set_players_stat(session=session,game=game,user=user)
    return stats_players

@stat.post('/disciplinary_stat',status_code=201)
def build_stat(session:session_db,game:GameRegisterStatDisciplinary,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    stats_players = set_players_disciplinary_stat(session=session,game=game,user=user)
    return stats_players





