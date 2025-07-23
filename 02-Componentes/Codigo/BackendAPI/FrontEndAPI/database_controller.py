import mysql.connector
from mysql.connector import Error
import json
from datetime import date
import time
import os

""" Auxiliary functions in order to help JSON deserialization"""
def date_converter(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Convierte el objeto 'date' a una cadena ISO
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")

""" Clase de Base de Datos que alberga todos los procesos necesarios para operar con ella"""
class Database:
    def __init__(self):
        self.pool = None

    def connect(self):
        attempts = 0
        while attempts < 5:
            try:
                self.pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="databasepool",
                    pool_size=5,
                    pool_reset_session=True,
                    host= os.getenv("DATABASE_HOST"),
                    user= os.getenv("DATABASE_USER"),
                    password= os.getenv("DATABASE_PASSWORD"),
                    database= os.getenv("DATABASE_NAME"),
                )
                self.isConnected = True
                return
            except Error as e:
                attempts +=1
                print(e)
                time.sleep(2)
        
        print("Could not connect correctly to the database after 5 attempts")
        self.pool = None
    
    def get_connection(self):
        if not self.pool:
            self.connect()
        if self.pool:
            return self.pool.get_connection()
        return None
    
    """ Operaciones permitidas en base de datos de lectura (casos de uso basicos) """
    
    def get_users(self, username=None):
        """  Leer usuarios (uno o todos) """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            if username:
                cursor.execute("SELECT p.Username, p.Id, p.Type, au.Password, au.SeeAllSubjects FROM person p JOIN user_authorization au ON p.Id = au.Id WHERE p.Username = %s;",(username,))
                result = cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM person;")
                result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        
        cursor.close()
        connection.close()
        return result
    
    def get_users_through_id(self, userId):
        """  Leer usuarios a través del id """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            if userId:
                cursor.execute("SELECT p.Username, p.Id, p.Type, au.Password, au.SeeAllSubjects FROM person p JOIN user_authorization au ON p.Id = au.Id WHERE p.Id = %s;",(userId,))
                result = cursor.fetchone()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_subjects(self, subjectId=None):
        """  Leer asignaturas (una o todas) """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            if subjectId:
                cursor.execute("SELECT s.*, p.Username as AdministratorName FROM subject s LEFT JOIN person p on s.IdAdministrator = p.Id WHERE s.IdSubject = %s;",(subjectId,))
                result = cursor.fetchone()
            else:
                cursor.execute("SELECT IdSubject, Name FROM subject;")
                result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_activities(self, activityId=None):
        """  Leer actividades (una o todas) """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            if activityId:
                cursor.execute("SELECT ActivityID, ActivityName, ActivityType, Description, EstimatedHours, StartOfActivity, Status, Strategy, EndOfActivity, NewEndOfActivity, SubjectName, SubjectID FROM vSubjectActivityInfo  WHERE ActivityID = %s;",(activityId,))
                result = cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM activity;")
                result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_activities_main_info(self, actualDate):
        """  Leer actividades (todas y solo la información principal) """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT ActivityId, ActivityName, ActivityType, StartOfActivity, EndOfActivity, SubjectId, SubjectName FROM vSubjectActivityInfo WHERE Status = 'Asignado' AND StartOfActivity BETWEEN DATE_FORMAT(DATE_SUB(%s, INTERVAL 1 MONTH), '%Y-%m-01') AND LAST_DAY(DATE_ADD(%s, INTERVAL 2 MONTH));", (actualDate,actualDate,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_calendar(self, calendarDate=None):
        """  Leer días del calendario (uno o varios) """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            if calendarDate:
                cursor.execute("SELECT * FROM vActivitiesPerDay WHERE CalendarDate BETWEEN STR_TO_DATE(CONCAT(IF(MONTH(%s) >= 9, YEAR(%s), YEAR(%s) - 1),'-09-01'), '%Y-%m-%d') AND STR_TO_DATE(CONCAT(IF(MONTH(%s) >= 9, YEAR(%s) + 1, YEAR(%s)),'-10-31'), '%Y-%m-%d') ORDER BY CalendarDate;",(calendarDate,calendarDate,calendarDate,calendarDate,calendarDate,calendarDate))
                result = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM vActivitiesPerDay WHERE CalendarDate = CURDATE();")
                result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_calendar_scheduled_based_on_date(self, calendarDate):
        """  Leer días del organizador en base a la fecha """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM vActivitiesPerDay WHERE CalendarDate = %s;",(calendarDate,))
            result = cursor.fetchone()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_calendar_scheduled_based_on_activity(self, activityId):
        """  Leer días del organizador en base al activityId """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT c.*, s.IdActivity as Activity, s.Hours as Hours FROM calendar c LEFT JOIN schedule s ON c.CalendarDate = s.CalendarDate WHERE s.IdActivity = %s;",(activityId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_calendar_scheduled_based_on_dates(self, startDate, endDate):
        """  Leer días del organizador en base al activityId """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM vActivitiesPerDay WHERE CalendarDate BETWEEN DATE_SUB(%s, INTERVAL 3 DAY) AND DATE_ADD(%s, INTERVAL 3 DAY);",(startDate,endDate))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_calendar_scheduled_based_on_subject(self, subjectId):
        """  Leer días del organizador en base al subjectId """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT c.*, s.IdActivity as Activity, s.Hours as Hours, a.IdSubject as Subject FROM calendar c LEFT JOIN schedule s ON c.CalendarDate = s.CalendarDate LEFT JOIN activity a ON s.IdActivity = a.IdActivity WHERE a.IdSubject = %s;",(subjectId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def read_pending_activities(self, userId):
        """  Leer días del organizador en base a la fecha """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM vPendingActivitiesInformation WHERE CoordinatorId = %s;",(userId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_subjects_of_user(self, userId):
        """  Leer para un usuario las asignaturas que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT SubjectID, SubjectName, SubjectCredits, Semester, Year FROM vPersonSubjectInfo WHERE UserID = %s;",(userId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_subjects_of_coordinator(self, userId):
        """  Leer para un usuario las asignaturas que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT SubjectID, SubjectName FROM vPersonSubjectInfo WHERE AdministratorID = %s;",(userId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_users_of_subject(self, subjectId):
        """ Leer para una asignatura los usuarios que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT UserID, Username, UserType FROM vPersonSubjectInfo WHERE SubjectID = %s GROUP BY UserID, Username, UserType;",(subjectId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_users_state_on_subject(self, subjectId):
        """ Leer para una asignatura los usuarios que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT p.Username, p.Id, p.Type, CASE WHEN pps.IdSubject IS NOT NULL THEN TRUE ELSE FALSE END AS IsAssigned FROM person p LEFT JOIN personPerSubject pps ON p.Id = pps.IdPerson AND pps.IdSubject = %s;",(subjectId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_proffesors_of_subject(self, subjectId):
        """ Leer para una asignatura los profesores que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT UserID, Username FROM vPersonSubjectInfo WHERE SubjectID = %s AND UserType = 'Profesor' GROUP BY UserID, Username;",(subjectId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_activities_of_subject(self,subjectId):
        """ Leer para una asignatura las distintas actividades que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT ActivityID, ActivityName FROM vSubjectActivityInfo WHERE SubjectID = %s;",(subjectId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    def get_activities_of_user(self,userId):
        """ Leer para una asignatura las distintas actividades que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT ActivityID, ActivityName, ActivityType, Description, EstimatedHours, StartOfActivity, EndOfActivity, FromSubjectId, FromSubjectName FROM vUserInterestedActivities WHERE UserID = %s",(userId,))
            result = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return result
    
    """ Operaciones de creación/modificación """

    def create_user(self,username,password,userType):
        """ Crear usuario """
        userId = None
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newId = NULL;")
            cursor.execute("CALL usp_CreateOrUpdateUser(%s,%s,%s,0,NULL,@p_newId);",(username,userType,password))
            cursor.execute("SELECT @p_newId as userId;")
            result = cursor.fetchone()
            userId = result["userId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            print(err.errno, int(err.msg.strip()), err.sqlstate)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200, userId
    
    def update_user(self,username,password,userType,seeAllSubjects,usernameId):
        """ Actualizar usuario """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newId = NULL;")
            cursor.execute("CALL usp_CreateOrUpdateUser(%s,%s,%s,%s,%s,@p_newId);",(username,userType,password,seeAllSubjects,usernameId))
            cursor.execute("SELECT @p_newId as userId;")
            result = cursor.fetchone()
            userId = result["userId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                print(err.sqlstate, err.errno)
                return 505, None
        cursor.close()
        connection.close()
        return 200, userId
    
    def update_subject(self,credits,semester,year,name,subjectId):
        """ Crear/Actualizar asignatura """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newIdSubject = NULL;")
            cursor.execute("CALL usp_CreateOrUpdateSubject(%s,%s,%s,%s,%s,@p_newIdSubject);",(credits,semester,year,name,subjectId))
            cursor.execute("SELECT @p_newIdSubject as subjectId;")
            result = cursor.fetchone()
            subjectId = result["subjectId"] if result else None            
            connection.commit()
        except mysql.connector.Error as err:
            print(err)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200, subjectId
    
    def create_activity(self,name,description,type,hours,subjectId,strategy,startOfAct=None,endOfAct=None):
        """ Crear actividad """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newId = NULL;")
            if startOfAct:
                if endOfAct:
                    cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,%s,%s,%s,NULL,@p_newId);",(name,description,type,hours,subjectId,endOfAct,startOfAct,strategy))
                else:
                    cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,NULL,%s,%s,NULL,@p_newId);",(name,description,type,hours,subjectId,startOfAct,strategy))
            else:
                if endOfAct:
                    cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,%s,NULL,%s,NULL,@p_newId);",(name,description,type,hours,subjectId,endOfAct,strategy))
                else:
                    cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,NULL,NULL,%s,NULL,@p_newId);",(name,description,type,hours,subjectId,strategy))
            cursor.execute("SELECT @p_newId as activityId;")
            result = cursor.fetchone()
            activityId = result["activityId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200, activityId
    
    def update_activity(self,name,description,type,hours,subjectId,activityId,strategy,startOfAct=None,endOfAct=None):
        """ Actualizar actividad """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newId = NULL;")
            if startOfAct:
                if endOfAct:
                    cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,%s,%s,%s,%s,@p_newId);",(name,description,type,hours,subjectId,endOfAct,startOfAct,strategy,activityId))
                else:
                    cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,NULL,%s,%s,%s,@p_newId);",(name,description,type,hours,subjectId,startOfAct,strategy,activityId))
            else:
                if endOfAct:
                    cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,%s,NULL,%s,%s,@p_newId);",(name,description,type,hours,subjectId,endOfAct,strategy,activityId))
                else:
                    cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,NULL,NULL,%s,%s,@p_newId);",(name,description,type,hours,subjectId,strategy,activityId))
            cursor.execute("SELECT @p_newId as activityId;")
            result = cursor.fetchone()
            activityId = result["activityId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200, activityId
    
    def create_calendar_days(self,days):
        """ Crear/Actualizar dias del calendario """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            days_json = json.dumps([day.dict() for day in days], default=date_converter)
            cursor.execute("CALL usp_CreateOrUpdateCalendarDays(%s);",(days_json,))          
            connection.commit()
        except mysql.connector.Error as err:
            print(err)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    def assign_user_to_subject(self,userList,subjectId):
        """ Asignar asignatura a un usuario """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            user_json = json.dumps([user.dict() for user in userList],default=date_converter)
            cursor.execute("CALL usp_AssignOrUnassignUsersToSubject(%s,%s);",(subjectId, user_json))
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    def change_subject_vision_of_user(self,userId,seeAllSubjects):
        """ Asignar asignatura a un usuario """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("CALL usp_ChangeSubjectVisionOfUser(%s,%s);",(userId,seeAllSubjects))
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    def assign_coordinator_to_subject(self,adminId,subjectId):
        """ Asignar asignatura a un usuario """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("CALL usp_AssignCoordinatorToSubject(%s,%s);",(subjectId,adminId))
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    def assign_activity_to_day(self,scheduledActivities):
        """ Asignar actividad al calendario """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            activities_json = json.dumps([activity.dict() for activity in scheduledActivities],default=date_converter)
            cursor.execute("CALL usp_AssignActivityToDay(%s);",(activities_json,))
            connection.commit()
        except mysql.connector.Error as err:
            print(err)
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    def change_status_of_activity(self,activityId,newStatus,newEndDate,newStartDate):
        """ Asignar asignatura a un usuario """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("CALL usp_ChangeStatusOfActivity(%s,%s,%s,%s);",(activityId,newStatus,newEndDate,newStartDate))
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    """ Delete operations:
    - User
    - Subject
    - Activity
    - Scheduler
    """

    def delete_user(self,userId):
        """ Borrar un usuario """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM user_authorization WHERE Id = %s;",(userId))
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    def delete_subject(self,subjectId):
        """ Borrar una asignatura """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM subject WHERE IdSubject = %s;",(subjectId))
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    def delete_activity(self,activityId):
        """ Borrar una actividad """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM activity WHERE IdActivity = %s;",(activityId))
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    def delete_scheduled_activities(self,activities):
        """ Borrar una actividad de scheduler """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            conditions = []
            params = []
            activities_dicts = [{**activity.dict(),
                                 "calendarDate": activity.calendarDate.strftime("%Y-%m-%d")} for activity in activities]
            for activity in activities_dicts:
                conditions.append("(CalendarDate = %s AND IdActivity = %s)")
                params.extend([activity["calendarDate"], activity["activityId"]])
            
            query = f"""
                DELETE FROM schedule
                WHERE {" OR ".join(conditions)}
            """
            cursor.execute(query,params)
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            print(err)
            if err.sqlstate == '45000' and err.errno == 1644:
                return int(err.msg.strip()), None
            else:
                return 505, None
        cursor.close()
        connection.close()
        return 200
    
    


db = Database()