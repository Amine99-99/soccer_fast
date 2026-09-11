from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()





@app.get('/info')
def info():
    return{
        'ping':'pong'
    }