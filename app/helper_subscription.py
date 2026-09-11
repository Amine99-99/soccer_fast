from fastapi import  HTTPException 
from .models import Subscription,SessionApp,ProgramAcademy ,SubscriptionRegister,User,PaymentPlan,PaymentPlanReg,SubscriptionPlan,PlanRegister
from .models import PaymentPlan,FreezePlan,Fields,UserField,InvoiceNotify,ReviewReschedule
from .core.debs import session_db

from uuid import UUID
from datetime import datetime ,timedelta
from sqlmodel import select
from sqlalchemy.orm import selectinload
from .helper_stat import notify
from .scheduler import generate_invoice_subscription





DAY_MAP={
    'Monday':0,
    'Tuesday':1,
    'Wednesday':2,
    'Thursday':3,
    'Friday':4,
    'Saturday':5,
    'Sunday':6
}



def create_subscription_coach(session:session_db,sub:SubscriptionRegister,user:User):
   
    number_of_sessions = sub.amounts.number_of_sessions
    amount_session = sub.amounts.amount_session 
    total_amount = sub.amounts.total_amount 
    amount_per_period = sub.amounts.amount_per_period
    bill_cycle= sub.schedule.billing_cycle
    pay_method = sub.schedule.payment_method
   
    days_of_week = [d.model_dump()  for d in sub.schedule.days_of_week]
    new_sub = Subscription(total_amount=total_amount,amount_per_period=amount_per_period,amount_session=amount_session,billing_cycle=bill_cycle,academy_id=None,start_date=sub.start_date,end_date=sub.end_date,duration=sub.duration,number_of_sessions=number_of_sessions,days_of_week=days_of_week,
                           user_id=user.id,field_id=sub.field_id,court_id=sub.court_id,status='pending' if pay_method=='pay_on_field' else 'online_pay_pending' ,plan_id=sub.plan_id)
    

    
   
    
   
    return new_sub
def approve_sub(session:session_db,sub_id:str,user:UserField):

    sub_db = session.get(Subscription,UUID(sub_id))
    if sub_db.program_id is not None:
        program = session.get(ProgramAcademy,sub_db.program_id)
        program.start_date=sub_db.start_date
        program.end_date = sub_db.end_date 



    if sub_db is None:
        raise HTTPException(
            status_code=401,
            detail='Subscription not found'
        )
   
    
    sub_db.status='active'
    sessions= session.exec(select(SessionApp).where(SessionApp.subscription_id==sub_db.id)).all()
    for s in sessions:
        s.status='approved'

    if sub_db.status !='active' :
        raise HTTPException(
            status_code=404,
            detail='Subscription not approved'
        )


 
    notify(session=session,user_id=str(sub_db.user_id),sender_id=str(user.id),type='Approved Subscription',ref_id=str(sub_db.id),read=False)
  
    


    

    session.commit()
   
    session.refresh(sub_db)
    for s in sessions:
        session.refresh(s)
    data={
        'message':'Subscription Active'
    }
    return data 

def deny_subscription(session:session_db,sub_id:str,user:UserField):
    sub_db = session.get(Subscription,UUID(sub_id))
    sub_db.status='rejected'
    sessions= session.exec(select(SessionApp).where(SessionApp.subscription_id==sub_db.id)).all()
    for s in sessions:
        s.status='rejected'
    session.commit()
    session.refresh(sub_db)
    for s in sessions:
        session.refresh(s)
    notify(session=session,user_id=str(sub_db.user_id),sender_id=str(user.id),type='Denied Subscription',ref_id=str(sub_db.id),read=False)

    data={
        'message':'Subscription Denied'
    }
    return data 
def transfer_subscription(session:session_db,sub_id:str,user:UserField):
    sub_db = session.get(Subscription,UUID(sub_id))
    sub_db.status=='transfered'
    session.commit()
    session.refresh(sub_db)
    data={
        'message':'Subscription Transfered'
    }
    return data 


