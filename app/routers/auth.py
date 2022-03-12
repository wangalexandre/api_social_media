from os import access
from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schemas, utils, oauth2
import psycopg2
from psycopg2.extras import RealDictCursor
import time

router = APIRouter(tags=['Authentication'])

# connecting to database
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi_social_media', user='postgres', 
        password='admin', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Database connection was successful')
        break
    except Exception as error:
        print('Connecting to database failed')
        print('Error: ', error)
        time.sleep(2)


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    # more secure client credentials input approach, need to pass data in form-data vs raw json in postman
    # using OAuth2PasswordRequestFormm, it stores by default client inputs in username and password
    cursor.execute("""SELECT * FROM users WHERE email = %s """, (user_credentials.username,))
    user = cursor.fetchone()

    if not user or not utils.verify(user_credentials.password, user['password']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')
    
    # create token
    # return token

    # creating signature
    access_token = oauth2.create_access_token(data = {'user_id': user['id']})

    return {'access_token': access_token, 'token_type': 'bearer'}    