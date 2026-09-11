from fastapi import APIRouter,HTTPException,Depends,Form,UploadFile
from ..helper_3 import approve_appointment, get_courts,create_courts,get_field,create_appointment,field_owner_book
from ..models import UserField,Fields,FieldsRegister,Appointment,AppointmentRegister,User,AppointmentOwner,AppointmentRegisterOwner
from ..models import AppointmentRegisterUpdate,RequestTransfer
from ..core.debs import session_db,get_courts_registred,get_current_active_user
from typing import Annotated,List
from sqlmodel import select
import json
from uuid import UUID 
from ..helper_3 import get_registred_trans,create_courts_x,transfer_appointment
from ..models import Payment,PaymentMethod,PaymentStatus,PaymentRegister,Court,Subscription,Transfer
from sqlalchemy.orm import selectinload
from ..field_owner_service.field_service import FieldOwnerService



court =APIRouter()
help(get_courts)



new_field_owner = FieldOwnerService()



@court.post('/register_court',response_model=Fields,status_code=201)
async def register_court(session:session_db,field:FieldsRegister,user:Annotated[UserField,Depends(get_courts_registred)]):
    data = create_courts_x(session=session,field=field,user=user)
    return data


@court.get('/courts',status_code=200)
def get_court(session:session_db)->List[dict]:
    fields = session.exec(select(Fields)).all()
    



    fields_platform = [
        {
            'id':field.id,
            'number_of_courts':field.number_of_courts,
            'field_name':field.user_field.company_name,
            'city':field.city,
            'postal_code':field.postal_code,
            'name':field.field_name,
            'address':field.address,

           
            
        }
        for field in fields
    ]
    
 
  
  
    return fields_platform

@court.get('/fields/{field_id}',status_code=200)
def my_field_book(session:session_db,field_id:str,user:Annotated[User,Depends(get_current_active_user)]):
     fields  = session.exec(select(Fields).where(Fields.id==UUID(field_id)).options(selectinload(Fields.courts))).first()
     my_fields= {
        'id':fields.id,
      
        'city':fields.city,
        'address':fields.address,
        'field_name':fields.field_name,
        'courts':[
            {
                'id':c.id,
                'court_size':c.court_size,
                'price':c.session_price,
                'type_of_court':c.type_of_court,
            'opening_days':c.opening_days,
            'start_hour':c.start_hour,
            'end_hour':c.end_hour,
            'duration':c.session_time,
            
            'session_price':c.session_price,
            'field_id':c.field_id

            }
            for c in fields.courts
        ]
        
        


          }
            
 
     return my_fields
@court.get('/courts_field/{field_id}',status_code=200)
def courts_field(session:session_db,field_id:str):
    print('field id',field_id)
    f = session.exec(select(Fields).where(Fields.id==UUID(field_id)).options(selectinload(Fields.courts))).first()
    print('f',f)
    

    field_associated ={
            'id':f.id,
            'name':f.field_name,
            'city':f.city,
            'number_of_courts':f.number_of_courts,
            'courts': [
                {
            'id':c.id,
            'type_of_court':c.type_of_court,
            'opening_days':c.opening_days,
            'start_hour':c.start_hour,
            'end_hour':c.end_hour,
            'duration':c.session_time,
            'court_size':c.court_size,
            'session_price':c.session_price,
            'field_id':c.field_id
        } 
          for c in f.courts

            ]
        }

     
 
    
    return field_associated



