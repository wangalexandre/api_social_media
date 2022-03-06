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
from .routers import post, user


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