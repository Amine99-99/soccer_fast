from .models import Player,Game,GameTeam,UserField,Court,CourtRegister,Fields,FieldsRegister,Appointment,AppointmentRegister,AppointmentBase,User,BuildTeam,Team,PlayersRegister
from .core.debs import session_db
from sqlmodel import select
from typing import List
from fastapi import UploadFile,HTTPException
import uuid
from uuid import UUID
import os
from .models import Invoice,AppointmentOwner,AppointmentRegisterOwner,AppointmentRegisterUpdate,Transfer,RequestTransfer
from sqlalchemy.orm import selectinload
from decimal import Decimal 
from datetime import datetime



def create_invoice_app(ref_id:UUID,amount:Decimal,due_date:datetime,payer_field_id:UUID|None=None,payer_id:UUID|None=None,payee_field_id:UUID|None=None):
    today = datetime.now().date()





    return Invoice(appointment_id=ref_id,amount=amount,status='pending',issue_date=today,
                   due_date=due_date,payer_id=payer_id,payee_field_id=payee_field_id)

async def create_courts_pictures(images:List[UploadFile]):
    paths=[]
    os.makedirs('./courts_photo',exist_ok=True)
    for image in images:
        filename=f"{uuid.uuid4()}_{image.filename}"
        file_path=f"./courts_photo/{filename}"
        contents = await image.read()
        with open(file_path,"wb") as f:
            f.write(contents)
      
        paths.append(file_path)
    return paths

def get_field(session:session_db,field:FieldsRegister,user:UserField):
    field = select(Fields).where((Fields.address==field.address) & (Fields.city== field.city) & (Fields.postal_code==field.postal_code)&(Fields.user_field_id==user.id))
    field_db = session.exec(field).first()
   
    return field_db

    
def get_courts(session:session_db,user:UserField)->List[Court]:
    field = select(Fields).where(Fields.user_field_id==user.id)
    fields_db = session.exec(field).first()
    if fields_db:
       courts = fields_db.courts
       return courts
   
def serialize_court(court:CourtRegister)->dict:
    print('court',court)
  
    data = court.model_dump()
  
    data['start_hour']=data['start_hour'].isoformat()
    data['end_hour'] = data['end_hour'].isoformat()
    data['type_of_court'] = str(data['type_of_court'])
    data['session_time'] = int(data['session_time'])
    return data
    
def create_courts(session:session_db,field:FieldsRegister,user:UserField)->Court:
    
  
    
   
      
    field_db=Fields(status='pending',is_active=False,user_field_id=user.id,field_name=field.field_name,address=field.address,city=field.city,postal_code=field.postal_code)
       
    session.add(field_db)
    session.commit()

    session.refresh(field_db)
    print('field_d',field_db,field_db.id)

   
    return field_db
def create_courts_x(session:session_db,field:FieldsRegister,user:UserField):
    field_db_1 = get_field(session=session,field=field,user=user)
    if field_db_1:
        raise HTTPException(
            status_code =404,
            detail='Field alreadcy registred'
        )
  

    field_db = create_courts(session=session,field=field,user=user)
    field_id = field_db.id
    courts  = [c for c in  field.courts]
    new_courts=[]

    for c in courts :
        new_court=Court(type_of_court=c.type_of_court,opening_days=c.opening_days,start_hour=c.start_hour,end_hour=c.end_hour,
                        session_time=c.session_time,court_size=c.court_size,session_price=c.session_price,field_id=field_id)
        
        session.add(new_court)
        new_courts.append(new_court)
    session.commit()
    for c in new_courts:
        session.refresh(c)
    return {'new_courts':new_courts,'field_db':field_db}









            
        
        
def is_user_booked(session:session_db,appointment:AppointmentRegister,user:User|UserField):

    field_db = session.exec(select(Fields).where(Fields.id==UUID(appointment.field_id)).options(selectinload(Fields.appointments))).first()
    appointments_db = field_db.appointments 
    print('appointments',appointments_db)
    for a in appointments_db:
        print('a',a)
      
        if str(a.time) ==str(appointment.time) and str(a.date)==str(appointment.date) and a.court_id==appointment.court_id and (a.user_id ==user.id if a.user_id else a.user_field_id==user.id):
            return False 
    return True 

def is_three_appointments(session:session_db,appointment:AppointmentRegister):
    field_db = session.exec(select(Fields).where(Fields.id==UUID(appointment.field_id)).options(selectinload(Fields.appointments))).first()

    three_appointments=[]
    appointments_db = field_db.appointments 
    for a in appointments_db:
         if str(a.time) ==str(appointment.time) and str(a.date)==str(appointment.date) and a.court_id==appointment.court_id and(a.status=='pending' or a.status=='transfered'):
             three_appointments.append(a)
    if len(three_appointments)>=3:
        return False 
    return True


