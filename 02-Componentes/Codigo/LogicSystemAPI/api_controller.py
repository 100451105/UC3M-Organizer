from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, conint, constr, model_validator, confloat
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal, List, Optional
from datetime import date, timedelta, datetime
import requests
import json

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

class UpdateActivity(BaseModel):
    activityName: constr(min_length=0,max_length=1024)
    description: constr(min_length=0,max_length=1024)
    type: Literal["Examen","Actividad","Laboratorio","Clase","Otros"]
    estimatedHours: conint(ge=1)
    strategy: Literal["Agresiva","Calmada","Completa"]
    subjectId: int
    endOfActivity: date
    startOfActivity: Optional[date]
    activityId: int = None

class ConfirmActivity(BaseModel):
    activityId: int

class UserAssignment(BaseModel):
    userId: int
    assigned: bool

class AssignUserToSubject(BaseModel):
    users: List[UserAssignment]
    subjectId: int

    @model_validator(mode="after")
    def validate_assignments(self):
        if not self.users:
            raise ValueError("Debe asignar al menos un usuario.")
        return self
    
def obtener_dia_semana(fecha_str):
    # Convertir string a objeto datetime
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
    
    # Obtener el nombre del día en español
    dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    return dias[fecha.weekday()]

""" User Action Endpoints """
@app.post("/user/login/", description= "Login of the User", tags=["User"])
def user_login(information: UserLoginRegister):
    # Check if the user exists and the password is correct
    user_info = requests.get("http://backend_api:8000/users/", params={"username": information.email})
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
    if users is None:
        raise HTTPException(status_code=401, detail="No username found in the database with the userId given")
    subject_info_of_user = requests.get("http://backend_api:8000/subjects/user", params={
        "userId": userId
    })
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
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "activities": activity
        })
    )

@app.get("/activities/info/subject/", description= "Activities Information Based On Subject", tags=["Activity"])
def activities_information_based_on_subject(subjectId: int):
    # Checks if the user already exists and, if not, creates it
    activity_info = requests.get("http://backend_api:8000/activities/subject/",params={
        "subjectId": subjectId
    })
    if activity_info.status_code != 200:
        raise HTTPException(status_code=activity_info.status_code, detail=activity_info.text)
    activity = activity_info.json()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "activities": activity
        })
    )

@app.get("/activities/specific/info/", description= "Activities Specific Information", tags=["Activity"])
def activity_information(activityId: int):
    # Checks if the user already exists and, if not, creates it
    activity_info = requests.get("http://backend_api:8000/activities/", params={
        "activityId": activityId
    })
    print(activity_info)
    if activity_info.status_code != 200:
        raise HTTPException(status_code=activity_info.status_code, detail=activity_info.text)
    activityInfo = activity_info.json()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "activityInfo": activityInfo
        })
    )

@app.get("/calendar/info/daily/", description= "Calendar Daily Information", tags=["Calendar"])
def calendar_daily_information():
    # Checks if the user already exists and, if not, creates it
    calendar_info = requests.get("http://backend_api:8000/scheduler/calendar")
    if calendar_info.status_code != 200:
        raise HTTPException(status_code=calendar_info.status_code, detail=calendar_info.text)
    calendar = calendar_info.json()
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
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "subjectList": subjectList
        })
    )

@app.get("/subject/specific/info/", description= "Subject Specific Information", tags=["Subject"])
def subject_information(subjectId: int):
    # Checks if the user already exists and, if not, creates it
    subject_info = requests.get("http://backend_api:8000/subjects/", params={
        "subjectId": subjectId
    })
    print(subject_info)
    if subject_info.status_code != 200:
        raise HTTPException(status_code=subject_info.status_code, detail=subject_info.text)
    subjectInfo = subject_info.json()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "subjectInfo": subjectInfo
        })
    )

@app.get("/subject/coordinator/info/", description= "Subjects of a Coordinator", tags=["Subject"])
def subject_coordinator_information(userId: int = None):
    # Checks if the user already exists and, if not, creates it
    subject_coordinator_info = 0
    if userId is not None:
        subject_coordinator_info = requests.get("http://backend_api:8000/subjects/coordinator/", params={
            "userId": userId
        })
    else:
        subject_coordinator_info = requests.get("http://backend_api:8000/subjects/")
    if subject_coordinator_info.status_code != 200:
        raise HTTPException(status_code=subject_coordinator_info.status_code, detail=subject_coordinator_info.text)
    subjectList = subject_coordinator_info.json()
    print(subjectList)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "subjectList": subjectList
        })
    )

@app.get("/subject/assigned/info/", description= "Users Assigned To Subject", tags=["Subject"])
def subject_information(subjectId: int):
    # Checks if the user already exists and, if not, creates it
    subject_info = requests.get("http://backend_api:8000/users/assigned/subject/", params={
        "subjectId": subjectId
    })
    if subject_info.status_code != 200:
        raise HTTPException(status_code=subject_info.status_code, detail=subject_info.text)
    userList = subject_info.json()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "userList": userList
        })
    )

