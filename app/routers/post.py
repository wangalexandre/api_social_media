from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from sqlite3 import Cursor
from .. import schemas, oauth2
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from typing import List

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
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


# get all posts stored in db
@router.get('/', response_model=List[schemas.Post])
def get_posts(current_user: int = Depends(oauth2.get_current_user)):
    print(current_user['email'])
    # cursor.execute allows you to use raw SQL
    cursor.execute("""SELECT * FROM posts """)
    
    # use cursor.fetchall() if retrieving multiple items
    posts = cursor.fetchall()
    
    return posts

# create new post based on client input
# Depends function verifies if user is authenticated for the function to be called
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user)):
    print(current_user)
    # using %s placeholders instead of {post.title} directly in the SQL code to prevent SQL injection attacks. %s sanitizes the variable
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    (post.title, post.content, post.published))
    
    # use cursor.fetchone() to retrieve only the created post
    new_post = cursor.fetchone()
    
    # need to commit to push changes to database, everything above is staging the changes
    conn.commit()

    return new_post



# retrieve a specific post based on id - path parameter
@router.get('/{id}', response_model=schemas.Post)
# specifying that the id input should be an integer to validate user input
def get_post(id: int, current_user: int = Depends(oauth2.get_current_user)):
    # need to convert id to str to make sure SQL query interprets it, cannot interpret integer
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    post = cursor.fetchone()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} was not found')
    
    return post


# delete a specific post based on id - path parameter
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} does not exist')

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# update post based on id
@router.put('/{id}', response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} does not exist')

    return updated_post