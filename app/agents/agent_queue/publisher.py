import redis 
import json
from ..base.event import Event
from ...models import User
from ...core.debs import session_db
import uuid




Channel='team_finder'
redis_client = redis.Redis(host="localhost",port=6379)
channel_1 = 'request_team'
channel_2 ='respond_req'
channel_3 = 'find_player'

def publish_response(req_id:str):
    event_id=str(uuid.uuid4())
   
    payload={
        'req_id':req_id
    }
    
    event = Event(event_type='respond_req',event_task='finding_team',event_id=event_id,payload=payload)
   

    event.payload=payload
    message = json.dumps(event.to_dict())
    print('message',message)
    redis_client.publish(channel_2,message)

def find_player(player_id:str,extra_payload):
    event_id=str(uuid.uuid4())
    payload={
        'player_id':player_id
    }

    if extra_payload:
        payload.update(extra_payload)
    event = Event(event_tyep='players_request',event_task='finding_player',event_id=event_id,payload=payload)

    message = json.dumps(event.to_dict())
    print(message,type(message),'message finding player')
    redis_client.publish(channel_3,message)
    print('event player search published')
    return event_id


def publish_event_1(player_id:str,extra_payload):
    event_id=str(uuid.uuid4())
    
   
    payload={
        'player_id':player_id,
        
        
    }
    if extra_payload:
        payload.update(extra_payload)
   
    event  = Event(event_type='request_team',event_task='finding_team',event_id=event_id,payload=payload)
   
  
    message = json.dumps(event.to_dict())
    print('message2',message)
    redis_client.publish(channel_1,message)
    print('redis client',redis_client.publish(channel_1,message))



def publish_event(user:User,extra_payload):
    event_id=str(uuid.uuid4())
    print('eventid',event_id)
    payload={
        'player_id':str(user.id),
        'player_name':user.username,
        
    }
    if extra_payload:
        payload.update(extra_payload)
   
    
   
    event =Event(event_type='team_finding',event_task='finding_team',event_id=event_id,payload=payload)
    
   
    print(event.payload,event.event_id,'eventid and payload')
   
    message = json.dumps(event.to_dict())
    print("Redis message to publish:", message)
    redis_client.publish(Channel,message)
    print("Event published to Redis channel:", Channel)
    return event_id

    '''


    agent decided share the list with player 
    i created model to store these data  
    now enforecement learning and building longterm memory 
    the agent must be aware what the player decided  
    the agent must learn if request approved or not for the list he suggested  
    the agent mudt have these data thrugh two new event event when the player sned reqs this is the first learning pricess and new even if approve or deny regarinf the request 

    
    
    '''
