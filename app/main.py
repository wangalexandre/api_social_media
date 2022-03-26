from fastapi import FastAPI
from .routers import post, user, auth, vote
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

print(settings.database_hostname)

app = FastAPI()

# create an allow list for sources allowed to interact with API, for example 'https://www.google.com' for Google domain
# can use '*' to make a public API to allow access from everyone
origins = ['*']

# CORS policy to control access from external sources
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    # specify specific path operations allowed
    allow_methods=["*"],
    allow_headers=["*"],
)


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