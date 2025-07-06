from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, conint, model_validator
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, List
from datetime import date
import requests

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" Payload definition """
class UserLoginRegister(BaseModel):
    email: str
    password: str

""" Main Logic Endpoints """
@app.post("/user/login/", description= "Login of the User", tags=["User"])
def user_login(information: UserLoginRegister):
    """
    # Check if the user exists and the password is correct
    user_info = requests.get("http://backend_api:8000/users/")
    if user_info.status_code != 200:
        raise HTTPException(status_code=500, detail="Error retrieving user information.")
    users = user_info.json()
    for user in users:
        if user["email"] == information.email:
            if user["password"] == information.password:
                return JSONResponse(
                    status_code=200,
                    content=jsonable_encoder({
                        "result": 200,
                        "message": "User logged in successfully.",
                        "user": user
                    })
                )
            else:
                raise HTTPException(status_code=401, detail="Incorrect password.")
    """
    # Simulate a successful login for demonstration purposes
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "message": "User logged in successfully.",
            "user": {
                "email": information.email,
                "name": "Test User"
            }
        })
    )