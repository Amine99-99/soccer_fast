from fastapi import APIRouter ,Query,Depends 
from ..models import Fields,Game,Team,Player,User,UserField,Academy
from typing import Annotated,Optional
from ..core.debs import session_db,get_current_active_user
from sqlmodel import select
from datetime import date
from ..agents.agent_queue.publisher import publish_event,find_player
from ..agents.base.event import Event
import os
import uuid
from sqlalchemy.orm import selectinload




search=APIRouter()


@search.get('/fields_registred',status_code=200)
def search_field(session:session_db,city:Annotated[str|None,Query()]=None,code:Annotated[str|None,Query()]=None,
                 name_street:Annotated[str|None,Query()]=None,field_name:Annotated[str|None,Query()]=None):
    stmt_field = select(Fields).where(Fields.status=='active',Fields.is_active==True)
    if city:
        stmt_field = stmt_field.where(Fields.city.ilike(f"%{city}%"))
    if code :
        stmt_field = stmt_field.where(Fields.postal_code==code)
    if name_street:
        stmt_field = stmt_field.where(Fields.address.ilike(f"%{name_street}%"))
    if field_name:
        stmt_field = stmt_field.where(Fields.field_name.ilike(f"%{field_name}%"))
    
    results = session.exec(stmt_field).all()
    result_search=[
        {
            'id':f.id,
            'field_name':f.field_name,
            'city':f.city,
            'address':f.address
        }
        for f in results
    ]
    return result_search
@search.get('/find_games',status_code=200)
def search_games(session:session_db,date:date|None=Query(None),field_name:str|None=Query(None),
                 coach:str|None=Query(None),city:str|None=Query(None)):
    stmt_game = select(Game).where(Game.status=='pending')
    if date:
        stmt_game = stmt_game.where(Game.date==date)
        print(stmt_game,'date stmt')
        
  
    if field_name:
        stmt_game = stmt_game.join(Game.field).where(Fields.field_name.ilike(f"%{field_name}%"))
    if coach:
        stmt_game = stmt_game.join(Game.user).where(User.username.ilike(f"%{coach}%")) if Game.user_id else  stmt_game.Join(Game.user_field).where(UserField.username.ilike(f"%{coach}%"))
    if city:
        stmt_game = stmt_game.join(Game.field).where(Fields.city.ilike(f"%{city}%"))
    results = session.exec(stmt_game).all()
    results_game=[
        {
            'id':g.id,
            'date':g.date,
            'time':g.time,
            'owner':g.user.username if g.user else g.user_field.username,
            'city':g.field.city,
            'field_name':g.field.field_name,

        }
        for g in results
    ]
   
    return results_game

@search.get('/find_teams',status_code=200)
def search_teams(session:session_db,user:Annotated[User,Depends(get_current_active_user)],coach:Annotated[str|None,Query]=None,city:Annotated[str|None,Query()]=None,address:Annotated[str|None,Query()]=None):
    stmt_teams = select(Team)
    print('stmt',stmt_teams)

    if coach:
        stmt_teams= stmt_teams.where(Team.coach_name.ilike(f"%{coach}%"))
    if city:
        stmt_teams = stmt_teams.join(Team.user).where(User.city.ilike(f"%{city}%")) if Team.user_id else stmt_teams.join(Team.user_field).where(UserField.city.ilike(f"%{city}"))

    if address:
           stmt_teams = stmt_teams.join(Team.user).where(User.address.ilike(f"%{address}%")) if Team.user_id else stmt_teams.join(Team.user_field).where(UserField.address.ilike(f"%{address}"))

    print(city,'city')

    results = session.exec(stmt_teams).all()
    results_team =[
        {
            'id':t.id,
            'coach':t.coach_name,
            'team_name':t.team_name,
           
            'team_city':t.user.city if t.user else t.user_field.city,
            'team_address':t.user.address if t.user else t.user_field.address
        }
        for t in results
    ]
    event_id=str(uuid.uuid4())
    extra_payload={
        'city':city,
        
    }
    print("Publishing event for user:", user.username, "with payload:", extra_payload)
    event_id=publish_event(user=user,extra_payload=extra_payload)
    
   
    print("DB PATH:", os.path.abspath("database.db"))
    print(results_team)
    return {'result':results_team,'event_id':event_id}

@search.get('/find_players',status_code=200)
def search_players(session:session_db,user:Annotated[User,Depends(get_current_active_user)],phone:Annotated[str|None,Query()]=None,name:Annotated[str|None,Query()]=None,city:Annotated[str|None,Query()]=None
                   ,address:Annotated[str|None,Query]=None):
    stmt_players= select(Player)
    if phone:
        stmt_players = stmt_players.where(Player.phone==phone)
    if name:
        stmt_players = stmt_players.where(Player.name==name)
        
    if city:
        stmt_players = stmt_players.join(Player.user).where(User.city.ilike(f"%{city}%"))
    if address:
        stmt_players = stmt_players.join(Player.user).where(User.address.ilike(f"%{address}%")) 

    results = session.exec(stmt_players).all()
    results_player=[
        {
            'id':p.id,
            'name':p.name,
            'phone':p.phone,
            'city':p.user.city ,
            'address':p.user.address 
        }
        for p in results
    ]
   
    return  results_player 


@search.get('/find_academies',status_code=200)
def search_academies(session:session_db,
                   
                    academy_name:Annotated[str|None,Query()]=None,
                    city:Annotated[str|None,Query()]=None,
                    address:Annotated[str|None,Query()]=None,
                    coach_name:Annotated[str|None,Query()]=None
                    ):
    stmt_academies = select(Academy).options(selectinload(Academy.programs),selectinload(Academy.user))
    if city :
        stmt_academies = stmt_academies.where(Academy.city.ilike(f"%{city}%"))
    if academy_name:
        stmt_academies = stmt_academies.where(Academy.name==academy_name)
   
    if address:
        stmt_academies = stmt_academies.where(Academy.address.ilike(f"%{address}%"))
    if coach_name:
        stmt_academies = stmt_academies.where(Academy.user.username.ilike(f"%{coach_name}%"))

    result = session.exec(stmt_academies).all()
    print('result',result)

    academies_searched= [
        {
           'id':my_academy.id,
             'name':my_academy.name,
    
            'city':my_academy.city,
            'address':my_academy.address,
           'description':my_academy.description,
           'coach':my_academy.user.username,
           'programs':[
                  {
                       'id': program.id,
    'name': program.name,
    'min_age': program.min_age,
    'max_age': program.max_age,
    'gender': program.gender,
    'status': program.status,
    'coach': program.coach.username if program.coach else None,
    'description': program.description,
    'max_players': program.max_players,
    'amount_fee': program.amount_fee_period,
   
    'open': program.enrollment_open,
    'academy_id':program.academy_id,
    'academy_name':program.academy.name,
    'logo':program.academy.logo,
                
            }
            for program in my_academy.programs
               

               

           ]

        }
        for my_academy in result
    ]
    return academies_searched





