from fastapi import APIRouter,HTTPException,Depends,Form,UploadFile
from ..core.debs import session_db,get_current_active_user
from typing import Annotated
from ..models import ReviewReschedule, ProgramAcademy,KidAcademy, SubscriptionPlan,Fields, PlanRegister,UserField, User,AcademyRegister,Academy,MemberAcademy,Player,Notification,SubscriptionRegister,Subscription,SessionApp
from ..helper_academy import create_academy ,generate_sessions,academy_enroll,approve_academy_member,deny_academy_member
from sqlmodel import select
from uuid import UUID
from ..helper_stat import notify
from ..helper_subscription import create_plans,generate_sessions_sub,deny_subscription,approve_sub
from sqlalchemy.orm import selectinload
from ..models import EnrollementAcademy
import requests
from ..helper_subscription import negotiable_sub,reschedule_sub







academy=APIRouter()




@academy.post('/register_your_academy',status_code=201)
def register_academy(session:session_db,user:Annotated[User,Depends(get_current_active_user)],academy_reg:AcademyRegister):
    academy = create_academy(session=session,academy=academy_reg,user=user)
    return academy 

@academy.get('/get_academies',status_code=200)
def get_academies(session:session_db):
    academies = session.exec(select(Academy)).all()
    academies_registred=[
        {
            'id':a.id,
            'name':a.name,
            'category':a.academy_type,
            'user_id':a.user_id,
            'user':a.user
        }
        for a in academies
    ]
    return academies_registred

