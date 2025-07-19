from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, conint, constr, model_validator, confloat
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

class UserUpdate(BaseModel):
    username: constr(min_length=0,max_length=100)
    password: constr(min_length=0,max_length=100)
    userType: Literal["Profesor","Estudiante","Administrador","Otros"]
    seeAllSubjects: bool
    userId: int

class UpdateSubject(BaseModel):
    credits: confloat(ge=0,le=12,multiple_of=0.1)
    semester: conint(ge=1,le=2)
    year: conint(ge=1,le=4)
    name: constr(min_length=0,max_length=1024)
    subjectId: int
    coordinator: constr(min_length=0,max_length=100)

class ConfirmActivity(BaseModel):
    activityId: int

""" User Action Endpoints """
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

@app.post("/user/update/", description= "User Update", tags=["User"])
def user_update(info: UserUpdate):
    # Checks if the user already exists and, if not, creates it
    user_info = requests.put("http://backend_api:8000/users/", json={
        "username": info.username,
        "password": info.password,
        "userType": info.userType,
        "seeAllSubjects": info.seeAllSubjects,
        "userId": info.userId
    })

    if user_info.status_code != 200:
        raise HTTPException(status_code=user_info.status_code, detail=user_info.text)
    users = user_info.json()
    print(users);
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "userInformation": users["affected"]
        })
    )

""" Endpoints de información """

@app.get("/user/info/", description= "User Information", tags=["User"])
def user_information(userId: int):
    # Checks if the user already exists and, if not, creates it
    user_info = requests.get("http://backend_api:8000/users/id", params={
        "userId": userId
    })
    if user_info.status_code != 200:
        raise HTTPException(status_code=user_info.status_code, detail=user_info.text)
    users = user_info.json()
    print(users);
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

@app.get("/subject/info/", description= "Subject Information", tags=["Subject"])
def subject_information():
    # Checks if the user already exists and, if not, creates it
    subject_info = requests.get("http://backend_api:8000/subjects/")
    if subject_info.status_code != 200:
        raise HTTPException(status_code=subject_info.status_code, detail=subject_info.text)
    subjectList = subject_info.json()
    print(subjectList)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "subjectList": subjectList
        })
    )

@app.post("/subject/update/", description= "Subject Update/Creation", tags=["Subject"])
def subject_information(information: UpdateSubject):
    print(information)
    return_message_OK = "Subject has been created/updated correctly."
    # Checks if the user already exists and, if not, creates it
    subject_info = requests.post("http://backend_api:8000/subjects/", json={
        "credits": information.credits,
        "semester": information.semester,
        "year": information.year,
        "name": information.name,
        "subjectId": information.subjectId
    })
    if subject_info.status_code != 200:
        raise HTTPException(status_code=subject_info.status_code, detail=subject_info.text)
    if information.coordinator:
        coordinator_info = requests.get("http://backend_api:8000/users/", params={"username": information.coordinator})
        if coordinator_info.status_code != 200:
            raise HTTPException(status_code=coordinator_info.status_code, detail="Couldn't assign the coordinator properly to the subject (subject is created but coordinator not assigned). Due to: " + coordinator_info.text)
        coordinator = coordinator_info.json()
        if coordinator is None:
            raise HTTPException(status_code=401, detail="Coordinator '" + information.coordinator + "' does not exist in the database. Subject is created but no coordinator is assigned.")
        print(coordinator)
        assign_coordinator_to_subject = requests.post("http://backend_api:8000//subjects/assign/coordinator/", json={
            "adminId": coordinator["Id"],
            "subjectId": information.subjectId
        })
        if assign_coordinator_to_subject.status_code != 200:
            raise HTTPException(status_code=assign_coordinator_to_subject.status_code, detail=assign_coordinator_to_subject.text)
        return_message_OK += " Coordinator has been assigned correctly to the subject."
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "message": return_message_OK
        })
    )

@app.get("/activities/pending/info/", description= "Pending Activities Information", tags=["Activities"])
def pending_activities_information(userId: int):
    # Checks if the user already exists and, if not, creates it
    pending_activities_information = requests.get("http://backend_api:8000/scheduler/activities/pending/", params={
        "userId": userId
    })
    if pending_activities_information.status_code != 200:
        raise HTTPException(status_code=pending_activities_information.status_code, detail=pending_activities_information.text)
    pending_list = pending_activities_information.json()
    print(pending_list)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "pendingList": pending_list
        })
    )

@app.post("/activities/confirm/", description= "Confirm Activity", tags=["Activities"])
def confirm_activity(information: ConfirmActivity):
    # Checks if the user already exists and, if not, creates it
    confirmed_activity = requests.post("http://backend_api:8000/activities/change/status/", json={
        "activityId": information.activityId,
        "newStatus": "Asignado"
    })
    if confirmed_activity.status_code != 200:
        raise HTTPException(status_code=confirmed_activity.status_code, detail=confirmed_activity.text)
    confirmation_message = confirmed_activity.json()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "message": confirmation_message
        })
    )