def is_slot_available(session:session_db,field_id:UUID,date:str,time:str,court_id:UUID):
    field_db = session.exec(select(Fields).where(Fields.id==field_id).options(selectinload(Fields.sessions),selectinload(Fields.appointments),selectinload(Fields.owner_appointments))).first()
    sessions = [ s for s in  field_db.sessions if s.status=='approved' ]
   
    appointments = [a for a in field_db.appointments if a.status=='approved' ]
    owner_apps = [ap for ap in field_db.owner_appointments if ap.status=='approved']
    slots_confirmed = sessions + appointments + owner_apps 
    print(len(slots_confirmed),'len')
   

    for s in slots_confirmed :
        print(time,type(date),date,type(s.date),str(s.time)[:5],str(s.time)[:5]==time , s.date==date ,s.court_id==court_id)
      
        
        if str(s.time)[:5]==time and s.date==date and s.court_id==court_id :
            return False
    return True


    
    
    

    
       
   
def generate_sessions_sub(session:session_db,sub:SubscriptionRegister,user:User):
    subscription =create_subscription_coach(session=session,sub=sub,user=user)
    session.add(subscription)
    session.flush()
   
    sessions_db=[]
    print('court_id',sub.court_id)
   
 
    days_of_week = [d for d in sub.schedule.days_of_week]
    current_date=sub.start_date
    end_date= sub.end_date 
    approved_slot=[]
   
    while current_date<end_date:
        
        for d in days_of_week:
           time_session =  datetime.strptime(d.session_start, "%H:%M").time()
           print('time session',d.session_start,current_date)

           if current_date.weekday()==DAY_MAP[d.day_of_week]:
                available = is_slot_available(field_id=sub.field_id,court_id=sub.court_id,date=current_date,time=d.session_start,session=session)
                print('available',available)
                if available is not True:
                    approved_slot.add(new_session)
                    status='not available'
                else:
                    status='available'
                
                    
                
               
                
                new_session=SessionApp(date=current_date,time=time_session,status=status ,subscription_id=subscription.id,court_id=sub.court_id,field_id=sub.field_id)
                session.add(new_session)
                sessions_db.append(new_session)
            
               
            
        current_date = current_date+timedelta(days=1)
    
    
  
   
    data = availabilty_ratio(sessions_generated=sessions_db,conflicts_sessions=approved_slot,period=subscription.duration,sub_id=subscription.id)
    print('conf',data['conflicts_sessions'],'data',data)
    if len(data['conflicts_sessions'])==0:
        generate_invoice_subscription(sub_id=subscription.id,session=session,user=user)


    session.commit()


         
        
    field = subscription.field
    user_id= field.user_field_id
    notify(session=session,sender_id=str(user.id),user_id=str(user_id),ref_id=str(subscription.id),read=False,type=f'Request To Subscribe')
    
       
        

   
  
    return data

def availabilty_ratio(sessions_generated:list,conflicts_sessions:list,period:int,sub_id:UUID):
    total = len(sessions_generated)
   
    conflicts = len(conflicts_sessions)

    ratio = conflicts/total 
    if period==1:
        max_ratio = 0.30 
    elif 1<period <=3 :
        max_ratio=0.30
    elif  3<period<=6:
        max_ratio=0.30
    else :
        max_ratio=0.3 

    if ratio == 0:
        status = 'available'
    elif ratio <=max_ratio :
        status = 'available with sessions to renogotiate due to heavy calendar' 
    else:
        status = 'not available'


    return {
        'status':status,
        'conflicts_sessions':conflicts_sessions,
       
       
        'sub_id':sub_id
        
    }



   

        