@academy.get('/my_academy',status_code=200)
def get_my_academy(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    my_academy = session.exec(select(Academy).where(Academy.user_id==user.id).options(selectinload(Academy.programs))).first()

    return {
        'id':my_academy.id,
        'name':my_academy.name,
    
        'city':my_academy.city,
        'address':my_academy.address,
        'description':my_academy.description,
        'programs':[

            {
                 'id':p.id,
            'name':p.name,
            'min_age':p.min_age,
            'max_age':p.max_age,
            'gender':p.gender,
            'status':p.status,
           
            'description':p.description,
            'max_players':p.max_players,
            'amount_fee':p.amount_fee_period,
            
            'open':p.enrollment_open,
             
            }
            for p in my_academy.programs
        ]
    }


@academy.post('join_academy/{academy_id}',status_code=201)
def join_academy(session:session_db,academy_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    academy = session.get(Academy,UUID(academy_id))
    player = session.exec(select(Player).where(Player.user_id==user.id)).first()
    if player is None:
        raise HTTPException(
            status_code=401,
            detail='You are not registred as player'
        )
    player_id=player.id
    reciever_id =academy.user_id

    new_member= MemberAcademy(player_id=player_id,academy_id=UUID(academy_id),status='pending')
    session.add(new_member)
    session.commit()
    session.refresh(new_member)
    if new_member.id is not None:
        new_notification = notify(session=session,sender_id=str(user.id),user_id=str(reciever_id),ref_id=academy_id,read=False,
                                  type=f'Player {player.name} making request to join the academy {academy.name}') 
        print(new_notification.id)
    data ={
        'message':'request sent'
    }
    return data 
@academy.post('/approve_academy_member/{member_id}',status_code=201)
def approve_academy_membership(session:session_db,member_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    return approve_academy_member(session=session,member_id=member_id,user=user)
   

@academy.post('/deny_academy_member/{member_id}',status_code=201)
def deny_academy_membership(session:session_db,member_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    return deny_academy_member(session=session,member_id=member_id,user=user)
   



@academy.post('/academy_subscription',status_code=201)
def subscribe_academy(session:session_db,sub:SubscriptionRegister,user:Annotated[User,Depends(get_current_active_user)]):
    return generate_sessions(session=session,sub=sub,user=user)
   
   
    



@academy.get('/my_academy_subscription',status_code=201)
def my_subscription(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    subscription =  session.exec(select(Subscription).where((Subscription.user_id==user.id)&(Subscription.status=='pending'))).first()
    print('subscription',subscription)
    subscription_db={
        'id':subscription.id,
        'academy_id':subscription.academy_id ,
        'field_id':subscription.field_id,
        'field':subscription.field,
        'start_date':subscription.start_date,
        'end_date':subscription.end_date,
        'status':subscription.status,
        'created_at':subscription.created_at,
        
            
            
    }
    
    return subscription_db



@academy.get('/my_academy_sessions',status_code=200)
def get_my_sessions(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    sessions= session.exec(select(SessionApp).join(Subscription).where( Subscription.user_id == user.id, Subscription.status == 'pending')).all()
    print(sessions)

    sessions_db = [
        {
            'id':s.id,
            'day':s.date,
            'hour':s.time,
            'status':s.status,
            'subscription_id':s.subscription_id,
            'subscription':s.subscription
        }
        for s in sessions
    ]
    return sessions_db



@academy.post('/register_plans',status_code=201)
def register_plans(session:session_db,user:Annotated[UserField,Depends(get_current_active_user)],reg:PlanRegister):
    plans = create_plans(session=session,reg=reg)
    print(plans)
    return plans



@academy.get('/my_plans_registered',status_code=200)
def my_plans(session:session_db,user:Annotated[UserField,Depends(get_current_active_user)]):
    plans = session.exec(select(SubscriptionPlan).join(Fields).where(Fields.user_field_id==user.id,SubscriptionPlan.status=='active').options(selectinload(SubscriptionPlan.payment_plan),selectinload(SubscriptionPlan.freeze_plan))).all()
    print(plans,'plans')
    plans_active=[
        {
            'id':p.id,
            'name':p.name,
            'type':p.type,
            'session_price':p.session_price,
            'mode':p.mode,
            'target_groups':p.target_groups,
            'max_session':p.max_sessions_per_week,
            'court_size':p.court_size,
            'payment_plan':[p.payment_plan.allowed_methods],
            'freeze_plan_allowed':p.freeze_plan.allowed,
            'first_payment':p.payment_plan.first_payment_required,
            'max_freeze_days':p.freeze_plan.max_freeze_days

        }
        for p in plans
    ]
    return plans_active


@academy.get('/plans_registered/{field_id}',status_code=200)
def registered_plans(session:session_db,field_id:str):
    plans = session.exec(select(SubscriptionPlan).where(SubscriptionPlan.field_id==UUID(field_id)).options(selectinload(SubscriptionPlan.payment_plan),selectinload(SubscriptionPlan.freeze_plan))).all()
    print(plans,'plans')
    plans_active=[
        {
            'id':p.id,
            'name':p.name,
            'type':p.type,
            'session_price':p.session_price,
            'mode':p.mode,
            'target_groups':p.target_groups,
            'max_session':p.max_sessions_per_week,
            'court_size':p.court_size,
            'final_price':p.final_price,
            'payment_plan':[p.payment_plan.allowed_methods],
            'freeze_plan_allowed':p.freeze_plan.allowed,
            'first_payment':p.payment_plan.first_payment_required,
            'max_freeze_days':p.freeze_plan.max_freeze_days,
                    
                    
            }
        for p in plans
    ]
    return plans_active


@academy.post('/register_subscription',status_code=201)
def subscribe_register(session:session_db,sub:SubscriptionRegister,user:Annotated[User,Depends(get_current_active_user)]):
    return generate_sessions_sub(session=session,sub=sub,user=user)
    


@academy.get('/my_subscription_plan',status_code=201)
def my_subscription_plans(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    subscriptions =  session.exec(select(Subscription).where((Subscription.user_id==user.id)).options(selectinload(Subscription.sessions))).all()
    if subscriptions is None:
        raise HTTPException(
            status_code=404,
            detail='Plan Not Found'

        )
    subscription_db=[
        
        {
        'id':subscription.id,
      
        
        'field_id':subscription.field_id,
        'field':subscription.field,
        'plan_id':subscription.plan_id,
        'plan':subscription.plan,
        'duration':subscription.duration,
        'start_date':subscription.start_date,
        'end_date':subscription.end_date,
        'status':subscription.status,
        'created_at':subscription.created_at,
        'sessions':subscription.number_of_sessions,
        'days':subscription.days_of_week,
        'sessions_sub': [
            {'id':s.id,
            'date':s.date,
            'time':s.time,
            'status':s.status,
            'subscription_id':s.subscription_id,
            'subscription':s.subscription}
            for  s in subscription.sessions
        ]
      

        
            
            
    }
    for subscription in subscriptions
    ]

    
    return subscription_db

@academy.get('/plans/{plan_id}',status_code=200)
def my_plan_id(session:session_db,plan_id:str,user:Annotated[User|UserField,Depends(get_current_active_user)]):

    subscription = session.exec(select(Subscription).where(Subscription.id==UUID(plan_id)).options(selectinload(Subscription.sessions))).first()
    subscription_db={
        'id':subscription.id,
      
        
        'field_id':subscription.field_id,
        'field':subscription.field,
        'plan_id':subscription.plan_id,
        'plan':subscription.plan,
        'user':subscription.user,
        'court_id':subscription.court_id,
        'user_id':subscription.user_id,
        'duration':subscription.duration,
        'start_date':subscription.start_date,
        'end_date':subscription.end_date,
        'status':subscription.status,
        'created_at':subscription.created_at,
        'sessions':subscription.number_of_sessions,
        'days':subscription.days_of_week,
        'sessions_sub': [
            {'id':s.id,
            'date':s.date,
            'time':s.time,
            'status':s.status,
            'subscription_id':s.subscription_id,
            'subscription':s.subscription}
            for  s in subscription.sessions
        ]
      

        
            
            
    }
    return subscription_db



@academy.get('/my_subscribers/{field_id}',status_code=200)
def subscribers(session:session_db,field_id:str,user:Annotated[UserField,Depends(get_current_active_user)]):
    subscriptions = session.exec(select(Subscription).where(Subscription.field_id==UUID(field_id)).options(selectinload(Subscription.sessions))).all()

    subscription_db=[
        {
        'id':subscription.id,
      
        
        'field_id':subscription.field_id,
        'field':subscription.field,
        'plan_id':subscription.plan_id,
        'plan':subscription.plan,
        'academy_id':subscription.academy_id,
        'academy':subscription.academy,
        'program_id':subscription.program_id,
        'program':subscription.program,
        'user':subscription.user,
        'user_id':subscription.user_id,
        'duration':subscription.duration,
        'start_date':subscription.start_date,
        'end_date':subscription.end_date,
        'status':subscription.status,
        'created_at':subscription.created_at,
        'sessions':subscription.number_of_sessions,
        'days':subscription.days_of_week,
        'sessions_sub': [
            {'id':s.id,
            'date':s.date,
            'time':s.time,
            'status':s.status,
            'subscription_id':s.subscription_id,
            'subscriber':s.subscription.user.username,
           

            
            }
            for  s in subscription.sessions
        ]


        
        }
        for subscription in subscriptions
      

        
            
            
    ]
    return subscription_db 



@academy.post('/my_subscriber_approve/{sub_id}',status_code=201)
def approve_subscriber(session:session_db,sub_id:str,user:Annotated[UserField,Depends(get_current_active_user)]):
    approve_sub(session=session,sub_id=sub_id,user=user)



@academy.post('/my_subscriber_deny/{sub_id}',status_code=201)
def deny_subscriber(session:session_db,sub_id:str,user:Annotated[UserField,Depends(get_current_active_user)]):
    deny_subscription(session=session,sub_id=sub_id,user=user)




@academy.get('/my_academy_id/{academy_id}',status_code=200)
def academy_detail(session:session_db,academy_id:str):

    my_academy = session.exec(select(Academy).where(Academy.id==UUID(academy_id))
                              .options(selectinload(Academy.user),selectinload(Academy.programs),selectinload(Academy.membership),selectinload(Academy.subscriptions))).first()
    

    my_academy_detail={
        'id':my_academy.id,
        'name':my_academy.name,
        'coach':my_academy.user.username,
        'city':my_academy.city,
        'address':my_academy.address,
        'phone':my_academy.user.phone,
     
        


    }


    return my_academy_detail

@academy.get('/my_academy_programs/{academy_id}')
def my_programs(session:session_db,academy_id:str):
    programs= session.exec(select(ProgramAcademy).where(ProgramAcademy.academy_id==UUID(academy_id))
                           .options(selectinload(ProgramAcademy.coach),selectinload(ProgramAcademy.subscriptions),selectinload(ProgramAcademy.membership))).all()
    
    print(programs,'programs')
    
    programs_by_academy=[
        {
            'id':p.id,
            'name':p.name,
            'min_age':p.min_age,
            'max_age':p.max_age,
            'gender':p.gender,
            'status':p.status,
            'coach':p.coach.username if p.coach else None,
            'description':p.description,
            'max_players':p.max_players,
            'amount_fee':p.amount_fee_period,
          
            'open':p.enrollment_open,
           

            'subscription':[
                {
                    'id':s.id,
                    'field':s.field.field_name,
                    'city':s.field.city,
                    'address':s.field.address,
                    'start_date':s.start_date,
                    'end_date':s.end_date,
                    'duration':s.duration,
                    'status':s.status,
                    'sessions':s.number_of_sessions,
                    'days':[d for d in s.days_of_week],

                }
                for s in p.subscriptions 
            ],
            

        }
        for p in programs
    ]

    return programs_by_academy



@academy.get('/program_by_id/{program_id}',status_code=200)
def my_program_detail(session:session_db,program_id:str):
    program = session.exec(
    select(ProgramAcademy)
    .where(ProgramAcademy.id == UUID(program_id))
    .options(
        selectinload(ProgramAcademy.coach),
        selectinload(ProgramAcademy.academy),
        selectinload(ProgramAcademy.subscriptions),
        selectinload(ProgramAcademy.membership)
    )
).first()


    my_program = {
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
     'start_date':program.start_date,
     'end_date':program.end_date,
    'open': program.enrollment_open,
    'academy_id':program.academy_id,
    'academy_name':program.academy.name,
    'logo':program.academy.logo,


    'subscriptions': [
        {
            'id': subscription.id,
            'field': subscription.field.field_name,
            'city': subscription.field.city,
            'address': subscription.field.address,
            'start_date': subscription.start_date,
            'end_date': subscription.end_date,
            'duration': subscription.duration,
            'status': subscription.status,
            'sessions': subscription.number_of_sessions,
            'days': [
                day for day in subscription.days_of_week
            ],

        }

        for subscription in program.subscriptions
    ],

}
    return my_program



@academy.post('/enroll_kids',status_code=201)
def enroll_my_kids(session:session_db,enroll:EnrollementAcademy):
    return academy_enroll(session=session,enroll=enroll)



@academy.get('/my_academy_memebrship/{academy_id}',status_code=200)
def my_members_academy(session:session_db,academy_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    print('academy_id',UUID(academy_id))
    academy=session.exec(select(Academy).where(Academy.id==UUID(academy_id)).options(selectinload(Academy.membership))).first()
    print('academy db ',academy.membership)
    memberships= session.exec(select(MemberAcademy).where(MemberAcademy.academy_id == UUID(academy_id)).options(selectinload(MemberAcademy.kid)
        .selectinload(KidAcademy.parent),selectinload(MemberAcademy.program))).all()
    print('m',memberships)
  

    members_academy = [
        {
            'id':m.id,
            'kid_birth_date':m.kid.birth_date,
            'first_name':m.kid.first_name,
            'last_name':m.kid.last_name,
            'gender':m.kid.gender,
            'parent_id':m.kid.parent_id,
            'parent_name':m.kid.parent.username,
            'email':m.kid.parent.email,
            'phone':m.kid.parent.phone,
            'address':m.kid.parent.address,
            'program_id':m.program_id,
            'program_name':m.program.name,
            'status':m.status

        }
        for m in  memberships
    ]
    return members_academy



@academy.get('/my_program/{program_id}',status_code=200)
def my_program_page(session:session_db,program_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    program = session.exec(
    select(ProgramAcademy)
    .where(ProgramAcademy.id == UUID(program_id))
    .options(
        selectinload(ProgramAcademy.coach),
        selectinload(ProgramAcademy.academy),
        selectinload(ProgramAcademy.subscriptions),
        selectinload(ProgramAcademy.membership)
    )
).first()
    print('program',program)


    my_program = {
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
    'start_date':program.start_date ,
    'end_date':program.end_date ,


    'subscriptions': [
        {
            'id': subscription.id,
            'field': subscription.field.field_name,
            'city': subscription.field.city,
            'address': subscription.field.address,
            'start_date': subscription.start_date,
            'end_date': subscription.end_date,
            'duration': subscription.duration,
            'status': subscription.status,
            'sessions': subscription.number_of_sessions,
            'days': [
                day for day in subscription.days_of_week
            ],

        }

        for subscription in program.subscriptions
    ],

}
    return my_program



@academy.get('/my_kids_academy',status_code=200)
def my_kids(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    kids = session.exec(select(KidAcademy).where(KidAcademy.parent_id==user.id).options(selectinload(KidAcademy.membership))).all()

    print('kids',kids)
    print('kids')
    my_kids=[
        {
            'id':k.id,
            'first_name':k.first_name,
            'last_name':k.last_name,
            'gender':k.gender,
            'memebrs':[
                {
                'id':m.id,
                'academy_id':m.academy_id,
                'program':m.program_id
                }
                for m in k.membership
            ]
           

        }
        for k in kids
    ]
    return my_kids


@academy.get('/my_just_subscribed/{sub_id}')
def my_just_sub(session:session_db,sub_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    return negotiable_sub(session=session,sub_id=sub_id)


@academy.post('/reschedule_sessions')
def reschedule(session:session_db,reschedule:ReviewReschedule,user:Annotated[User,Depends(get_current_active_user)]):
    return reschedule_sub(session=session,reschedule=reschedule,user=user)




       