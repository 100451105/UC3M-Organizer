from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, confloat, conint, constr
from typing import Literal, Optional
from datetime import datetime
import database_controller as Database

app = FastAPI()
db = Database.db

""" Definimos los payloads que esperamos para cada base de datos"""
class CreateUser(BaseModel):
    username: constr(min_length=0,max_length=100)
    password: constr(min_length=0,max_length=100)
    userType: Literal["Profesor","Estudiante","Administrador","Otros"]

    class Config:
        extra = "forbid"

class UpdateUser(BaseModel):
    username: constr(min_length=0,max_length=100)
    password: constr(min_length=0,max_length=100)
    userType: Literal["Profesor","Estudiante","Administrador","Otros"]
    userId: int

class CreateSubject(BaseModel):
    credits: confloat(ge=0,le=12,multiple_of=0.1)
    semester: conint(ge=1,le=2)
    year: conint(ge=1,le=4)

    class Config:
        extra = "forbid"

class UpdateSubject(BaseModel):
    credits: confloat(ge=0,le=12,multiple_of=0.1)
    semester: conint(ge=1,le=2)
    year: conint(ge=1,le=4)
    subjectId: int

class CreateActivity(BaseModel):
    name: constr(min_length=0,max_length=1024)
    description: constr(min_length=0,max_length=1024)
    type: Literal["Examen","Actividad","Laboratorio","Clase","Otros"]
    hours: conint(ge=0)
    subjectId: int
    endOfActivity: datetime = None

    class Config:
        extra = "forbid"

class UpdateActivity(BaseModel):
    name: constr(min_length=0,max_length=1024)
    description: constr(min_length=0,max_length=1024)
    type: Literal["Examen","Actividad","Laboratorio","Clase","Otros"]
    hours: conint(ge=0)
    subjectId: int
    endOfActivity: datetime = None
    activityId: int

class AssignUserToSubject(BaseModel):
    userId: int
    subjectId: int

class AssignCoordinatorToSubject(BaseModel):
    adminId: int
    subjectId: int

class DeleteUser(BaseModel):
    userId: int

class DeleteSubject(BaseModel):
    subjectId: int

class DeleteActivity(BaseModel):
    activityId: int

""" User Endpoints """

@app.get("/users/", description= "GetUsers", tags=["Users"])
def read_users(userId: Optional[int] = None):
    result = db.get_users(userId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/users/subject/", description= "GetUsersOfSubject", tags=["Users"])
def read_users_of_subject(subjectId: int = None):
    result = db.get_users_of_subject(subjectId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.post("/users/", description= "CreateUser", tags=["Users"])
def create_user(item: CreateUser):
    result = db.create_user(item.username, item.password, item.userType)
    match result[0]:
        case 200:
            return {"result": result[0], "affected": result[1]}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")

@app.put("/users/", description= "UpdateUser", tags=["Users"])
def update_user(item: UpdateUser):
    result = db.update_user(item.username, item.password, item.userType, item.userId)
    match result[0]:
        case 200:
            return {"result": result[0], "affected": result[1]}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")

@app.post("/users/delete/", description= "DeleteUser", tags=["Users"])
def delete_user(item: DeleteUser):
    result = db.delete_user(item.userId)
    match result:
        case 200:
            return {"result": result, "message": "User succesfully deleted"}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
        
""" Subject Endpoints """

@app.get("/subjects/", description= "GetSubjects", tags=["Subjects"])
def read_subjects(subjectId: Optional[int] = None):
    result = db.get_subjects(subjectId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/subjects/user", description= "GetSubjectsPerUser", tags=["Subjects"])
def read_subjects_of_user(userId: int = None):
    result = db.get_subjects_of_user(userId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.post("/subjects/", description= "CreateSubject", tags=["Subjects"])
def create_subject(item: CreateSubject):
    result = db.create_subject(item.credits, item.semester, item.year)
    match result[0]:
        case 200:
            return {"result": result[0], "affected": result[1]}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")

@app.put("/subjects/", description= "UpdateSubject", tags=["Subjects"])
def update_subject(item: UpdateSubject):
    result = db.update_subject(item.credits, item.semester, item.year, item.subjectId)
    match result[0]:
        case 200:
            return {"result": result[0], "affected": result[1]}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")

@app.post("/subjects/delete/", description= "DeleteSubject", tags=["Subjects"])
def delete_subject(item: DeleteSubject):
    result = db.delete_subject(item.subjectId)
    match result:
        case 200:
            return {"result": result, "message": "Subject succesfully deleted"}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
        
@app.post("/subjects/assign/user/", description= "AssignUserToSubject", tags=["Subjects"])
def assign_user_to_subject(item: AssignUserToSubject):
    result = db.assign_user_to_subject(item.userId,item.subjectId)
    print(result)
    match result:
        case 200:
            return {"result": result, "message": "Assigned user to subject succesfully"}
        case 401:
            raise HTTPException(status_code=401, detail="User doesn't exist")
        case 402:
            raise HTTPException(status_code=402, detail="Subject doesn't exist")
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")

@app.post("/subjects/assign/coordinator/", description= "AssignCoordinatorToSubject", tags=["Subjects"])
def assign_coordinator_to_subject(item: AssignCoordinatorToSubject):
    result = db.assign_coordinator_to_subject(item.adminId,item.subjectId)
    match result:
        case 200:
            return {"result": result, "message": "Assigned coordinator to subject succesfully"}
        case 401:
            return HTTPException(status_code=401, detail="Subject doesn't exist")
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
        
""" Activity Endpoints """

@app.get("/activities/", description= "GetActivities", tags=["Activities"])
def read_activities(activityId: Optional[int] = None):
    result = db.get_activities(activityId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/activities/subject/", description= "GetActivitiesOfSubject", tags=["Activities"])
def read_activities_of_subject(subjectId: int):
    result = db.get_activities_of_subject(subjectId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/activities/user/", description= "GetActivitiesOfUser", tags=["Activities"])
def read_activities_of_user(userId: int):
    result = db.get_activities_of_user(userId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.post("/activities/", description= "CreateActivity", tags=["Activities"])
def create_activity(item: CreateActivity):
    result = db.create_activity(item.name, item.description, item.type, item.hours, item.subjectId, item.endOfActivity)
    match result[0]:
        case 200:
            return {"result": result[0], "affected": result[1]}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")

@app.put("/activities/", description= "UpdateActivity", tags=["Activities"])
def update_activity(item: UpdateActivity):
    result = db.update_activity(item.name, item.description, item.type, item.hours, item.subjectId, item.activityId, item.endOfActivity)
    match result[0]:
        case 200:
            return {"result": result[0], "affected": result[1]}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")

@app.post("/activities/delete/", description= "DeleteActivity", tags=["Activities"])
def delete_activity(item: DeleteActivity):
    result = db.delete_activity(item.activityId)
    match result:
        case 200:
            return {"result": result, "message": "Activity succesfully deleted"}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
        