def create_plans(session:session_db,reg:PlanRegister):
    plans= [p for p in reg.plans.sub_types ]
    plans_sub=[]
    plans_pay=[]
    plans_freeze=[]
    for p in plans:
        if p.base_benefits.applied_discount:
            final_price = p.session_price *(1-((p.base_benefits.base_discount)**0.01))
        else :
            final_price=p.session_price

        new_plan = SubscriptionPlan(
            name=p.name,type=p.type,session_price=p.session_price,
            mode=p.mode,max_sessions_per_week=p.max_sessions_per_week,target_groups=p.target_groups,field_id=UUID(reg.field_id),
            final_price=final_price,court_size=p.court_size
        )
        payment=p.payment 
        freeze= p.freeze
        session.add(new_plan)
        session.flush()
        plan_id=new_plan.id 
        new_payment = PaymentPlan(plan_id=plan_id,
                                   allowed_methods=payment.allowed_methods,
                                   first_payment_required=payment.first_payment_required
                                   
                                  )
        session.add(new_payment)
        plans_pay.append(new_payment)
        
        new_freeze= FreezePlan(plan_id=plan_id,
                                allowed=freeze.allowed,
                                max_freeze_days=freeze.max_freeze_days, 
                                max_freezes_per_period=freeze.max_freezes_per_period
                               
                               
                               )
        session.add(new_freeze)
        plans_freeze.append(new_freeze)

        plans_sub.append(new_plan)
    session.commit()
    for p in plans_sub:
        session.refresh(p)
    for pay in plans_pay:
        session.refresh(pay)
    for f in plans_freeze:
        session.refresh(f)

    return {
        'sub':plans,'pay':plans_pay,'freeze':plans_freeze
    }





def register_plan(session:session_db,reg:PlanRegister):
    plans= create_plans(session=session,reg=reg)
    plans= [p for p in reg.plans.sub_types] 
    plans_pay=[]
    plans_freeze=[]
    i=0
    for p in plans :
        payment= p.payment
        freeze = p.freeze  
      
        new_payment=PaymentPlan(
            allowed_methods=payment.allowed_methods,
            first_payment_required=payment.first_payment_required,
            plan_id = plans[i].id

        )
        new_freeze= FreezePlan(
            allowed=freeze.allowed ,
            max_freeze_days=freeze.max_freeze_days ,
            max_freezes_per_period=freeze.max_freezes_per_day ,
            plan_id=plans[i].id

        )
        i +=1
        session.add(new_payment)
        session.add(new_freeze)
        plans_pay.append(new_payment)
        plans_freeze.append(new_freeze)
    session.commit()
    for f in plans_freeze:
        session.refresh(f)
    for p in plans_pay:
        session.refresh(p)
    return {
        'sub':plans,'pay':plans_pay,'freeze':plans_freeze
    }




def negotiable_sub(session:session_db,sub_id:str):

    sub= session.exec(select(Subscription).where(Subscription.id==UUID(sub_id)).options(selectinload(Subscription.sessions))).first()

    my_sub={

        'id':sub.id,
        'start_date':sub.start_date,
        'end_date':sub.end_date,
        'duration':sub.duration,
        'status':sub.status,
        'pay':sub.payment_method,
        'number_of_sessions':sub.number_of_sessions,
        'total_amount':sub.total_amount,
        'period_amount':sub.amount_per_period,
        'field_id':sub.field_id,
        'court_id':sub.court_id,
        'sessions':[
            {
            'id':sess.id,
            'time':sess.time,
            'date':sess.date,
            'status':sess.status
            }
            for sess in sub.sessions
        ]

    }
    return my_sub



def reschedule_sub(session:session_db,reschedule:ReviewReschedule,user:User):
    sessions = session.exec(select(SessionApp).where(SessionApp.subscription_id==reschedule.sub_id,SessionApp.status=='not available')).all()
    if len(sessions) != len(reschedule.selected):
        raise HTTPException(
            status='401',
            detail='Invalid reschedule '
        )
    for i in range(len(sessions)):
        sessions[i].time = reschedule.selected[i].date 
        sessions[i].time = reschedule.selected[i].time

    generate_invoice_subscription(sub_id=reschedule.sub_id,session=session,user=user)

    session.commit() 

    return {
        'message':'Successfully rescheduled sessions'
    }
        










