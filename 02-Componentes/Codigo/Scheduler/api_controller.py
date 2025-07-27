from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, conint, model_validator
from typing import Literal, List, Optional
from datetime import date
import scheduler as SchedulerController

app = FastAPI()

""" Definición del formato de las peticiones """
class Activity(BaseModel):
    estimatedHours: conint(ge=0)
    strategy: Literal["Agresiva","Calmada","Completa"]
    startOfActivity: Optional[date] = None
    endOfActivity: date

    class Config:
        extra = "forbid"

class Calendar(BaseModel):
    calendarDate: date
    dayType: Literal["Festivo","Normal"]
    totalHoursBusy: conint(ge=0)

class ScheduleActivity(BaseModel):
    activity: Activity
    calendar: List[Calendar]

    @model_validator(mode="after")
    def check_calendar_days(self) -> 'ScheduleActivity':
        """ Comprueba la cantidad de días de calendario que necesita tener la petición """
        activity = self.activity
        calendar = self.calendar

        if activity.startOfActivity:
            expected = (activity.endOfActivity - activity.startOfActivity).days + 1 + 3
            if len(calendar) < expected:
                raise ValueError(f"Call expected {expected} days on the Calendar list. It was given {len(calendar)}.")
        else:
            if len(calendar) != 21:
                raise ValueError(f"Call expected 21 days on the Calendar list. It was given {len(calendar)}.")
        
        return self

""" Endpoints relacionados con la Lógica del Organizador """
@app.post("/scheduler/logic/activity/", description= "CreateCalendarScheduledActivities", tags=["Scheduler"])
def create_calendar_scheduled_activities(information: ScheduleActivity):
    scheduler = SchedulerController.Scheduler()
    result, solutions = scheduler.search_day_to_assign(
            activity=information.activity.dict(),
            calendar=[calendar.dict() for calendar in information.calendar])
    match result:
        case 200:
            return {
                "result": result, 
                "message": "Assigned activity to the scheduler successfully.",
                "solutions": solutions
                }
        case 201:
            return JSONResponse(status_code=201,content=jsonable_encoder({
                "result": result, 
                "message": "Assigned activity to the scheduler successfully. However, the endOfActivity given had to be changed in order to schedule it properly.",
                "solutions": solutions
                }))
        case 401:
            raise HTTPException(status_code=401, detail="Could not assign the activity to the scheduler successfully.")
        case 505:
            raise HTTPException(status_code=505, detail="Unknown Error")
        case _:
            raise HTTPException(status_code=400, detail="Unknown Code")