@app.post("/subject/update/", description= "Subject Update/Creation", tags=["Subject"])
def subject_update(information: UpdateSubject):
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
        assign_coordinator_to_subject = requests.post("http://backend_api:8000/subjects/assign/coordinator/", json={
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

@app.post("/activities/update/", description= "Update/Create Activity and Attemp Organize", tags=["Activity"])
def activity_information(information: UpdateActivity):
    # 1. Llamada para crear/actualizar actividad (activityId)
    activity_confirmation = 0
    if information.activityId:
        activity_confirmation = requests.put("http://backend_api:8000/activities/", json={
            "name": information.activityName,
            "description": information.description,
            "type": information.type,
            "estimatedHours": information.estimatedHours,
            "strategy": information.strategy,
            "subjectId": information.subjectId,
            "startOfActivity": information.startOfActivity if information.startOfActivity is None else information.startOfActivity.isoformat(),
            "endOfActivity": information.endOfActivity.isoformat(),
            "activityId": information.activityId
        })
    else:
        activity_confirmation = requests.post("http://backend_api:8000/activities/", json={
            "name": information.activityName,
            "description": information.description,
            "type": information.type,
            "estimatedHours": information.estimatedHours,
            "strategy": information.strategy,
            "subjectId": information.subjectId,
            "startOfActivity": information.startOfActivity if information.startOfActivity is None else information.startOfActivity.isoformat(),
            "endOfActivity": information.endOfActivity.isoformat()
        })
    if activity_confirmation.status_code != 200:
        raise HTTPException(status_code=activity_confirmation.status_code, detail=activity_confirmation.text)
    activity_info = activity_confirmation.json()
    activityId = activity_info["affected"]
    print(activityId)
    # 2. Llamada para conseguir los días
    start_date = (
        information.startOfActivity
        if information.startOfActivity is not None
        else information.endOfActivity - timedelta(days=14)
    )
    calendar_information = requests.get("http://backend_api:8000/scheduler/dates/", params={
        "startDate": start_date.isoformat(),
        "endDate": information.endOfActivity.isoformat()
    })
    if calendar_information.status_code != 200:
        raise HTTPException(status_code=calendar_information.status_code, detail=calendar_information.text)
    calendar_information = calendar_information.json()

    calendar_info_for_scheduler = []
    for day in calendar_information:
        activities = json.loads(day["Activities"])
        totalHours = sum(activity["Hours"] or 0 for activity in activities)
        calendar_info_for_scheduler.append({
            "calendarDate": day["CalendarDate"],
            "dayType": day["DayType"],
            "totalHoursBusy": totalHours
        })
    
    activity_for_scheduler = {
        "estimatedHours": information.estimatedHours,
        "strategy": information.strategy,
        "startOfActivity": information.startOfActivity if information.startOfActivity is None else information.startOfActivity.isoformat(),
        "endOfActivity": information.endOfActivity.isoformat()
    }

    # 3. Realizar llamada al scheduler para organizar la actividad

    scheduler_info = {
        "activity": activity_for_scheduler,
        "calendar": calendar_info_for_scheduler
    }
    scheduler_new_info = requests.post("http://scheduler:8001/scheduler/logic/activity/", json=scheduler_info)
    scheduler_response = scheduler_new_info.json()
    

    # 4. Organizar información llegada del scheduler, colocar el status de la actividad dependiendo del response code y actualizar actividad con nueva información
    status = 0
    chosen_solution = 0
    newEndDate = 0
    if (scheduler_new_info.status_code == 200 or scheduler_new_info.status_code == 201):
        status = "Confirmar"
        chosen_solution = scheduler_response["solutions"][0]
        newEndDate = chosen_solution["newEndDate"]
    else:
        status = "Sin Asignar"
        chosen_solution = None
        newEndDate = None

    activity_status_confirmation = requests.post("http://backend_api:8000/activities/change/status/", json={
        "activityId": activityId,
        "newStatus": status,
        "newEndDate": newEndDate,
        "newStartDate": start_date.isoformat()
    })
    if activity_status_confirmation.status_code != 200:
        raise HTTPException(status_code=activity_status_confirmation.status_code, detail=activity_status_confirmation.text)

    # 5. Actualizar el calendario y el organizador con la salida del scheduler
    if chosen_solution is None:
        raise HTTPException(status_code=scheduler_new_info.status_code, detail=scheduler_new_info.text)

    newCalendarPayload = []
    newSchedulePayload = []
    for date in chosen_solution["schedule"]:
        newSchedulePayload.append({
            "calendarDate": date["calendarDate"],
            "hours": date["assignedHours"],
            "activityId": activityId
        })
        
    for date in chosen_solution["modifiedCalendar"]:
        newCalendarPayload.append({
            "calendarDate": date["calendarDate"],
            "dayType": date["dayType"],
            "weekDay": obtener_dia_semana(date["calendarDate"]),
            "status": date["status"]
        })
    
    calendar_creation_confirmation = requests.post("http://backend_api:8000/scheduler/days/", json=newCalendarPayload)
    schedule_creation_confirmation = requests.post("http://backend_api:8000/scheduler/days/activities/", json=newSchedulePayload)

    if calendar_creation_confirmation.status_code != 200:
        raise HTTPException(status_code=calendar_creation_confirmation.status_code, detail=calendar_creation_confirmation.text)
    if schedule_creation_confirmation.status_code != 200:
        raise HTTPException(status_code=schedule_creation_confirmation.status_code, detail=schedule_creation_confirmation.text)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "message": "Ok"
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

@app.post("/subject/assignments/", description= "Change Assignments of User", tags=["Subject"])
def change_user_assigments_to_subject(information: AssignUserToSubject):
    # Checks if the user already exists and, if not, creates it
    print("Petition arrived: ", information.dict())
    confirmed_assignments = requests.post("http://backend_api:8000/subjects/assign/user/", json=information.dict())
    if confirmed_assignments.status_code != 200:
        raise HTTPException(status_code=confirmed_assignments.status_code, detail=confirmed_assignments.text)
    confirmation_message = confirmed_assignments.json()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "result": 200,
            "message": confirmation_message
        })
    )

