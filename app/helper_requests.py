from .models import User,UserField,Team,PlayersRegister,GameTeam,Player,GameBase,Game,Appointment,ReqJoinTeamGame,Fields,BuildTeam,ReqJoinTeam
from .core.debs import session_db 

from sqlmodel import select
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import selectinload



def ser_player(pl:PlayersRegister)->dict:
    data = pl.model_dump()
    data['id'] = str(data['id'])
    return data 

def register_players_t2(teamr:BuildTeam,session:session_db,teamdb:Team):
    players_come = [player_team for player_team in teamr.players ] 
    added_to_db=[]
    for pl in players_come:
        existing_user = session.exec(select(User).where(User.phone==pl.phone)).first()
        existing_player = session.exec(select(Player).where(Player.phone==pl.phone)).first()
        if existing_player:
            player_db=existing_player 
     
        else:
            player_db=Player(phone=pl.phone,name=pl.name,player_status=pl.player_status,user_id=existing_user.id if existing_user else None )

            session.add(player_db)
        added_to_db.append(player_db)
    
    session.commit()
    links_team=[]
    for player_db in added_to_db:
        session.refresh(player_db)
        player_team=TeamPlayer(team_id=teamdb['id'],player_id=player_db.id)
        session.add(player_team)
        links_team.append(player_team)
    session.commit()
    for player_team in links_team:
        session.refresh(player_team)
    return {
        'link':links_team,'players':added_to_db
    }

   







   


def game_exist(session:session_db,app:Appointment,user:User|UserField):
    games=session.exec(select(Game).where(Game.user_id==user.id)).all()
    
    game_d = next((ga for ga in games if (ga.date==app.date and ga.time==app.time)),None)
  
    return game_d
    
    
def start_game(session:session_db,app_id:str,team_number:int,user:User|UserField):
    
    
    
    app_d =session.get(Appointment,UUID(app_id))
    game_db = game_exist(session=session,app=app_d,user=user)
    print('app_d',app_d)
    field_db = session.get(Fields,app_d.field_id)
    if game_db:
        raise HTTPException(
            status_code=403,
            detail='Game exist'
            
        )
    if isinstance(user,User):
        game_db = Game(
             date=app_d.date,
             time=app_d.time,
             players_per_team=team_number,
             status='pending',
             
            
             field_id=field_db.id,
             user_id=user.id,
             user_field_id=None


    )   
      
        team = session.exec(select(Team).where(Team.user_id==user.id)).first()
       

    elif isinstance(user,UserField):
        game_db = Game(
             date=app_d.date,
             time=app_d.time,
              players_per_team=team_number,
              status='pending',
             
           
             field_id=field_db.id,
             user_id=None,
             user_field_id=user.id


    )
        team = session.exec(select(Team).where(Team.user_field_id==user.id)).first()
    session.add(game_db)
    session.commit()
    session.refresh(game_db)
    if team is not None:
            team_id =team.id
            game_id = game_db.id
            team_game=GameTeam(team_id=team_id,game_id=game_id,status='confirmed')
    app_d.game_id=game_db.id
    session.add(team_game)
    session.commit()
    session.refresh(app_d)
    session.refresh(team_game)
   
   
    return game_db


def exist_player(session:session_db,team_id:UUID,user:User|UserField):
    
    
    tea_db = session.get(Team,team_id)
    print('tea_db',tea_db)
    player_db = next((pla for pla in tea_db.players if pla.user_id==user.id),None)
    print(player_db,'player_db')


    return player_db
def exist_req(session:session_db,team_id:UUID,id_game:UUID,user:User|UserField):
    player_db = user.player 
    player_id= player_db.id
    req_db = session.exec(select(ReqJoinTeamGame).where((ReqJoinTeamGame.player_id==player_id)&(ReqJoinTeamGame.game_id==id_game)&(ReqJoinTeamGame.team_id==team_id))).first()
    return req_db

def exist_req_team(session:session_db,team_id:UUID,user:User|UserField):
    player_db=user.player
    player_id=player_db.id
    req_db = session.exec(select(ReqJoinTeam).where((ReqJoinTeam.player_id==player_id)&(ReqJoinTeam.team_id==team_id))).first()
    return req_db


def game_state_tracker(session: session_db, game_id: str):
    game = session.exec(
        select(Game)
        .where(Game.id == UUID(game_id))
        .options(
            selectinload(Game.teams).selectinload(Team.memberships),
            selectinload(Game.appointments),
            selectinload(Game.reqs_game),
        )
    ).first()
    user_id = game.user_id 
    team_coach = next((t for t in game.teams if t.user_id == user_id),None)

    if not game:
        return None

   
    reqs_approved = [
        r for r in game.reqs_game if r.status == "confirmed"
    ]

   
    approved_team_ids = {r.team_id for r in reqs_approved}

    teams_approved = [
        t for t in game.teams if t.id in approved_team_ids
    ]
    teams_approved.append(team_coach)
    print(teams_approved,'team approved')

    
    teams_active = [
        [m for m in t.memberships if m.status == "active"]
        for t in teams_approved
    ]

  
    app_approved = any(
        app.status == "approved" for app in game.appointments
    )

    
    completed_teams = [
        t for t in teams_active
        if len(t) == game.players_per_team
    ]


    if len(completed_teams)==2 and app_approved:
        game.status='confirmed'
        session.add(game)
    else:
        game.status='pending'

    session.commit()
    session.refresh(game)
    return game

    


  
   


   
    



    
                       



    