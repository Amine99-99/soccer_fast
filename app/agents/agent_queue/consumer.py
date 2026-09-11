from dotenv import load_dotenv
import os

load_dotenv()
import redis 

from ..base.agent import AgentBase
import json
from ..base.event import Event
from ..base.event_handler import EventHandler 
from ...core.db import engine ,create_db_and_tables
from sqlmodel import Session
import time







r= redis.Redis(host='localhost',port=6379)

pubsub = r.pubsub()
pubsub.subscribe('team_finder','request_team','respond_req','players_request')
print("Consumer subscribed to channels:", pubsub.channels)

create_db_and_tables()
print(engine.url,'engine url')

print("DB PATH:", os.path.abspath("database.db"))

agent = AgentBase()

dispatcher = EventHandler(agent)






try:
    while True:
        message = pubsub.get_message(timeout=1)

        if message and message["type"] == "message":
            print('hello amine')

            print("Consumer received raw message:", message['data'])
            data = json.loads(message['data'])

            print("Parsed event data:", data)

            event = Event(
                event_type=data['event_type'],
                event_task=data['event_task'],
                event_id=data['event_id'],
                payload=data['payload'],
                timestamp=data['timestamp']
            )
            i= 1
            i =i+1
            print(i,f'{i} event')

            print("Event object created:", event)

            session = None
            try:
                session = Session(engine)

                dispatcher.handle_event(event, session)
                print("Dispatcher handled event and sent to agent")

            except Exception as e:
                print("Error while dispatching to agent:", e)

            finally:
                if session:
                    session.close()

        # small sleep to avoid CPU overuse
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping consumer...")

finally:
    pubsub.close()
    r.close()
    print("Consumer shut down cleanly.")
   



'''
import redis
from ...core.config import settings

def main():
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    pubsub = r.pubsub()
    pubsub.subscribe("agents")  # the channel name

    print("Consumer is listening on 'agents' channel...")
    for message in pubsub.listen():
        if message['type'] == 'message':
            print("Received message:", message['data'].decode())

if __name__ == "__main__":
    main()

Objects 
User ==> RequestSearch ===>Event triggered===>Redis object publich event ===>
Redis subscribe to events channels Even Handler took event as arg and routed to the right agent Agent 
event first search then observe reason decide then store to db EventUser event data result and user 
now user made request new event triggered the agent observe the request and compare with event user 
agent observe request made with wich team  compaare with result in event user
    '''