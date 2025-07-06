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
    # Check if the user exists and the password is correct
    user_info = requests.get("http://backend_api:8000/users/", params={"username": information.email})
    print("User info response:", user_info.status_code, user_info.text)
    if user_info.status_code != 200:
        raise HTTPException(status_code=user_info.status_code, detail=user_info.text)
    users = user_info.json()
    print("User information:", users)
    if users is None:
        raise HTTPException(status_code=401, detail="No username found in the database.") 
    if users["Password"] != information.password:
        raise HTTPException(status_code=402, detail="Incorrect password.")
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "message": "User logged in successfully.",
            "user": users
        })
    )

@app.post("/user/register/", description= "Register of the User", tags=["User"])
def user_register(information: UserLoginRegister):
    # Checks if the user already exists and, if not, creates it
    result = requests.post("http://backend_api:8000/users/", json={
        "username": information.email,
        "password": information.password,
        "userType": "Estudiante"
    })
    print("User register response:", result.status_code, result.text)
    if result.status_code == 401:
        raise HTTPException(status_code=401, detail="Username already exists.")
    elif result.status_code != 200:
        raise HTTPException(status_code=result.status_code, detail=result.text)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "message": "User registered successfully."
        })
    )