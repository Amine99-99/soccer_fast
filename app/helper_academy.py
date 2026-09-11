from .models import Academy,AcademyRegister,AcademyCategory,User,SubscriptionRegister,SubscriptionPlan,Subscription,Fields,SessionApp,ProgramAcademy
from .core.debs import session_db
from sqlmodel import select
from fastapi import HTTPException
from uuid import UUID
from datetime import date,timedelta,datetime
from sqlalchemy.orm import selectinload
from .helper_1 import register_parent
from .models import ParentRegister,KidsRegister,EnrollementAcademy,KidAcademy,UserField,MemberAcademy,InvoiceNotify
from .helper_stat import notify
from .helper_subscription import is_slot_available,availabilty_ratio
from .scheduler import generate_invoice_subscription






def registred_academy(session:session_db,academy_register:AcademyRegister):
    academy = session.exec(select(Academy).where(Academy.name==academy_register.name)).first()
    return academy 


def create_academy(session:session_db,user:User,academy:AcademyRegister):
    academy_db  = registred_academy(session=session,academy_register=academy)
    if academy_db :
        raise HTTPException(
            status_code=401,
            detail='Academy with this name exist'
        ) 
    programs=[]
    program = [cat.model_dump() for cat in academy.programs ]
    print(program,'category')
    new_academy = Academy(name=academy.name,user_id=user.id,city=academy.city,description=academy.description,
                          logo=academy.logo,address=academy.address,status='active')
    session.add(new_academy)
    session.flush()
    academy_id= new_academy.id
    for cat in academy.programs:
        new_program = ProgramAcademy(name=cat.name,training_focus=cat.training_focus,training_level=cat.training_level,description=cat.description_program,min_age=cat.min_age,max_age=cat.max_age,gender=cat.gender,amount_fee_period=cat.amount_fee,billing_cycle=cat.billing_cycle,max_players=cat.max_players,status='active',academy_id=academy_id,coach_id=user.id)
        session.add(new_program)
        programs.append(new_program)

    
    session.commit()
    session.refresh(new_academy)
    for cat in programs:
        session.refresh(cat)
    return new_academy


def registred_subscription(session:session_db,sub:SubscriptionRegister):
    sub = session.exec(select(Subscription).where((Subscription.start_date==sub.start_date)&(Subscription.end_date==sub.end_date)&(Subscription.court_id==UUID(sub.court_id)))).first()
    return sub 



def create_subscription(session:session_db,sub:SubscriptionRegister,user:User):
    
    number_of_sessions = sub.amounts.number_of_sessions
    amount_session = sub.amounts.amount_session 
    total_amount = sub.amounts.total_amount 
    amount_per_period = sub.amounts.amount_per_period
    bill_cycle= sub.schedule.billing_cycle
    days_of_week = [d.model_dump()  for d in sub.schedule.days_of_week]
    new_sub = Subscription(total_amount=total_amount,amount_per_period=amount_per_period,amount_session=amount_session,billing_cycle=bill_cycle,program_id=sub.program_id,academy_id=sub.academy_id,start_date=sub.start_date,end_date=sub.end_date,duration=sub.duration,days_of_week=days_of_week,number_of_sessions=number_of_sessions,
                           user_id=user.id,field_id=sub.field_id,court_id=sub.court_id,status='pending',plan_id=sub.plan_id)
    
    return new_sub
    
 



DAY_MAP={
    'Monday':0,
    'Tuesday':1,
    'Wednesday':2,
    'Thursday':3,
    'Friday':4,
    'Saturday':5,
    'Sunday':6
}

def generate_sessions(session:session_db,sub:SubscriptionRegister,user:User):
    subscription =create_subscription(session=session,sub=sub,user=user)
    field_db = session.get(Fields,sub.field_id)
    if field_db is None:
        raise HTTPException(
            status_code=404,
            detail='Field not found'
        )
    program = session.get(ProgramAcademy,sub.program_id)
    if program is None :
        raise HTTPException(
            status_code=404,
            detail='Program not found'
        )
    program.start_date =sub.start_date 
    program.end_date=sub.end_date 
    

    session.add(subscription)
    session.flush()
    sessions_db=[]
    approved_slot=[]
    print('court_id',sub.court_id)
    
    days_of_week = [d for d in sub.schedule.days_of_week]
    current_date=sub.start_date
    end_date= sub.end_date 
 
    while current_date<end_date:
        
        for d in days_of_week:
           time_session =  datetime.strptime(d.session_start, "%H:%M").time()
           print('time session',d.session_start,current_date,'d',d.day_of_week)

           if current_date.weekday()==DAY_MAP[d.day_of_week]:
                available= is_slot_available(field_id=sub.field_id,court_id=sub.court_id,date=current_date,time=d.session_start,session=session) 
                print(available)
                
                   
                 

              
                   
                new_session=SessionApp(date=current_date,time=time_session,status='available' if available is True else 'not available',subscription_id=subscription.id,court_id=sub.court_id,field_id=sub.field_id)
                session.add(new_session)
                sessions_db.append(new_session)
                if new_session.status=='not available':
                    approved_slot.append(new_session)
    
                                  
                
        current_date = current_date+timedelta(days=1)
    print(approved_slot,'approved slot')
    print(len(approved_slot)/len(sessions_db),'ratio')
    data = availabilty_ratio(sessions_generated=sessions_db,conflicts_sessions=approved_slot,period=subscription.duration,sub_id=subscription.id)
    print('conf',data['conflicts_sessions'],'data',data)
    if len(data['conflicts_sessions'])==0:
        generate_invoice_subscription(sub_id=subscription.id,session=session,user=user)
    
    
       
  
  
    session.commit()
  
      
     
    return data


