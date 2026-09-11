from enum import Enum 
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo






class PeriodTime(str,Enum):
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month" 







def calculate_period_time(period:PeriodTime):


    now = datetime.now(ZoneInfo("Africa/Tunis"))

    print('now',now)



    if period == PeriodTime.TODAY:
        start_time = now.replace(hour=0,minute=0,second=0,microsecond=0)
        end_time = now 

    elif period == PeriodTime.LAST_7_DAYS:
        start_time = now - timedelta(days=7)
        end_time = now 

    elif period == PeriodTime.THIS_MONTH:
        start_time = now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_time = now  

    elif period == PeriodTime.LAST_MONTH:
        first_this_month = now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        start_time = (first_this_month -timedelta(days=28)).replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        end_time = first_this_month - timedelta(seconds=1)



    else : 
        end_time=now
        start_time = now - timedelta(days=30)

    return start_time,end_time



 
