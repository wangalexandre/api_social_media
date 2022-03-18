from fastapi import FastAPI, Response, status, HTTPException, APIRouter
from .. import schemas, utils
from ..database import conn, cursor

# defining router to be referenced in main.py
# Prefix is used to shorten path in path operations
# Tags are used for grouping path ops in documentation
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


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
    cursor.execute("""SELECT * FROM users WHERE id = %s """, (str(id), ))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id: {id} was not found')
    
    return user    