def get_confirmed_appointment(session:session_db,appointment:AppointmentRegister):

    field_db = session.exec(select(Fields).where(Fields.id==UUID(appointment.field_id)).options(selectinload(Fields.courts),selectinload(Fields.appointments))).first()
    print('court_id',appointment.court_id)
    courts = field_db.courts
    court_app = next((court for court in courts if court.id == appointment.court_id),None)
    if court_app is None:
        raise HTTPException(
            status_code=400,
            detail='court not registred to the field'
        )
    appointments_db = field_db.appointments
    app_owner_db=field_db.owner_appointments
    
    apps=[]
    for app in appointments_db:
       

        if  str(app.time)==str(appointment.time) and str(app.date)==str(appointment.date) and app.court_id==appointment.court_id and app.status=='approved':
            apps.append(appointment)

    for app in app_owner_db:
        if  str(app.time)==str(appointment.time) and str(app.date)==str(appointment.date) and app.court_id==appointment.court_id  :
            apps.append(appointment)
        
    app_db= apps[0] if len(apps)==1 else None
           

            
        
        
    return app_db




    
    
def create_appointment(session:session_db,appointment:AppointmentRegister,user:UserField|User)->Appointment:
    app_db = get_confirmed_appointment(session=session,appointment=appointment)
    print(app_db,'app_db')
    if app_db:
        raise HTTPException(
            status_code=403,
            detail='Slot is reserved'
        )
   
    if not is_user_booked(session=session,appointment=appointment,user=user):
        raise HTTPException(
            status_code=409,
            detail=f'{user.username} Already you have an appointment in this time slot'
        )
        
        
    if not is_three_appointments(session=session,appointment=appointment):
        raise HTTPException(
            status_code=409,
            detail='Time slot already booked'
        )
    field  = session.get(Fields,UUID(appointment.field_id))

    if isinstance(user,User):
        app_base = Appointment.model_validate(appointment,update={'user_id':user.id,'user_field_id':None,'field_id':UUID(appointment.field_id),'court_id':appointment.court_id,'status':'pending','game_id':None})

    elif isinstance(user,UserField):
        app_base = Appointment.model_validate(appointment,update={'user_id':None,'user_field_id':user.id,'field_id':UUID(appointment.field_id),'court_id':appointment.court_id,'status':'pending' ,'game_id':None})
    
    session.add(app_base)
    session.flush()
    new_app_invoice = create_invoice_app(ref_id=app_base.id,amount=app_base.amount,due_date=datetime.now(),payer_field_id=user.id if app_base.user_field else None,payee_field_id=field.user_field_id,payer_id=user.id if app_base.user else None)
    session.add(new_app_invoice)
    session.commit()
    session.refresh(new_app_invoice)
    session.refresh(app_base)
    print(app_base.payment_method,'method',app_base)
    print(new_app_invoice,'invoice')


   
    data= {
        'message':'Successfully Booked',
        'invoice_id':new_app_invoice.id,
        'payment_method':app_base.payment_method
    }
    print(data,'data')
    return data
    




def register_players(teamr:BuildTeam,session:session_db,teamdb:Team):
    players_come = [player_team for player_team in teamr.players ] 
    added_to_db=[]
    for pl in players_come:
        existing_user = session.exec(select(User).where(User.phone==pl.phone)).first()
        existing_player = session.exec(select(Player).where(Player.phone==pl.phone)).first()
        if existing_player:
            player_db=existing_player 
     
        else:
            player_db=Player(position=pl.position,phone=existing_user.phone if existing_user else pl.phone ,name= existing_user.username if existing_user else pl.name,player_status=pl.player_status,user_id=existing_user.id if existing_user else None )

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


def unique_team(session:session_db,team:BuildTeam):
    exist_team = session.exec(select(Team).where(Team.coach_name==team.coach_name)).first()
    return exist_team

def create_team(session:session_db,team:BuildTeam,user:UserField|User):
    exist_team = unique_team(session=session,team=team)
    if exist_team is not None:
        raise HTTPException(
            status_code=401,
            detail=f'Coach {team.coach_name} You Have a Team registred'
        )
    
   
    

   
   
    if isinstance(user,User):
        team_db = Team(coach_name=team.coach_name,coach_id=str(user.id),coach_email=user.email,
                      
                      
                       team_name=team.team_name,
                      
                       status_team='registred team',
                       user_id=user.id,
                       user_field_id=None,
                       
                       
                       
                       
                       
                       
                       
                       )
        games = session.exec(select(Game).where((Game.user_id==user.id)&(Game.status=='pending'))).all()
       

    elif isinstance(user,UserField):
      team_db = Team(coach_name=team.coach_name,coach_id=str(user.id)
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     ,coach_email=user.email,
                
                       team_name=team.team_name,
                      
                       status_team='registred team',
                       user_id=None,
                       user_field_id=user.id,
                       )
      games = session.exec(select(Game).where((Game.user_id==user.id)&(Game.status=='pending'))).all()

      

    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    games_team=[]
    if games is not None:
        team_id = team_db.id
        for game in games:
            game_id=game.id
            game_team=GameTeam(game_id=game_id,team_id=team_id)
            session.add(game_team)
            games_team.append(game_team)
        session.commit()
        for game in games_team:
            session.refresh(game)
        


    

    print('teams',team_db)
    team_out = team_db.model_dump()
    print(team_out,'out')
 
    return team_out

