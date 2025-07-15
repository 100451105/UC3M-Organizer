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
            "message": "User registered successfully.",
            "userId": result.json()["affected"]
        })
    )

@app.get("/user/info/", description= "User Information", tags=["User"])
def user_information(userId: int):
    # Checks if the user already exists and, if not, creates it
    user_info = requests.get("http://backend_api:8000/users/id", params={
        "userId": userId
    })
    if user_info.status_code != 200:
        raise HTTPException(status_code=user_info.status_code, detail=user_info.text)
    print(user_info)
    users = user_info.json()
    if users is None:
        raise HTTPException(status_code=401, detail="No username found in the database with the userId given")
    subject_info_of_user = requests.get("http://backend_api:8000/subjects/user", params={
        "userId": userId
    })
    print(subject_info_of_user)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "userInformation": users,
            "subjectsOfUser": subject_info_of_user.json()
        })
    )

@app.get("/activities/info/", description= "Activities Information", tags=["Activity"])
def activities_information(actualDate: date):
    # Checks if the user already exists and, if not, creates it
    activity_info = requests.get("http://backend_api:8000/activities/info",params={
        "actualDate": actualDate
    })
    if activity_info.status_code != 200:
        raise HTTPException(status_code=activity_info.status_code, detail=activity_info.text)
    activity = activity_info.json()
    print(activity)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "activities": activity
        })
    )

@app.get("/calendar/info/daily/", description= "Calendar Daily Information", tags=["Calendar"])
def calendar_daily_information():
    # Checks if the user already exists and, if not, creates it
    calendar_info = requests.get("http://backend_api:8000/scheduler/calendar")
    if calendar_info.status_code != 200:
        raise HTTPException(status_code=calendar_info.status_code, detail=calendar_info.text)
    calendar = calendar_info.json()
    print(calendar)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "calendar": calendar
        })
    )

@app.get("/calendar/info/", description= "Calendar Information", tags=["Calendar"])
def calendar_information(calendarDate: date):
    # Checks if the user already exists and, if not, creates it
    calendar_info = requests.get("http://backend_api:8000/scheduler/calendar",params={
        "calendarDate": calendarDate
    })
    if calendar_info.status_code != 200:
        raise HTTPException(status_code=calendar_info.status_code, detail=calendar_info.text)
    calendar = calendar_info.json()
    print(calendar)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "calendar": calendar
        })
    )