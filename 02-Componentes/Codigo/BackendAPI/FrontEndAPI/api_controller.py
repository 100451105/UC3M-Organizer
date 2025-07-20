from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, confloat, conint, constr, model_validator
from typing import Literal, Optional, List
from datetime import date
import database_controller as Database

app = FastAPI()
db = Database.db

""" Payload definition """
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
    seeAllSubjects: bool
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
    name: constr(min_length=0,max_length=1024)
    subjectId: int

class CreateActivity(BaseModel):
    name: constr(min_length=0,max_length=1024)
    description: constr(min_length=0,max_length=1024)
    type: Literal["Examen","Actividad","Laboratorio","Clase","Otros"]
    estimatedHours: conint(ge=0)
    strategy: Literal["Agresiva","Calmada","Completa"]
    subjectId: int
    startOfActivity: date = None
    endOfActivity: date = None

    class Config:
        extra = "forbid"

class UpdateActivity(BaseModel):
    name: constr(min_length=0,max_length=1024)
    description: constr(min_length=0,max_length=1024)
    type: Literal["Examen","Actividad","Laboratorio","Clase","Otros"]
    estimatedHours: conint(ge=0)
    strategy: Literal["Agresiva","Calmada","Completa"]
    subjectId: int
    startOfActivity: date = None
    endOfActivity: date = None
    activityId: int

class CreateCalendarDay(BaseModel):
    calendarDate: date
    dayType: Literal["Festivo","Normal"]
    weekDay: Literal["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"]
    status: Literal["Ocupado","Libre"]

class CreateCalendarScheduledActivities(BaseModel):
    calendarDate: date
    hours: conint(ge=1)
    activityId: int

class DeleteCalendarScheduledActivities(BaseModel):
    calendarDate: date
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

class ChangeSubjectVisionOfUser(BaseModel):
    userId: int
    seeAllSubjects: bool

class AssignCoordinatorToSubject(BaseModel):
    adminId: int
    subjectId: int

class ChangeStatusOfActivity(BaseModel):
    activityId: int
    newStatus: Literal["Organizar","Confirmar","Sin Asignar","Asignado"]

class DeleteUser(BaseModel):
    userId: int

class DeleteSubject(BaseModel):
    subjectId: int

class DeleteActivity(BaseModel):
    activityId: int

""" User Endpoints """

@app.get("/users/", description= "GetUsers", tags=["Users"])
def read_users(username: Optional[constr(min_length=0,max_length=100)] = None):
    result = db.get_users(username)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/users/id/", description= "GetUsersThroughId", tags=["Users"])
