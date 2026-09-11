from ..core.debs import session_db 
from ..models import Fields,PlansPltformRegisters,User,MyPlanPlatform,Invoice
from sqlmodel import select
from datetime import datetime,time,date,timedelta,timezone
from sqlalchemy.orm import selectinload
from .time_control import calculate_period_time
from zoneinfo import ZoneInfo







def admin_data(session:session_db,period:str):




    start_period,end_period = calculate_period_time(period=period)
    print('period',period)

    print(start_period,'start period')
    total_rev= revenue_platform(session=session,start_period=start_period)




    date_range={
        'from':start_period,
        'to':end_period

    }



   





    fields = session.exec(select(Fields).options(selectinload(Fields.courts),selectinload(Fields.user_field))).all()
    print('fields',fields)
    active=[]
    for f in fields:
        
        if f.status=='active' and f.approved_at.replace(tzinfo=ZoneInfo("Africa/Tunis"))<=end_period:
            active.append(f)
   
    print('active',active)
    inactive_fields = [f for f in fields if f.status=='pending' and f.create_at.replace(tzinfo=ZoneInfo("Africa/Tunis"))<=end_period]
    pending_fields = [f for f in fields if f.status== 'pending' and f.create_at.replace(tzinfo=ZoneInfo("Africa/Tunis"))<=end_period]
    print('pending_fields',pending_fields,len(pending_fields))
    avg_review = approv_avg_time(fields)
    pending_delay = surpassed_48_hours(pending_fields)
    print('total rev',total_rev)



    dash_response={
        'kpis':{
            'totalFields':len(fields),
            'activeFields':len(active),
            'inactiveFields':len(inactive_fields),
            'pendingApproval':len(pending_fields),
            'average_review':avg_review,
            'pendingOverSlaCount':pending_delay,
            'revenue':total_rev,
            
            


        },
        'timePeriod': period,
        'dateRange':date_range,
        'fields':[
            {

                'id':f.id,
                'name':f.field_name,
                'location':f.city,
                'address':f.address,
                'status':f.status,
                'company':f.user_field.company_name,
                'field_owner':f.user_field.full_name,
                'field_username':f.user_field.username,
                'phone':f.user_field.phone,
                'email':f.user_field.email,
                'date':f.create_at.date(),
                'courts':[
                    {
                        'type_of_court':court.type_of_court,
                        'court_size':court.court_size,
                        'opening_days':[d for d in court.opening_days],
                        'start_hour':court.start_hour,
                        'end_hour':court.end_hour,
                        'rate_session':court.session_price

                    }
                    for court in f.courts
                    
                    
                ]
            }
            for f in fields
        ]

    }

    return dash_response





def approv_avg_time(fields:list[Fields]):


    approved = [f for f in fields]
    avg_list=[]

    for f in approved :
        hours_diff=((f.approved_at.timestamp() *1000) - (f.create_at.timestamp() *1000 ) )/(1000*60*60) if f.approved_at else 0
        avg_list.append(hours_diff)

    try:
        avg= sum(avg_list)/len(avg_list)

    except ZeroDivisionError as e:
        avg = 0


   
    return round(avg,2)

def surpassed_48_hours(fields:list[Fields]):
  
    now = datetime.now(timezone.utc)
    avg_risk=[]  

    for f in fields:
        if ((now.timestamp()*1000) - (f.create_at.timestamp() * 1000))/(1000*60*60) >=48:
            avg_risk.append(f)

    return len(avg_risk)



def revenue_platform(session:session_db,start_period):

    invoices_paid = session.exec(select(Invoice).where(Invoice.status=='paid')).all()
    print(invoices_paid,'paid')
    print(start_period.date(),'date')
    inv_period = [inv for inv in invoices_paid if inv.due_date>=start_period.date()]
    total_rev = 0

    for inv in inv_period:
        total_rev = total_rev + inv.amount 

    print(total_rev)


    return total_rev
    














   

   








    


