
from .observation import get_player_user,get_teams_finder,get_request_team,get_response
from .reasoning import teams_final
from .action import acting 
from ...core.debs import session_db
from ...models import User 
from ..memory.vector_store import mem
class TeamFinder():
    def request_team(self,event,session:session_db):
        observation = get_request_team(event=event,session=session)
        print('observation')
        return observation

    def respond_req(self,event,session:session_db):
        memory_response = get_response(event=event,session=session)
        return memory_response
   
        
    def observe(self,event,session:session_db):
        player_db=get_player_user(session=session,event=event)
        teams=get_teams_finder(session=session,event=event)
        observation = {
            'player':player_db,'teams':teams
                            }
       
        return observation
    def reason(self,observation:dict,session:session_db,event):
        teams = teams_final(observation=observation,session=session,event=event)
        print('teams,agent',teams)
        
        return teams
    def act(self,decision:list):
        teams=acting(decision=decision)
        return teams
    def mem(self,event,result:list,session:session_db):
        user_event = mem(event=event,result=result,session=session)
        return user_event
    def team_finding(self, event, session):
        observation = self.observe(event,session)
        decision = self.reason(observation,session,event)
        result = self.act(decision)
        memory_event = self.mem(event,result,session)
        #self.learn(observation,decision,result,event,memory_event)
        print(memory_event,'memory event')
        return memory_event
    
    





        


        
        
    def learn(self,event,observation,decision,result):
        pass

