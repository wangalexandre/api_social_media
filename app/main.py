from enum import auto
from sqlite3 import Cursor
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import schemas, utils


app = FastAPI()


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


# in FastAPI, this is a Path Operation - similar to route in Flask
# decorator is the @ symbol, identifying the root path of API
# .get is the HTTP method
@app.get("/")
# function, naming should reflect the operation
def root():
    return {"message": "Welcome to Social Media API!"}

# get all posts stored in db
@app.get('/posts', response_model=List[schemas.Post])
def get_posts():
    # cursor.execute allows you to use raw SQL
    cursor.execute("""SELECT * FROM posts """)
    
    # use cursor.fetchall() if retrieving multiple items
    posts = cursor.fetchall()
    
    return posts

# create new post based on client input
@app.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate):
    # using %s placeholders instead of {post.title} directly in the SQL code to prevent SQL injection attacks. %s sanitizes the variable
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    (post.title, post.content, post.published))
    
    # use cursor.fetchone() to retrieve only the created post
    new_post = cursor.fetchone()
    
    # need to commit to push changes to database, everything above is staging the changes
    conn.commit()

    return new_post



# retrieve a specific post based on id - path parameter
@app.get('/posts/{id}', response_model=schemas.Post)
# specifying that the id input should be an integer to validate user input
def get_post(id: int):
    # need to convert id to str to make sure SQL query interprets it, cannot interpret integer
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    post = cursor.fetchone()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} was not found')
    
    return post


# delete a specific post based on id - path parameter
@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} does not exist')

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# update post based on id
@app.put('/posts/{id}', response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} does not exist')

    return updated_post

# create new user
@app.post('/users', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
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

    