@court.get('/courts_user')
def get_user_court(session:session_db,user:Annotated[UserField,Depends(get_courts_registred)]):
    fields  = session.exec(select(Fields).where(Fields.user_field_id==user.id).options(selectinload(Fields.courts),
        selectinload(Fields.appointments),selectinload(Fields.subscriptions))).all()

  
    


     
    my_fields= [{
        'id':field.id,
        
        'city':field.city,
        'address':field.address,
        'field_name':field.field_name,
        'courts':[
            {
                'id':c.id,
                'court_size':c.court_size,
                'price':c.session_price,
                'type_of_court':c.type_of_court,
            'opening_days':c.opening_days,
            'start_hour':c.start_hour,
            'end_hour':c.end_hour,
            'duration':c.session_time,
            
            'session_price':c.session_price,
            'field_id':c.field_id

            }
             for c in field.courts
            
            ],
        'appointments_approved':[
            {
                'id':a.id,
                'time':a.time,
                'date':a.date,
                'status':a.status,
                'payment_method':a.payment_method,
                'user_id':a.user_id if a.user else a.user_field_id
            }
            for a in field.appointments if a.status=='approved'
        ],
        'appointments_pending':[
            {
                'id':a.id,
                'time':a.time,
                'date':a.date,
                'status':a.status,
                'payment_method':a.payment_method,
                'user_id':a.user_id if a.user else a.user_field_id
            }
            for a in field.appointments if a.status=='pending' or a.status=='payment confirmation'
        ],
        'subscriptions_pending':[
            {
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
                
            }
            for subscription in field.subscriptions if subscription.status=='pending'
        ],
             'subscriptions_active':[
            {
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
                
            }
            for subscription in field.subscriptions if subscription.status=='active'
        ]
    }
           for field in fields
           
        ]
    
        
        


    
   
    
    
    return my_fields

@court.get('/fields_appointments/{field_id}',status_code=200)
def my_field_apps_approved(session:session_db,field_id:str,user:Annotated[UserField,Depends(get_courts_registred)]):
    fields  = session.exec(select(Fields).where(Fields.user_field_id==user.id).options(selectinload(Fields.appointments))).all()
    appointmnets_fields=[

    ]




@court.delete('/delete_court/{field_id}',status_code=200)
def delete_field(session:session_db,field_id:str):
    field= session.get(Fields,UUID(field_id))
    print('field',field)
    session.delete(field)
    session.commit() 
    return {
        'message':'field successfully deleted'
    }


@court.post('/book_court',status_code=201)
def book_court(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)],appointment:AppointmentRegister):
    return create_appointment(session=session,appointment=appointment,user=user)
   



@court.post('/request_app',status_code=200)
def request_appointment(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)]):
    pass

    

@court.get('/get_apps',status_code=201)
def get_apps(session:session_db):
    apps_stat = select(Appointment)
    apps_list = session.exec(apps_stat).all()
    print(apps_list,'apps')


    booked_ = [
        {
            'id':a.id,
            'date':a.date,
            'time':a.time,
            'status_appointment':a.status,
            
           
            
            'field_name':a.field.field_name,
            'field':a.field,
            'field_id':a.field_id,
            'city':a.field.city, 
            'address':a.field.address,
            'courts':a.field.courts,
            'user':a.user if a.user else a.user_field,
            'user_id': a.user_id if a.user else a.user_field_id,
            'game_id':a.game_id,
            'game':a.game
            
        }
        for a in apps_list
    ]
    return booked_




@court.post('/approve_appoint/{app_id}',status_code=200)
def approve_app(session:session_db,app_id:str,user:Annotated[UserField,Depends(get_courts_registred)]):
   return approve_appointment(session=session,app_id=app_id,user=user)

@court.post('/owner_booking',status_code=201)
def owner_book(session:session_db,appointment:AppointmentRegisterOwner,user:Annotated[UserField,Depends(get_courts_registred)]):
    app_owner = field_owner_book(session=session,appointment=appointment,user=user)
    return app_owner
    


    



@court.post('/deny_appointment/{app_id}',status_code=200)
def reject_app(session:session_db,app_id:UUID,user:Annotated[UserField,Depends(get_courts_registred)]):
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Unauhtorised User'
        )
    apps = session.get(Appointment,app_id)
    if apps.status =='approved':
        raise HTTPException(
            status_code=401,
            detail='invalid appointment to reject'

        )
    apps.status='deleted'
    
    session.commit()
    session.refresh(apps)
    
    return  {'message':'canceled appointment'}
    




