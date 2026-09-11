from pwdlib  import PasswordHash 
import secrets 
import string





password_hash = PasswordHash.recommended()



def verify_password(password,hashed_password):
    return password_hash.verify(password,hashed_password)


def hash_password(password:str):
    return password_hash.hash(password)

def hash_token(access_token:str):
    return password_hash.hash(access_token)



def generate_account_id(provider_name:str):
    chars = string.ascii_uppercase + string.digits

    account_id = provider_name + ''.join(secrets.choice(chars) for _ in range(13))

    return account_id

def generate_client_id():
    chars = string.ascii_uppercase + string.digits 
    client_id = ''.join(secrets.choice(chars) for _ in range(15))

    return client_id


def generate_secret_key():
    chars = string.ascii_uppercase + string.digits 
    secret_key = ''.join(secrets.choice(chars) for _ in range(30))
    
    return secret_key


def generate_merchant_id(provider_name:str):
    chars = string.ascii_uppercase + string.digits
    
    merchant_id = provider_name + ''.join(secrets.choice(chars) for _ in range(10))

    return merchant_id

