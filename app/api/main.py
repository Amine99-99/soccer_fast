from fastapi import APIRouter
from . import users,log ,courts,game,stat,search,academy,payment,admin
from ..agents.agent_api import my_agent

api_router= APIRouter()




api_router.include_router(users.auth)
api_router.include_router(log.auth)
api_router.include_router(courts.court)
api_router.include_router(game.game)
api_router.include_router(stat.stat)
api_router.include_router(search.search)
api_router.include_router(my_agent.my_agent)
api_router.include_router(academy.academy)
api_router.include_router(payment.filed)
api_router.include_router(admin.admin)