@court.delete('/cancel_appointment/{app_id}',status_code=201)
def delete_app(session:session_db,app_id:str):
    app_db = session.get(Appointment,UUID(app_id))
    session.delete(app_db)
    session.commit()
    return {
        'message':'success'
    }
@court.post('/transfer_app',status_code=201)
def transfer_app(session:session_db,user:Annotated[UserField,Depends(get_courts_registred)],trans:Transfer):
    transfer_appointment(session=session,user=user,trans=trans)
  






@court.post('/approve_trans/{req_id}',status_code=201)
def approve_trans(session:session_db,req_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    req_approved  = session.get(RequestTransfer,UUID(req_id))
    if not req_approved.user_requested_id == user.id:
        raise HTTPException(
            status_code=401,
            detail='user  is invalid'
        )
    if not req_approved:
        raise HTTPException(
            status_code=401,
            detail='req  is invalid'
        )
    req_approved.status_req=='approved'

    app_approved = session.get(Appointment,req_approved.app_id)
    if not app_approved:
        raise HTTPException(
            status_code=401,
            detail='req  is invalid'
        )
    app_approved.status_appointment='approved'
    session.commit()
    session.refresh(app_approved)
    session.refresh(req_approved)
    return app_approved
@court.post('/reject_trans/{req_id}',status_code=201)
def reject_trans_app(session:session_db,req_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    
    req_denied  = session.get(RequestTransfer,UUID(req_id))
    if not req_denied.user_requested_id == user.id:
        raise HTTPException(
            status_code=401,
            detail='user  is invalid'
        )
    if not req_denied:
        raise HTTPException(
            status_code=401,
            detail='req  is invalid'
        )
    req_denied.status_req=='denied'

    app_denied = session.get(Appointment,UUID(req_denied.app_id))
    if not app_denied:
        raise HTTPException(
            status_code=401,
            detail='req  is invalid'
        )
    app_denied.status_appointment='deleted'
    session.commit()
    session.refresh(app_denied)
    session.refresh(req_denied)
    return req_denied

   
    

@court.get('/get_req_app',status_code=200)
def get_my_app_req(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    stats = select(RequestTransfer).where(RequestTransfer.user_requested_id==str(user.id))
    reqs= session.exec(stats).all()
    reqs_app= [
        {
            'id':r.id,
            'app_id':r.app_id,
             'user':r.user_field if r.user_field else r.user,
             'requested': r.user_requested_id,
             'status_req':r.status_req

        }
        for r in reqs
    ]
    print('reqs_app',reqs_app)

    return reqs_app



@court.get('/owner_apps/{field_id}',status_code=200)
def get_owner_apps(session:session_db,field_id:str,user:Annotated[UserField,Depends(get_current_active_user)]):
    return new_field_owner.app_owner_fields(session=session,field_id=field_id)
   
@court.get('/my_appointments_field/{field_id}',status_code=200)
def get_my_apps(session:session_db,field_id:str,user:Annotated[UserField,Depends(get_courts_registred)]):
    return new_field_owner.appointments_field(session=session,field_id=field_id)
    
   



@court.get('/sessions_app/{field_id}',status_code=200)
def my_sessions_app(session:session_db,field_id:str,user:Annotated[UserField,Depends(get_current_active_user)]):
    return new_field_owner.sessions_sub_fields(session=session,field_id=field_id)
    

@court.get('/my_apps_field',status_code=200)
def get_my_field_app(session:session_db,user:Annotated[UserField,Depends(get_courts_registred)]):
    stat = select(Fields).where(Fields.user_field_id==user.id)

    field = session.exec(stat).first() 
    stats = select(AppointmentOwner).where(AppointmentOwner.field_id==field.id)
    apps = session.exec(stats).all()
    print('apps',apps)

    my_booked_apps =[
        {
            'id':a.id,
            'date':a.date,
            'time':a.time,
            
             'status':a.status,
            
            'court':a.court_id,
            'paid':a.payment_status,
            'field_name':a.field.field_name,
            'field':a.field,
            'field_id':a.field_id,
            'city':a.field.city, 
            'address':a.field.address,
            'courts':a.field.courts,
            'user':a.user_field,
            'username':a.username,
            'phone':a.phone,
            
            'user_id': a.user_field_id,
     

        }
        for a in apps
    ]

    return my_booked_apps



'''

user reciev request about transfer he may approve it why this appointment id has priority?


'''
@court.get('/my_booked_app',status_code=200)
def my_booked(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    stat = select(Appointment).where(Appointment.user_id==user.id)
    my_booked = session.exec(stat).all()
    my_booked_apps = [
        {
            'id':a.id,
            'date':a.date,
            'time':a.time,
            'status':a.status,
           
            'court':a.court_id,
            'paid':a.paid,
            'field_name':a.field.field_name,
            'field':a.field,
            'field_id':a.field_id,
            'city':a.field.city, 
            'address':a.field.address,
            'courts':a.field.courts,
          


        }
        for a in my_booked
    ]
    return my_booked_apps


@court.get('/my_booked_app_pending',status_code=200)
def my_booked(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    pending_apps = session.exec(
    select(Appointment).where(
        Appointment.user_id == user.id,
        Appointment.status.in_(
            ["pending", "payment confirmation"]
        )
    )
).all()
    print('pendi',pending_apps)
    apps_pending=[

        {
            'id':a.id,
            'date':a.date,
            'time':a.time,
            'status':a.status,
            'payment_method':a.payment_method

        }
        for a in pending_apps
    ]
    print(apps_pending,'pending')
    return apps_pending
@court.get('/my_booked_app_approved',status_code=200)
def my_booked(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    approved_apps = session.exec(select(Appointment).where(Appointment.user_id==user.id ,Appointment.status=='approved')).all()
    apps_approved=[

        {
            'id':a.id,
            'date':a.date,
            'time':a.time,
            'status':a.status,
            'payment_method':a.payment_method

        }
        for a in approved_apps
    ]
    return apps_approved


@court.post('/pay_booked',status_code=201)
def pay_app(session:session_db,user:Annotated[User|UserField,Depends(get_current_active_user)],payment:PaymentRegister):
    
    new_payment= Payment(user_id=user.id,status=PaymentStatus.INITIATED,method=payment.method,amount=float(payment.amount),appointment_id=UUID(payment.app_id))
    app= session.get(Appointment,UUID(payment.app_id))
    
    session.add(new_payment)
    session.flush()
    app.status=='approved'


    
    session.commit()
    session.refresh(new_payment)
    session.refresh(app)
    return new_payment


@court.get('/session_paid/{book_id}',status_code=201)
def session_paying(session:session_db,book_id:str,user:Annotated[User,Depends(get_current_active_user)]):
    session_to_pay = session.get(Appointment,UUID(book_id))
    session_paying={
        'id':session_to_pay.id,
        'time':session_to_pay.time,
        'date':session_to_pay.date,
        'method':session_to_pay.payment_method,
        'field_name':session_to_pay.field.field_name
    }
    return session_paying


@court.get('/my_apps_booked',status_code=200)
def my_booked(session:session_db,user:Annotated[User,Depends(get_current_active_user)]):
    stat = select(Appointment)
    my_booked = session.exec(stat).all()
    my_apps = [
        {
            'id':a.id,
            'date':a.date,
            'time':a.time,
            'status':a.status,
            'payment_method':a.payment_method


        }
        for a in my_booked
    ]
    print(my_apps,'my apps')
    return my_apps











    

    


    