def academy_enroll(session:session_db,enroll:EnrollementAcademy):
    program= session.get(ProgramAcademy,enroll.kids_enroll.program_id)
    if program is None :
      
         raise HTTPException(
            status_code=404,
            detail='Program Not Found '
        )
    academy_db =session.get(Academy,enroll.kids_enroll.academy_id)
    if   program.academy_id!= enroll.kids_enroll.academy_id:
         raise HTTPException(
            status_code=400,
            detail=f'Program does not belong to the academy{academy_db.name}'
        )
       
        
   

    parent =register_parent(session=session,parent=enroll.parent_account)
    session.add(parent)
    session.flush
    parent_id=parent.id
    
    if parent is None and parent_id is None:
        raise HTTPException(
            status_code=404,
            detail='Invalid Parent Account'
        )
    kids_enroll = [kid for kid in enroll.kids_enroll.kids]
  
   

    enrolls=[]
    members=[]
    academy_db =session.get(Academy,enroll.kids_enroll.academy_id)
   
    coach_id=academy_db.user_id
    
  
  

    for k in kids_enroll:
        days_enroll = [d.model_dump() for d in k.days_session]
        session_number= len(days_enroll)
        new_kid=KidAcademy(birth_date=k.birth_date,first_name=k.name,last_name=k.last_name,gender=k.gender,parent_id=parent_id,parent_field_id=None)
        session.add(new_kid)
        session.flush()
        new_member=MemberAcademy(total_amount=k.total_amount,billing_cycle=enroll.kids_enroll.billing_cycle,amount_period=enroll.kids_enroll.amount_period,days_session=days_enroll,session_number=session_number,start_date=k.start_date,end_date=program.end_date,academy_id=enroll.kids_enroll.academy_id,kid_id=new_kid.id,program_id=enroll.kids_enroll.program_id)
        session.add(new_member)
        session.flush()
        members.append(new_member)

        enrolls.append(new_kid)
    
        notify(session=session,user_id=str(coach_id),sender_id=str(parent_id),type=f'Enrollement request',ref_id=str(enroll.kids_enroll.program_id),read=False)
    

    session.commit()
   
   


    data={
        'message':'Successfully made enrollemnt request'
    }
    
    return data
    


def approve_academy_member(session:session_db,member_id:str,user:User):
    member = session.get(MemberAcademy,UUID(member_id))
    if member.status=='accepted':
        raise HTTPException(
            status_code=409,
            detail="Membership has already been approved."
        )
    member.status='accepted'
   
   

    ref_id = member.academy_id
    academy =member.academy
    player = member.player
    reciever_id =player.user_id 
    new_invoice_note=InvoiceNotify(ref_id=member.id,type='MemberAcademy',status='pending',payee_id=user.id,payer_id=reciever_id)
    
    new_notification = notify(session=session,sender_id=str(user.id),user_id=str(reciever_id),ref_id=str(ref_id),read=False,type=f'Your request to join {academy.name} accepted') 
    print(new_notification.id)
    data ={
        'message':'request sent'
    }
    return data 


def deny_academy_member(session:session_db,member_id:str,user:User):
    member = session.get(MemberAcademy,UUID(member_id))
    if member.status=='denied':
        raise HTTPException(
            status_code=409,
            detail="Membership has already been denied."
        )

    member.status='denied'
    session.commit()
    ref_id = member.academy_id
    academy =member.academy
    player = member.player
    reciever_id =player.user_id 
  
    new_notification = notify(session=session,sender_id=str(user.id),user_id=str(reciever_id),ref_id=str(ref_id),read=False,
                                  type=f'Your request to join {academy.name} denied') 
    print(new_notification.id)
    data ={
        'message':'request denied'
    }
    return data 

     