from fastapi import APIRouter, Depends, status, HTTPException, Response
from .. import schemas, utils
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


@router.post('/login')
def login(user_credentials: schemas.UserLogin):
    cursor.execute("""SELECT * FROM users WHERE email = %s """, (user_credentials.email,))
    user = cursor.fetchone()

    if not user or not utils.verify(user_credentials.password, user['password']):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Invalid Credentials')
    
    # create token
    # return token

    return user    