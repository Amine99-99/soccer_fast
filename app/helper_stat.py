from datetime import datetime
from .models import Game ,Appointment,User,UserField,StatDisciplinary ,GameRegisterStat,GameStat,Stat,Team,Notification,GameRegisterStatDisciplinary
from .core.debs import session_db
from sqlmodel import select
from uuid import UUID
from fastapi import HTTPException



def confirm_game(session:session_db,game_id:str):
    game_db=session.get(Game,UUID(game_id))
    if game_db is None :
          raise HTTPException(
            status_code=401,
            detail='Invalid Game'
        )
    if game_db.status!='pending':
          raise HTTPException(
            status_code=401,
            detail='Invalid Status'
        )
    game_db.status=='confirmed'
    session.add(game_db)
    session.commit()
    session.refresh(game_db)
    


def get_stat(session:session_db,game:GameRegisterStat|GameRegisterStatDisciplinary):
    stat = session.exec(select(GameStat).where((GameStat.game_id==game.game_id)& (GameStat.team_id==game.team_id))).first()
    return stat 
def validate_stat(session:session_db,game:GameRegisterStat|GameRegisterStatDisciplinary,user:User|UserField):
    team_id = game.team_id 
    team_db= session.get(Team,UUID(team_id))
    if team_db.user_id !=user.id:
        raise HTTPException(
            status_code=401,
            detail='Invalid User'
        )

    game_db = session.get(Game,UUID(game.game_id))
    if not game_db:
        raise HTTPException(
            status_code=404,
            detail='Game Not found'
        )
    if game_db.status!='confirmed':
        raise HTTPException(
            status_code=401,
            detail='game must be confirmed'
        )
    
    now= datetime.now()
    game_time = datetime.combine(game_db.date,game_db.time)
   
    if now<game_time:
        raise HTTPException(
            status_code=401,
            detail ="Stat are not valid,game didn't finish"
        )
def create_stat(session:session_db,game:GameRegisterStat,user:User|UserField):
    validate_stat(session=session,game=game,user=user)


    if isinstance(user,User):
        stats_db = GameStat(game_id=UUID(game.game_id),user_id=user.id,user_field_id=None,team_id=UUID(game.team_id))
    elif isinstance(user,UserField):
        stats_db = GameStat(game_id=UUID(game.game_id),user_id=None,user_field_id=user.id,team_id=UUID(game.team_id))
    session.add(stats_db)
    session.commit()
    session.refresh(stats_db)
    print('first stat db',stats_db)
    return stats_db 

def set_players_stat(session:session_db,game:GameRegisterStat,user:User|UserField):
    game_stat= session.exec(select(GameStat).where(GameStat.game_id==UUID(game.game_id))).first()
    if game_stat:
        stat_db_id=game_stat.id 
    else:
        stat_db = create_stat(session=session,game=game,user=user)
        print('stat db',stat_db)
        stat_db_id =stat_db.id
        
   
  
    stats_players=[]
    player_stats = [p_s for p_s in game.stats]
    for pla_st in  player_stats:
        pla_st_db=Stat(technical_execution=pla_st.technical_execution,tactical_intelligence=pla_st.tactical_intelligence,physical_contribution=pla_st.physical_contribution,
                       mental_attitude=pla_st.mental_attitude,impact_on_the_game=pla_st.impact_on_the_game,player_id=UUID(pla_st.player_id),game_stat_id=stat_db_id)
        session.add(pla_st_db)
        stats_players.append(pla_st_db)
    session.commit()
    for player_stat in stats_players:
        session.refresh(player_stat)
    return stats_players

def set_players_disciplinary_stat(session:session_db,game:GameRegisterStatDisciplinary,user:User|UserField):
    game_stat= session.exec(select(GameStat).where(GameStat.game_id==UUID(game.game_id))).first()
    if game_stat:
        stat_db_id=game_stat.id 
    else:
        stat_db = create_stat(session=session,game=game,user=user)
        print('stat db',stat_db)
        stat_db_id =stat_db.id

    disciplinary_players=[]
    players_disciplinary= [p for p in game.stats_disciplinary]
    for p in players_disciplinary:
        new_disciplinary=StatDisciplinary(
            attendance=p.attendance,punctuality=p.punctuality,
            behavior=p.behavior,commitment=p.commitment,
            payment_status=p.payment_status,player_id=UUID(p.player_id),
            game_stat_id=stat_db_id



        )
        session.add(new_disciplinary)
        disciplinary_players.append(new_disciplinary)
    session.commit()
    for s in disciplinary_players:
        session.refresh(s)
    return disciplinary_players
        


def notify(session:session_db,user_id:str,sender_id:str,type:str,ref_id:str,read:bool):
    new_notification = Notification(
        user_id=UUID(user_id),type=type,sender_id=UUID(sender_id),reference_id=UUID(ref_id),is_read=read
    )
    session.add(new_notification)
    session.commit()
    session.refresh(new_notification)
    return new_notification 



   

 



    



