from ...core.debs import session_db
from .observation import get_players_requesting ,get_player
from .reasoning import record_player_req
from .action import act_req_decision


class PlayerFinder():
    def observe(self,event,session:session_db):
        players = get_players_requesting(event=event,session=session)
        player= get_player(event=event,session=session)
        observation= {
            'player':player,
            'players':players
        }
        return observation
        

    def reason(self,observation,session:session_db):
        decision  = record_player_req(observation=observation,sesion=session)
        return decision
        
        
    def act(self,decision):
        result = act_req_decision(decision)
        return result


    def players_request(self,event,session:session_db):
        observation = self.observe(event=event,session=session)
        decision = self.reason(observation=observation,session=session)
        result = self.act(decision)
        return result


