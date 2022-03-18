from wsgiref import headers
from jose import JWTError, jwt
from datetime import date, datetime, timedelta
from . import schemas
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .database import cursor

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


# SECRET_KEY
# hash algo to be used
# expiration time of token

SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    # creating a copy of passed dict
    to_encode = data.copy()
    # adding expiration time for token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # passing expiration attribute to to_encode variable
    to_encode.update({"exp": expire})
    # hashing the signature with payload, secret and algorithm used
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# function to verify access token
def verify_access_token(token: str, credentials_exceptions):
    # good practice to use try for any code that can throw an error
    try:
        # decoding access token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get('user_id')

        if id is None:
            raise credentials_exceptions
        # validating extracted id with schema
        token_data = schemas.TokenData(id=id)
    
    except JWTError:
        raise credentials_exceptions

    # returning user id
    return token_data


# function that will be called for any operations that require user to be logged in
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})

    token = verify_access_token(token, credentials_exceptions)
    cursor.execute("""SELECT id, email, created_at FROM users WHERE id = %s """, (token.id, ))
    user = cursor.fetchone()

    # returns a dict with user_id, email etc
    return user