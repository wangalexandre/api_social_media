from fastapi import FastAPI, Response, status, HTTPException, APIRouter
from sqlite3 import Cursor
from .. import schemas, utils
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# defining router to be referenced in main.py
# Prefix is used to shorten path in path operations
# Tags are used for grouping path ops in documentation
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

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


# create new user
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate):
    
    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    cursor.execute("""INSERT INTO users (email, password) VALUES (%s, %s) RETURNING * """, 
    (user.email, user.password))
    
    # use cursor.fetchone() to retrieve only the created post
    new_user = cursor.fetchone()
    
    # need to commit to push changes to database, everything above is staging the changes
    conn.commit()

    return new_user


# retrieve user based on id
@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int):
    cursor.execute("""SELECT * FROM users WHERE id = %s """, (str(id)))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id: {id} was not found')
    
    return user    