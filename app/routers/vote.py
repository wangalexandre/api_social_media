from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from .. import schemas, oauth2
from ..database import conn, cursor

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, current_user: int = Depends(oauth2.get_current_user)):
    # check if post exists in posts table
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", 
                    (vote.post_id, ))
    # store query result in variable
    post_query = cursor.fetchone()
    if not post_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post {vote.post_id} does not exist')
    
    # query vote to check if it's existing or not
    cursor.execute("""SELECT * FROM votes WHERE user_id = %s AND post_id = %s""", 
                    (current_user['id'], vote.post_id))
    # store query result in variable
    vote_query = cursor.fetchone()

    # check if vote is upvoting
    if vote.dir:
        # check if vote exists in db, if exists then throw error
        if vote_query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f'user {current_user["id"]} has already voted on post {vote.post_id}')
        # if vote doesn't exist, create new vote entry in db
        cursor.execute("""INSERT INTO votes (user_id, post_id) VALUES (%s, %s)""", 
                                    (current_user['id'], vote.post_id))
        conn.commit()
        return {'message': 'successfully added vote'}
    # if vote is note upvoting
    else:
        # if vote doesn't exist in db
        if not vote_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'vote {vote.post_id} does not exist')
        # if vote exist in db, delete the vote entry - withdrawing the vote
        cursor.execute("""DELETE FROM votes WHERE user_id = %s AND post_id = %s RETURNING * """, 
                                    (current_user['id'], vote.post_id))
        conn.commit()
        return {'message': 'successfully deleted vote'}