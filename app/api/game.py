from fastapi import APIRouter,HTTPException,Depends,Form,UploadFile
from ..helper_3 import create_team,register_players,relate_team_game
from ..models import Court,UserField,Fields,GameTeam,ReqJoinTeamGame
from ..models import Appointment,AppointmentRegister,MemberShip,User,Team,BuildTeam,Notification,Player,Game,GameBase,GameTeam,RequestGameJoin,PlayersRegister,ReqJoinTeam
from ..core.debs import session_db,get_courts_registred,get_current_active_user
from typing import Annotated,List
from sqlmodel import select
import json
from uuid import UUID 
from typing import Annotated
from ..helper_requests import register_players_t2,start_game,exist_player,exist_req,exist_req_team,game_state_tracker
from sqlalchemy.orm import selectinload
from ..agents.agent_queue.publisher import publish_event_1,publish_response,find_player
from ..helper_stat import notify,confirm_game

game = APIRouter()

@game.post('/register_player',status_code=201)
def register_play(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)],player:PlayersRegister)->Player:
    player_db = session.exec(select(Player).where((Player.phone==player.phone)&(Player.user_id ==user.id))).first()
    if player_db:
        raise HTTPException(
            status_code=401,
            detail='PLayer registred'
        )
    new_player_db = Player(
        phone=player.phone,name=player.name,player_status=player.player_status,user_id=user.id,position=player.position
    )
    session.add(new_player_db)
    session.commit()
    session.refresh(new_player_db)
    return new_player_db


