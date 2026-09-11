from ...core.debs import session_db
from ..player_game_finder.agent import TeamFinder
from ..player_finder.agent import PlayerFinder

class AgentBase():
        
    def __init__(self):
        self.registry={
            'finding_team':TeamFinder(),
            'finding_player':PlayerFinder()
           
        
        }
    def get_agent(self,event):
        return self.registry.get(event.event_task)
  
        
  
 
'''
    def handle_team_search(self,event,session:session_db):
        observation = self.observe(event,session)
        decision = self.reason(observation,session=session,event=event)
        result = self.act(decision)
        memory_event = self.mem(event,result,session)
        self.learn(observation,decision,result,event,memory_event)
        return result
    def observe_request_team(self,event,session:session_db):
        observation_req=self.observe_request(event)


    def observe_response(self,event,session:session_db):
        

    
    def observe(self,event,session):
        raise NotImplementedError() 
    def reason(self,observation,session:session_db,event):
        raise NotImplementedError() 
    def act(self,decision):
        raise NotImplementedError()
    def mem(self,event,result):
        raise NotImplementedError()
    
    def learn(self,observation,observation_req,decision,result,event):
        pass 
        
'''
    