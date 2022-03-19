from fastapi import FastAPI
from .routers import post, user, auth, vote
from .config import settings

print(settings.database_hostname)

app = FastAPI()


# in FastAPI, this is a Path Operation - similar to route in Flask
# decorator is the @ symbol, identifying the root path of API
# .get is the HTTP method
@app.get("/")
# function, naming should reflect the operation
def root():
    return {"message": "Welcome to Social Media API!"}


# reference the router objects in routers folder
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)