@game.post('/start_my_game/{app_id}/{team_number}',status_code=201)
def my_game_box(session:session_db,app_id:str,team_number:int,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    game_db = start_game(session=session,user=user,app_id=app_id,team_number=team_number)

    return game_db

@game.post('/added_team',status_code=201)
def add_team_game(session:session_db,team:BuildTeam,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    data = relate_team_game(session=session,team=team,user=user)
    print(data)
    team_db = data['team_game']
    team_game= data['game_link']
    print('team game',team_game)
    register_players(session=session,teamr=team,teamdb=team_db)

    return team_db




@game.post('/request_team_player/{team_id}',status_code=201)
def req_team_join(session:session_db,team_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
     player_db = exist_player(session=session,team_id=UUID(team_id),user=user)
     if player_db:
        raise HTTPException(
            status_code=401,
            detail=f'You are already member of the team'
        )
     pl = user.player
     print('player',pl)
     pla_id = pl.id
     req = exist_req_team(session=session,team_id=UUID(team_id),user=user)
     team_db = session.get(Team,UUID(team_id))
     print(req,'req')
     if req:
         if req.status_req== 'denied':
            raise HTTPException(
                status_code=401,
                detail='Invalid request ,the coach refused previous req,try other game'
            
        )
         elif req.status_req== 'approved':
            raise HTTPException(
            status_code=401,
            detail='You Are already approved in previous request'
        )
         elif req.status_req=='pending':
            raise HTTPException(
             status_code=401,
             detail='You have a req under process'
         )
   
     req_new= ReqJoinTeam(
        team_id=UUID(team_id),status_req='pending',player_id=pla_id,requested_user_id=str(team_db.user_id)
    )
     session.add(req_new)
     session.commit()
     session.refresh(req_new)
     extra_payload={
         'team_id':team_id,
         'req_id':str(req_new.id)
         
     }
     publish_event_1(player_id=str(pla_id),extra_payload=extra_payload)
     extra_payload={'team_id':team_id}
     event_id = find_player(user=user,extra_payload=extra_payload)
     return req_new

@game.get('/my_team_reqs',status_code=200)
def get_my_team_reqs(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    reqs = session.exec(select(ReqJoinTeam).where((ReqJoinTeam.requested_user_id==str(user.id))&(ReqJoinTeam.status_req=='pending'))).all()
    reqs_recieved =[
        {
            'id':r.id,
            'player_id':r.player_id,
            'player_name':r.player.name,
            'player_position':r.player.position,
            'player_phone':r.player.phone,
            'user_id':r.player.user_id,
            'user':r.player.user,
            'status':r.status_req
        }
        for r in reqs
    ]
    print('reqs',reqs_recieved)
    return reqs_recieved 
@game.get('/my_pl_reqs',status_code=200)
def get_my_pl_reqs(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    player = session.exec(select(Player).where(Player.user_id==user.id)).first()
    
    reqs = session.exec(select(ReqJoinTeam).where(ReqJoinTeam.player_id==player.id)).all()
    reqs_recieved =[
        {
            'id':r.id,
            'player_id':r.player_id,
            'player_name':r.player.name,
            'player_position':r.player.position,
            'player_phone':r.player.phone,
            'user_id':r.player.user_id,
            'user':r.player.user,
            'status':r.status_req,
            'team':r.team.team_name,
            'coach':r.team.coach_name,
        }
        for r in reqs
    ]
    print('reqs',reqs_recieved)
    return reqs_recieved          

     

@game.post('/request_player_team/{team_id}/{id_game}',status_code=201)
def req_player_team(session:session_db,team_id:str,id_game:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    player_db = exist_player(session=session,team_id=UUID(team_id),user=user)
    if player_db:
        raise HTTPException(
            status_code=401,
            detail=f'You are already member of the team'
        )
    pl = user.player
    pla_id = pl.id
    req= exist_req(session=session,id_game=UUID(id_game),team_id=UUID(team_id),user=user)
    team_db = session.get(Team,UUID(team_id))
    print(req,'req')
    if req:
         if req.status_req== 'denied':
            raise HTTPException(
                status_code=401,
                detail='Invalid request ,the coach refused previous req,try other game'
            
        )
         elif req.status_req== 'approved':
            raise HTTPException(
            status_code=401,
            detail='You Are already approved in previous request'
        )
         elif req.status_req=='pending':
            raise HTTPException(
             status_code=401,
             detail='You have a req under process'
         )
   
    req_new= ReqJoinTeamGame(
        game_id=UUID(id_game),team_id=UUID(team_id),status_req='pending',player_id=pla_id,requested_user_id=str(team_db.user_id)
    )
    session.add(req_new)
    session.commit()
    session.refresh(req_new)
    extra_payload={
        'game_id':id_game,
        'team_id':team_id,

        'coach_id':req_new.requested_user_id
        
        
    }
    event_id = find_player(player_id=str(pla_id),extra_payload=extra_payload)
    return req_new


@game.get('/reqs_players',status_code=200)
def players_req(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    reqs = session.exec(select(ReqJoinTeamGame).where(ReqJoinTeamGame.requested_user_id==str(user.id))).all()
    print('reqs',reqs)
    req_players=[
        {
            'id':r.id,
            'requested':r.requested_user_id,
            'game_id':r.game_id,
            'team_id':r.team_id,
            'user_id':r.player_id,
            'player':r.player,
            'status':r.status_req
        }
        for r in reqs
    ]
    return req_players
    



@game.post('/approve_player_team/{req_id}',status_code=200)
def approve_player_team(session:session_db,req_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    req_db = session.get(ReqJoinTeam,UUID(req_id))
    req_db.status_req='approved'
    team_db = session.get(Team,req_db.team_id)
    team_db.confirmed_players=int(team_db.confirmed_players) +1
    
  
    player_team = TeamPlayer(team_id=req_db.team_id,player_id=req_db.player_id)
  
    session.add(player_team)
    session.commit()
    session.refresh(req_db)
    session.refresh(player_team)
    session.refresh(team_db)
    
    publish_response(req_id=str(req_id))
    return {
        'message':'Request Approved'
    }
@game.post('/deny_player_team/{req_id}',status_code=200)
def deny_player_team(session:session_db,req_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    req_db = session.get(ReqJoinTeam,UUID(req_id))
    req_db.status_req='denied'
    session.commit()
    session.refresh(req_db)
    publish_response(req_id=str(req_id))
    return {
        'message':'Request Denied'
    }

    


@game.post('/approve_player/{req_id}',status_code=200)
def approve_player(session:session_db,req_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    req_db = session.get(ReqJoinTeamGame,UUID(req_id))
    req_db.status_req='approved'
    team_db = session.get(Team,req_db.team_id)
    team_db.confirmed_players=int(team_db.confirmed_players) +1
    
  
    player_team = TeamPlayer(team_id=req_db.team_id,player_id=req_db.player_id)
  
    session.add(player_team)
    session.commit()
    session.refresh(req_db)
    session.refresh(player_team)
    session.refresh(team_db)
    return {
        'message':'Request Approved'
    }
@game.post('/deny_player/{req_id}',status_code=200)
def deny_player(session:session_db,req_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    req_db = session.get(ReqJoinTeamGame,UUID(req_id))
    req_db.status_req='denied'
    session.commit()
    session.refresh(req_db)
    return {
        'message':'Request Denied'
    }

    

   



    





    



@game.post('/add_exist_team/{id_game}/{team_id}',status_code=201)
def add_existing_team(session:session_db,team_id:str,id_game:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    
    print(team_id,'teamid',id_game,'idg')
    team = session.get(Team,UUID(team_id))
    game = session.get(Game,UUID(id_game))
    if user.id != team.user_id:
        raise HTTPException(
            status_code=404,
            detail='User invalid'
        )
    team_game =GameTeam(
        game_id=game.id,
        team_id = team.id
    )
    session.add(team_game)
    session.commit()
    session.refresh(team_game)
    return team_game

@game.get('/my_teams',status_code=200)
def get_teams_registred(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    my_teams = session.exec(select(Team).where(Team.user_id==user.id if Team.user else Team.user_field_id==user.id)).first()
    print('teams my',my_teams)


    my_team ={
        'id':my_teams.id,
        'team_name':my_teams.team_name,
        'coach_name':my_teams.coach_name,
        'user_id' :my_teams.user_id if my_teams.user else my_teams.user_field_id
    }
  
    print(my_team,my_team['user_id'])
    return my_team
     



@game.get('/my_games',status_code=200)
def my_g(session:session_db):
    game  = session.exec(select(Game)).all()
    print('g',game)
    pend_games = [
       
        {
            'id':g.id,
            'date':g.date,
            'time':g.time,
            'status':g.status,
            'teams':g.teams,
            'user':g.user if g.user else g.user_field,
            'user_id':g.user_id if g.user_id else g.user_field_id,
            'field':g.field,
            'field_id':g.field
            

        }
       

        for g in game
    ]
    print('pend',pend_games)
    return pend_games
@game.get('/my_games_confirmed',status_code=200)
def my_g(session:session_db):
    game  = session.exec(select(Game.status=='confirmed')).all()
    pend_games = [
        {
            'id':g.id,
            'date':g.date,
            'time':g.time,

        }
        for g in game
    ]
    return pend_games

@game.post('/register_team',status_code=201)
def register_team(session:session_db,team:BuildTeam,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    
    team_db=create_team(session=session,user=user,team=team)
   

    
    
    print('team_db',team_db)
   

    
   
    
    return team_db


@game.get('/teams_registred',status_code=200)
def teams_in_box(session:session_db):
    
    teams = session.exec(select(Team).options(selectinload(Team.memberships))).all()

    
   

    teams_returned=[
        {
            'id':t.id,
            'coach':t.coach_name,
            'coach_id':t.coach_id,
            'coach_email':t.coach_email,
            'team_name':t.team_name,
            
            'user_id':t.user_id if t.user else t.user_field,
            'status_team':t.status,
            
        
            
            'user': t.user if t.user else t.user_field ,
            'members':[


                {
                    'id':m.id,
                    'player_name':m.player.name,
                    'position':m.player.position,
                    'status':m.status,


                }
                for m in t.memberships 
            ]
           
       




            
        }
        for t in teams
    ]
    print('team',teams_returned)
    return teams_returned
@game.get('/players',status_code=200)
def get_players(session:session_db):
    players= session.exec(select(Player)).all()
    print('players',players)
    players_db =[
        {
            'id':p.id,
            'name':p.name,
            'phone':p.phone,
            'user':p.user,
            'user_id':p.user_id
        }
        for p in players
    ]
    return players_db


@game.get('my_players',status_code=200)
def get_my_players(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    pass


@game.get('/game_team_link',status_code=200)
def teamGame(session:session_db):
    print('endpoint exist')
    games_teams = session.exec(select(GameTeam)).all()
    print('ggg',games_teams)
    games_t = [
        {
            'id':f.id,
            'game_id':f.game_id,
            'team_id':f.team_id
        }
        for f in games_teams
    ]
    return games_t

@game.post('/confirm_game/{game_id}',status_code=201)
def complete_the_game(session:session_db,game_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    game_db = session.get(Game,UUID(game_id))
    if not game_db:
        raise HTTPException(
            status_code=404,
            detail='Game not found'
        )
    game_db.status='confirmed'
    session.commit()
    session.refresh(game_db)
    return {
        'message':f'Game confirmed on {game_db.date} at {game_db.time} '
    }

@game.post('/request_team_no_game',status_code=201)
def request_team_n_game(session:session_db):
    pass



@game.post('/request_team_member/{team_id}',status_code=201)
def request_member_ship(session:session_db,team_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    team = session.get(Team,UUID(team_id))
    player = session.exec(select(Player).where(Player.user_id==user.id if Player.user else Player.user_field_id==user.id)).first()
    new_membership = MemberShip(player_id=player.id,team_id=UUID(team_id),status='pending',description='join team request')
    sender_id = team.user_id
    session.add(new_membership)
    session.commit()
    session.refresh(new_membership)
    data = {
        'message':f'Your Request sent to {team.team_name} '
    }
    if new_membership.id is not None:
        notification = notify(session=session,sender_id=str(user.id),user_id=str(sender_id),ref_id=str(team.id),read=False,type=f'{player.name} sent a request to join your Team {team.team_name}')
        print(notification.id)
        return data 


@game.get('/membership_reqs',status_code=200)
def my_memberships(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
  
    reqs = session.exec(select(MemberShip)).all()

    reqs_sent=[
        {
            'id':r.id,
            'team_id':r.team_id,
            'player_id':r.player_id,
             'player':r.player,
             'player_name':r.player.name,
             'position':r.player.position,
             'team':r.team,
             'status':r.status,
             
        }
        for r in reqs
    ]
    print(reqs_sent)
    return reqs_sent

@game.get('/memberships_invitations',status_code=200)
def my_invitations(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    player = session.exec(select(Player).where(Player.user_id==user.id)).first()
    print(player,'player')
    if player is None and player.id is None:
        raise HTTPException(
            status_code=401,
            detail='Invlaid reqs'
        )
    memberships = session.exec(select(MemberShip).where((MemberShip.description=='player invitation')&(MemberShip.player_id==player.id))).all()

    invitations = [
        {
            'id':m.id,
            'player_id':m.player_id,
            'team_id':m.team_id,
            'status':m.status,
            'team':m.team
            
        }
        for m in memberships
    ]
    print(invitations,'invitation')
    return invitations


@game.get('/memberships',status_code=200)
def my_memberships(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
   
    reqs = session.exec(select(MemberShip).where(MemberShip.status=='active')).all()

    reqs_sent=[
        {
            'id':r.id,
            'team_id':r.team_id,
            'player_id':r.player_id,
             'player':r.player,
             'team':r.team,
             'status':r.status,
             
        }
        for r in reqs
    ]
    print(reqs_sent)
    return reqs_sent

@game.post('/approve_memberships/{member_id}',status_code=201)
def approve_player_member(session:session_db,member_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    member = session.get(MemberShip,UUID(member_id))
    print('member.player',member.player.name)
    if member is None:
        raise HTTPException(
            status_code=404,
            detail='Member request does not exist'
        )
    team =member.team
    team_id = member.team_id
    player = member.player

    reciever_id = player.user_id
    member.status='active'
    session.commit()
    session.refresh(member)
    print(member.status,'status')
    if member.status=='active':
         notification = notify(session=session,sender_id=str(user.id),user_id=str(reciever_id),ref_id=str(team_id),read=False,type=f'{team.team_name} accepted your request')
         print(notification.id)
    data = {
        'message':'Player request approved'
    }
    return data

@game.post('/deny_memberships/{member_id}',status_code=201)
def deny_player_member(session:session_db,member_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    member = session.get(MemberShip,UUID(member_id))
    if member is None:
        raise HTTPException(
            status_code=404,
            detail='Member request does not exist'
        )
    team =member.team
    team_id = member.team_id
    player = member.player

    reciever_id = player.user_id
    member.status='denied'
    session.commit()
    session.refresh(member)
    if member.status=='denied':
         notification = notify(session=session,sender_id=str(user.id),user_id=str(reciever_id),ref_id=str(team_id),read=False,type=f'{team.team_name} denied your request')
         print(notification.id)

   
    data = {
        'message':'Player request denied'
    }
    return data

@game.post('/invite_player/{player_id}',status_code=201)
def invite_player_team(session:session_db,player_id:str,user:Annotated[User,UserField,Depends(get_current_active_user)]):
    player = session.get(Player,UUID(player_id))
    print(player,'player')
    team = session.exec(select(Team).where(Team.user_id==user.id if Team.user else Team.user_field_id==user.id)).first()
    print('team',team)
    if team is  None or player is  None:
        raise HTTPException(
            status_code=401,
            detail='invalid request'
        )
    reciever_id = player.user_id
    new_membership = MemberShip(team_id=team.id,player_id=UUID(player_id),status='pending invitation',description='player invitation')
    session.add(new_membership)
    session.commit()
    session.refresh(new_membership)
    if new_membership.id is not None:
        notification = notify(session=session,sender_id=str(user.id),user_id=str(reciever_id),ref_id=str(team.id),read=False,type='sending request')
        print(notification.id)
        

    data= {
        'message':f'Invitation to Player {player.name} to join {team.team_name} sent'
    }
    return data
  

@game.post('/approve_membership_invitation/{member_id}',status_code=201)
def approve_team_invitation(session:session_db,member_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    member = session.get(MemberShip,UUID(member_id))
    print('member.player',member.player.name)
    if member is None:
        raise HTTPException(
            status_code=404,
            detail='Member request does not exist'
        )
    member.status='active'
    player=member.player.name
    team =member.team
    team_id = team.id 
    reciever_id = team.user_id
    member.status='active'
    session.commit()
    session.refresh(member)
    if member.status=='active':
         notification = notify(session=session,sender_id=str(user.id),user_id=str(reciever_id),ref_id=str(team_id),read=False,type='request approve')
         print(notification.id)

    data = {
        'message':f'Player {player} accepted Invitation'
    }
    return data

@game.post('/deny_membership_invitation/{member_id}',status_code=201)
def deny_team_invitation(session:session_db,member_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    member = session.get(MemberShip,UUID(member_id))
    if member is None:
        raise HTTPException(
            status_code=404,
            detail='Member request does not exist'
        )
    member.status='denied'
    player = member.player.name
    team =member.team
    team_id = team.id 
    reciever_id = team.user_id
    session.commit()
    session.refresh(member)
    if member.status=='denied':
         notification = notify(session=session,sender_id=str(user.id),user_id=str(reciever_id),ref_id=str(team_id),read=False,type='request deny')
         print(notification.id)
    data = {
        'message':f'Player {player} denied Invitation'
    }
    return data


@game.get('/notifications',status_code=200)
def notifications_me(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    notifications= session.exec(select(Notification).where((Notification.user_id==user.id)&(Notification.is_read==False))).all()
    recieved_notifications=[
        {
            'id':n.id,
            'user_id':n.user_id,
            'sender_id':n.sender_id,
            'ref_id':n.reference_id,
            'type':n.type,

        }
        for n in notifications
    ]
    print(recieved_notifications,'recieved')
    return recieved_notifications 


@game.post('/clear_notification/{note_id}',status_code=201)
def read_note(session:session_db,note_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):

    note = session.get(Notification,UUID(note_id))
    if note is not None:
        note.is_read=True 

    session.commit()
    session.refresh(note) 
    data ={
        'message':'not cleared'
    }
    return data 

@game.post('/join_team_req/{team_id}/{game_id}',status_code=201)
def game_join_req(session:session_db,game_id:str,team_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    game = session.get(Game,UUID(game_id))
    team = session.get(Team,UUID(team_id))
    reciever_id = game.user_id
    new_team_game= GameTeam(team_id=UUID(team_id),game_id=UUID(game_id),status='pending')
    new_reqs = RequestGameJoin(status='pending',team_id=UUID(team_id),game_id=UUID(game_id),user_id=user.id if User else None,user_field_id=user.id if UserField else None)
    session.add(new_reqs)
    session.add(new_team_game) 
    session.commit()
    session.refresh(new_reqs)
    session.refresh(new_team_game)
    if new_team_game.id is not None and new_reqs.id is not None:
        notification  = notify(session=session,user_id=str(reciever_id),sender_id=str(user.id),ref_id=game_id,read=False,type=f'Coach {team.coach_name} of {team.team_name} sent a request to join your game') 
        print(notification.id)
    data ={
        'message':'Request to join Game sent'
    }
    return data

@game.post('/approve_link_request/{id_req}',status_code=201)
def approve_link(session:session_db,id_req:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    print(user.register_as,'user role')
  
    req_app = session.get(RequestGameJoin,UUID(id_req))
    id_game = req_app.game_id 
    id_team= req_app.team_id
    team = req_app.team
    reciever_id = team.user_id
    game_app = session.exec(select(GameTeam).where((GameTeam.team_id==id_team)& (GameTeam.game_id==id_game))).first()
   
    req_app.status='confirmed'
    print(game_app)
    game_app.status='confirmed link'
    session.commit()
    session.refresh(game_app)
    session.refresh(req_app)
    if req_app.status=='confirmed':
                notification  = notify(session=session,user_id=str(reciever_id),sender_id=str(user.id),
                                       ref_id=str(id_game),read=False,
                                       type=f'Your Request to Join the game accepted') 
                print(notification.id,'id note')

    return {
        'message':'approved request'
    }
@game.post('/deny_link_request/{req_id}',status_code=201)
def deny_link(session:session_db,req_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
   
    req_app = session.get(RequestGameJoin,UUID(req_id))
    id_game = req_app.game_id 
    id_team= req_app.team_id
    team = req_app.team
    reciever_id = team.user_id
    game_app = session.exec(select(GameTeam).where((GameTeam.team_id==id_team)& (GameTeam.game_id==id_game))).first()
    req_app.status='denied'
    game_app.status='denied link'
    session.commit()
 
    session.refresh(req_app)
    session.refresh(game_app)
    if req_app.status=='denied':
                notification  = notify(session=session,user_id=str(reciever_id),sender_id=str(user.id),
                                       ref_id=str(id_game),read=False,
                                       type=f'Your Request to Join the game denied') 
                print(notification.id,'id note')
    return {
        'message':'denied request'
    }

@game.get('/get_my_games',status_code=200)
def get_my_games(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    my_games = session.exec(select(Game)).all()
    my_games_on = [
        {
            'id':g.id,
            'date':g.date,
            'time':g.time,
            'status':g.status,
            'team_number':g.players_per_team,
            'teams':g.teams,
            'user':g.user if g.user else g.user_field,
            'user_id':g.user_id if g.user_id else g.user_field_id,
            'field':g.field
           
        }
        for g in my_games
    ]
    return my_games_on


@game.get('/my_requests_sent',status_code=200)
def my_requests_owner(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    
    reqs = session.exec(select(RequestGameJoin)).all()
    
    print(reqs,'reqssss')
    if not user:
        raise HTTPException(
            status_code=401,
            detail ='invalid'
        )
    
    my_reqs=[
        {
            'id':r.id,
            'game_id':r.game_id,
            'user_id':r.user_id if r.user else r.user_field_id,
            'user':r.user if r.user else r.user_field,
             'team_id':r.team_id,
             'team':r.team,
             'status':r.status
        }

        for r in reqs
    ]
    print('my reqs',my_reqs)
    return my_reqs

@game.get('/game_team_confirmed',status_code=200)
def game_link(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):

    approved_game_link = session.exec(select(GameTeam).where(GameTeam.status=='confirmed link')).all()
    approved_game_team = [
        {
            'id':l.id,
            'team_id':l.team_id,
            'game_id':l.game_id,
            'status':l.status
        }
        for l in approved_game_link
    ]
    return approved_game_team



@game.get('/my_teams_searched/{team_id}',status_code=200)
def my_team_searched(session:session_db,team_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    team = session.exec(select(Team).where(Team.id==UUID(team_id)).options(selectinload(Team.memberships),selectinload(Team.games))).first()


    team_req= {
        'id':team.id,
        'team_name':team.team_name,
        'coach':team.coach_name,
        'members':[
            {
                'id':m.id,
                'member':m.player.name,


            }
            for m in team.memberships
            if m.status=='active'

        ],
        'games':[

        ]
    }
    return team_req


@game.get('/player_profile',status_code=201)
def my_player_profiel(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    player = session.exec(select(Player).where(Player.user_id==user.id)).first()

    i_am_player={
        'id':player.id,
        'name':player.name,
        'phone':player.phone,
        'position':player.position
    }


    return i_am_player


@game.get('/player_by_id/{player_id}',status_code=200)
def player_id_data(session:session_db,player_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    player = session.exec(select(Player).where(Player.id==UUID(player_id)).options(selectinload(Player.memberships),selectinload(Player.stats))).first()
    player_by_id={
        'id':player.id,
        'name':player.name,
        'phone':player.phone,
        'position':player.position,
        'memberships':[],
        'stats':[]
    }
    return player_by_id




@game.post('/completed_game/{game_id}',status_code=201)
def game_completed(session:session_db,game_id:str):
    game_state_tracker(session=session,game_id=game_id)

    return {
        'message':'Status updated'
    }
    



