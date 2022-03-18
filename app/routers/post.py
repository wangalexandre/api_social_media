from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from .. import schemas, oauth2
from ..database import conn, cursor
from typing import List, Optional

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# get all posts stored in db
# current user is defined as int type but doesn't really matter as it will return a dictionary either way
@router.get('/', response_model=List[schemas.Post])
def get_posts(current_user: int = Depends(oauth2.get_current_user), 
                limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # print(current_user['email'])
    # cursor.execute allows you to use raw SQL
    cursor.execute("""
                    SELECT p.*, u.id, u.email, u.created_at 
                    FROM public.posts p 
                    JOIN public.users u ON p.user_id = u.id
                    WHERE (%s IS NULL OR p.title LIKE %s)
                    LIMIT %s OFFSET %s
                    """, (search, f'%{search}%', limit, skip))

    # use cursor.fetchall() if retrieving multiple items
    posts = cursor.fetchall()
    
    return posts

# create new post based on client input
# Depends function verifies if user is authenticated for the function to be called
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user)):
    print(current_user['id'])
    # using %s placeholders instead of {post.title} directly in the SQL code to prevent SQL injection attacks. %s sanitizes the variable
    cursor.execute("""
                        INSERT INTO posts (title, content, published, user_id) 
                        VALUES (%s, %s, %s, %s) RETURNING * """, 
                        (post.title, post.content, post.published, current_user['id']))
    
    # use cursor.fetchone() to retrieve only the created post
    new_post = cursor.fetchone()
    print(new_post['id'])
    
    cursor.execute("""
                    SELECT p.*, u.id, u.email, u.created_at 
                    FROM public.posts p 
                    JOIN public.users u ON p.user_id = u.id
                    WHERE p.id = %s
                    """, (new_post['id'], ))
    new_post_with_id = cursor.fetchone()

    # need to commit to push changes to database, everything above is staging the changes
    conn.commit()

    return new_post_with_id


# retrieve a specific post based on id - path parameter
@router.get('/{id}', response_model=schemas.Post)
# specifying that the id input should be an integer to validate user input
def get_post(id: int, current_user: int = Depends(oauth2.get_current_user)):
    # need to convert id to str to make sure SQL query interprets it, cannot interpret integer
    cursor.execute("""
                        SELECT p.*, u.id, u.email, u.created_at 
                        FROM public.posts p JOIN public.users u 
                        ON p.user_id = u.id 
                        WHERE p.id = %s """, (str(id), ))
    post = cursor.fetchone()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} was not found')
    
    return post


# delete a specific post based on id - path parameter
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cursor.fetchone()

    if deleted_post == None:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} does not exist')

    # check on user_id, to allow only owner of the post to delete its posts
    if deleted_post['user_id'] != current_user['id']:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Not autheorized to perform requested action')

    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update post based on id
@router.put('/{id}', response_model=schemas.PostBase)
def update_post(id: int, post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
    (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()

    if updated_post == None:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} does not exist')
    
    if updated_post['user_id'] != current_user['id']:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Not autheorized to perform requested action')
        
    conn.commit()
    return updated_post