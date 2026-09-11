from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from typing import Annotated
from pydantic import BaseModel
from unittest.mock import patch
import pytest
from .log import auth 
import uuid

client = TestClient(auth)

class User:
    def __init__(self,id,username,email,register_as,phone):
        self.id=id 
        self.username=username 
        self.email = email 
        self.register_as = register_as 
        self.phone = phone 
class UserField(User):
    def __init__(self,id,username,email,register_as,phone,company_name,company_code):
        super().__init__(id,username,email,register_as,phone)
        self.company_name=company_name 
        self.company_code = company_code 

class UserPublic(BaseModel):
    id:uuid.UUID
    username:str 
    email:str 
    register_as:str 
    phone:str 
class UserFieldPublic(UserPublic):
    company_name:str 
    company_code:str

fake_id = uuid.uuid4()

def test_user_public():
    with patch('api.log.get_current_active_user',return_value=User(
        id=fake_id,username='amine',email='amine@gmail.com',register_as='author',phone='555'
    )):
        response = client.get('/user_me')
        assert response.status_code==200
        data = response.json()
        assert data['id']==str(fake_id)
        assert data['username']=='amine'
        assert data['email']=='amine@gmail.com'
        assert data['register_as']=='author'
        assert data['phone'] =='555'
def test_user_public_field():
    with patch('api.log.get_current_active_user',return_value=User(
        id=fake_id,username='amine',email='amine@gmail.com',register_as='author',phone='555',company_name='babil',company_code='5555'
    )):
        response = client.get('/user_me')
        assert response.status_code==200
        data = response.json()
        assert data['id']==str(fake_id)
        assert data['username']=='amine'
        assert data['email']=='amine@gmail.com'
        assert data['register_as']=='author'
        assert data['phone'] =='555'
        assert data['company_name']=='babil'
        assert data['company_code'] == '5555'

def test_authenticate_user():
    with patch('api.log.get_current_active_user',return_value=User(
        id=fake_id,username='amine',email='amine@gmail.com',register_as='author',phone='555'
    )):
        response = client.get('/authenticate')
        assert response.status_code==200 
        data =response.json()
        assert data['is_authenticated']==True 
    response = client.get('/authenticate')
    data = response.json()
    assert data['is_authenticated']==False