def read_users(userId: int):
    result = db.get_users_through_id(userId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/users/assigned/subject/", description= "GetUsersStateOnSubject", tags=["Users"])
def get_users_state_on_subject(subjectId: int):
    result = db.get_users_state_on_subject(subjectId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/users/subject/", description= "GetUsersOfSubject", tags=["Users"])
def read_users_of_subject(subjectId: int = None):
    result = db.get_users_of_subject(subjectId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/users/subject/proffesors/", description= "GetUsersOfSubject", tags=["Users"])
def read_proffesors_of_subject(subjectId: int = None):
    result = db.get_proffesors_of_subject(subjectId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.post("/users/", description= "CreateUser", tags=["Users"])
def create_user(item: CreateUser):
    result = db.create_user(item.username, item.password, item.userType)
    match result[0]:
        case 200:
            return {"result": result[0], "affected": result[1]}
        case 401:
            raise HTTPException(status_code=401, detail="Username already exists")
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")

@app.put("/users/", description= "UpdateUser", tags=["Users"])
def update_user(item: UpdateUser):
    result = db.update_user(item.username, item.password, item.userType, item.seeAllSubjects, item.userId)
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
            return {"result": result, "message": "User successfully deleted"}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
    
@app.post("/users/subject/vision/", description= "ChangeSubjectVisionOfUser", tags=["Users"])
def change_subject_vision_of_user(item: ChangeSubjectVisionOfUser):
    result = db.assign_user_to_subject(item.userId,item.seeAllSubjects)
    match result:
        case 200:
            return {"result": result, "message": "Changed Subject vision of the user succesfully"}
        case 401:
            raise HTTPException(status_code=401, detail="User doesn't exist")
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

@app.get("/subjects/user/", description= "GetSubjectsPerUser", tags=["Subjects"])
def read_subjects_of_user(userId: int = None):
    result = db.get_subjects_of_user(userId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/subjects/coordinator/", description= "GetSubjectsPerUser", tags=["Subjects"])
def get_subjects_of_coordinator(userId: int):
    result = db.get_subjects_of_coordinator(userId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.post("/subjects/", description= "CreateSubject", tags=["Subjects"])
def create_subject(item: UpdateSubject):
    result = db.update_subject(item.credits, item.semester, item.year, item.name, item.subjectId)
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
    result = db.update_subject(item.credits, item.semester, item.year, item.name, item.subjectId)
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
            return {"result": result, "message": "Subject successfully deleted"}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
        
@app.post("/subjects/assign/user/", description= "AssignUserToSubject", tags=["Subjects"])
def assign_user_to_subject(item: AssignUserToSubject):
    result = db.assign_user_to_subject(item.users,item.subjectId)
    match result:
        case 200:
            return {"result": result, "message": "Changed assignments of users to subject successfully"}
        case 401:
            raise HTTPException(status_code=401, detail="Subject doesn't exist")
        case 402:
            raise HTTPException(status_code=402, detail="One of the users given in the JSON does not exist")
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
            return {"result": result, "message": "Assigned coordinator to subject successfully"}
        case 401:
            raise HTTPException(status_code=401, detail="Subject doesn't exist")
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

@app.get("/activities/info/", description= "GetActivities", tags=["Activities"])
def read_activities_main_info(actualDate: date):
    result = db.get_activities_main_info(actualDate)
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
    result = db.create_activity(item.name, item.description, item.type, item.estimatedHours, item.subjectId, item.strategy, item.startOfActivity, item.endOfActivity)
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
    result = db.update_activity(item.name, item.description, item.type, item.estimatedHours, item.subjectId, item.activityId, item.strategy, item.startOfActivity, item.endOfActivity)
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
            return {"result": result, "message": "Activity successfully deleted"}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
        
@app.post("/activities/change/status/", description= "ChangeStatusOfActivity", tags=["Activities"])
def change_status_of_activity(item: ChangeStatusOfActivity):
    result = db.change_status_of_activity(item.activityId,item.newStatus)
    match result:
        case 200:
            return {"result": result, "message": "Changed the status of the activity succesfully"}
        case 401:
            raise HTTPException(status_code=401, detail="Activity doesn't exist")
        case 402:
            raise HTTPException(status_code=402, detail="Cannot confirm an activity without it being in pending status")
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
        

""" Scheduler Endpoints """  
@app.get("/scheduler/calendar/", description= "GetCalendar", tags=["Scheduler"])
def read_calendar(calendarDate: Optional[date] = None):
    result = db.get_calendar(calendarDate)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/scheduler/date/", description= "GetSchedulerCalendarBasedOnDate", tags=["Scheduler"])
def read_calendar_scheduled_on_date(calendarDate: date):
    result = db.get_calendar_scheduled_based_on_date(calendarDate)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/scheduler/activity/", description= "GetSchedulerCalendarBasedOnActivity", tags=["Scheduler"])
def read_calendar_scheduled_on_activity(activityId: int):
    result = db.get_calendar_scheduled_based_on_activity(activityId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/scheduler/subject/", description= "GetSchedulerCalendarBasedOnSubject", tags=["Scheduler"])
def read_calendar_scheduled_on_subject(subjectId: int):
    result = db.get_calendar_scheduled_based_on_subject(subjectId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.get("/scheduler/activities/pending/", description= "GetPendingActivities", tags=["Scheduler"])
def read_pending_activities(userId: int):
    result = db.read_pending_activities(userId)
    if result == 503:
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
    return result

@app.post("/scheduler/days/", description= "CreateCalendarDays", tags=["Scheduler"])
def create_calendar_days(days: List[CreateCalendarDay]):
    result = db.create_calendar_days(days)
    match result:
        case 200:
            return {"result": result, "message": "Successfully created/updated the calendar days"}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
        
@app.post("/scheduler/days/activities/", description= "CreateCalendarScheduledActivities", tags=["Scheduler"])
def create_calendar_scheduled_activities(days: List[CreateCalendarScheduledActivities]):
    result = db.assign_activity_to_day(days)
    match result:
        case 200:
            return {"result": result, "message": "Assigned activities to the scheduler successfully"}
        case 401:
            raise HTTPException(status_code=401, detail="One of the activityIds given does not exist")
        case 402:
            raise HTTPException(status_code=402, detail="One of the calendarDates given does not exist")
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")
    
@app.post("/scheduler/activities/delete/", description= "DeleteCalendarScheduledActivities", tags=["Scheduler"])
def delete_calendar_scheduled_activities(activities: List[DeleteCalendarScheduledActivities]):
    result = db.delete_scheduled_activities(activities)
    match result:
        case 200:
            return {"result": result, "message": "Deleted scheduled activities successfully"}
        case 503:
            raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to the database")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")