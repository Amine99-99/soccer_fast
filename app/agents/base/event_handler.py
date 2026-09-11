class EventHandler():
    def __init__(self,agent_base):
        self.agent_base=agent_base
      
    def handle_event(self,event,session):


        agent  = self.agent_base.get_agent(event)
        method= getattr(agent,event.event_type)
        print('method',method)

        return method(event,session) 
    

    












'''
Objects 
Agent  actions observe tool backend  db ,event data 
User player action search for team to join ,has id user name city 
Event has event type,^layer data and extra data  
Event Handler agents events type routing action route the approrivate event type to the appropriate agent 

'''