def relate_team_game(session:session_db,team:BuildTeam,user:User|UserField):
    game = session.get(Game,UUID(team.game_id))
    print('game',game)
    team_added = create_team(session=session,team=team,user=user)
    print('team added')
    if not team_added:
        raise HTTPException(
            status_code=404,
            detail='Team not registred'
        )
    game_team = GameTeam(team_id=team_added['id'],game_id=game.id)
    session.add(game_team)
    session.commit()
    session.refresh(game_team)
    return {
        'team_game':team_added,'game_link':game_team
    }
    
    


def get_registred_app(session:session_db,appointment:AppointmentRegisterOwner,user:UserField):
    field_db = session.get(Fields,UUID(appointment.id_field))
    print('court_id',appointment.court_id)
    courts = field_db.courts 
    court_app = next((court for court in courts if court["id"] == appointment.court_id),None)
    if court_app is None:
        raise HTTPException(
            status_code=400,
            detail='court not registred to the field'
        )
    appointments_db = field_db.appointments
    app_owner_db = field_db.owner_appointments
    
    
    apps=[]
    for app in appointments_db:
       

        if  app.time==appointment.time and app.date==appointment.date and app.court_id==appointment.court_id and app.status=='approved' :
            apps.append(appointment)
        
   
    for app in app_owner_db:
        if  app.time==appointment.time and app.date==appointment.date and app.court_id==appointment.court_id  :
            apps.append(appointment)

    app_db= apps[0] if len(apps)==1 else None
    return app_db
def get_registred_trans(session:session_db,appointment:AppointmentRegisterUpdate):
    field_db = session.get(Fields,UUID(appointment.field_id))
    print('court_id',appointment.court_id)
    courts = field_db.courts 
    court_app = next((court for court in courts if court["id"] == appointment.court_id),None)
    if court_app is None:
        raise HTTPException(
            status_code=400,
            detail='court not registred to the field'
        )
    appointments_db = field_db.appointments
    app_owner_db = field_db.owner_appointments
    
    
    apps=[]
    for app in appointments_db:
       

        if  app.time==appointment.time and app.date==appointment.date and app.court_id==appointment.court_id and app.status=='approved' :
            apps.append(appointment)
        
   
    for app in app_owner_db:
        if  app.time==appointment.time and app.date==appointment.date and app.court_id==appointment.court_id  :
            apps.append(appointment)

    app_db= apps[0] if len(apps)==1 else None
    return app_db


def field_owner_book(session:session_db,appointment:AppointmentRegisterOwner,user:UserField):
    app_db = get_registred_app(session=session,appointment=appointment,user=user)
    if app_db:
        raise HTTPException(
            status_code=401,
            detail='Invlaid date and time,Already booked'
        )
    
    new_app_db  = AppointmentOwner.model_validate(appointment,update=({
        'user_field_id':user.id,'field_id':appointment.id_field,'status':'confirmed'
    }))
    session.add(new_app_db)
    session.commit()
    session.refresh(new_app_db)

    return new_app_db




def transfer_appointment(session:session_db,trans:Transfer,user:UserField):
    app_db = session.get(Appointment,UUID(trans.app_id))
    if app_db is None:
        raise HTTPException(
            status_code=404,
            detail='Invalid Appointment '
        )
    

    app_db.date=trans.date
    app_db.time=trans.time 
    app_db.status='transfered'
    trans_req = RequestTransfer(user_field_id=user.id,user_id=None,app_id=trans.app_id,status_req='pending',user_requested_id=str(app_db.user_id))
    session.add(trans_req)
    session.commit()
    session.refresh(app_db)
    session.refresh(trans_req)

    if app_db.status=='transfered' and trans_req.id is not None:
        return {
            'message':'Transfer Appointment  Request Successfully Sent '
        }


def approve_appointment(session:session_db,app_id:str,user:UserField):
    if not user:
            raise HTTPException(
                status_code=401,
                detail='Unauhtorised User'
            )
    apps = session.get(Appointment,UUID(app_id))
    print('apps stats',apps.status)
    if apps.status =='approved':
        raise HTTPException(
            status_code=401,
            detail='invalid appointment to approve'
    
            )
    apps.status = 'approved'
        #generate_invoice()
    session.commit()
    
        
    return  {'message':'approved appointment'}
    


 
  
                       
                       
                       
                       
                       
                       
     










    

