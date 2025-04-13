import mysql.connector
from mysql.connector import Error
import time
import os

""" Clase de Base de Datos que alberga todos los procesos necesarios para operar con ella"""
class Database:
    def __init__(self):
        self.connection = None
        self.isConnected = False

    def connect(self):
        attempts = 0
        while attempts < 5:
            try:
                self.connection = mysql.connector.connect(
                    host= os.getenv("DATABASE_HOST"),
                    user= os.getenv("DATABASE_USER"),
                    password= os.getenv("DATABASE_PASSWORD"),
                    database= os.getenv("DATABASE_NAME")
                )
                self.isConnected = True
                return
            except Error as e:
                attempts +=1
                print(e)
                time.sleep(2)
        
        print("Could not connect correctly to the database after 5 attempts")
        self.isConnected = False
    
    def get_connection(self):
        if not self.isConnected:
            self.connect()
        return self.connection if self.isConnected else None
    
    """ Operaciones permitidas en base de datos de lectura (casos de uso basicos) """
    
    def get_users(self, userId=None):
        """  Leer usuarios (uno o todos) """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        if userId:
            cursor.execute("SELECT * FROM person WHERE Id = %s;",(userId))
            result = cursor.fetchone()
        else:
            cursor.execute("SELECT * FROM person;")
            result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_subjects(self, subjectId=None):
        """  Leer asignaturas (una o todas) """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        if subjectId:
            cursor.execute("SELECT * FROM subject WHERE IdSubject = %s;",(subjectId))
            result = cursor.fetchone()
        else:
            cursor.execute("SELECT * FROM subject;")
            result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_activities(self, activityId=None):
        """  Leer actividades (una o todas) """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        if activityId:
            cursor.execute("SELECT * FROM activity WHERE IdActivity = %s;",(activityId))
            result = cursor.fetchone()
        else:
            cursor.execute("SELECT * FROM activity;")
            result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_subjects_of_user(self, userId):
        """  Leer para un usuario las asignaturas que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT SubjectID, SubjectCredits, Semester, Year FROM vPersonSubjectInfo WHERE UserID = %s;",(userId))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_users_of_subject(self, subjectId):
        """ Leer para una asignatura los usuarios que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT UserID, Username, UserType FROM vPersonSubjectInfo WHERE SubjectID = %s GROUP BY UserID, Username, UserType;",(subjectId))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_activities_of_subject(self,subjectId):
        """ Leer para una asignatura las distintas actividades que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT ActivityID, ActivityName, ActivityType, Description, EstimatedHours, EndOfActivity FROM vSubjectActivityInfo WHERE SubjectID = %s;",(subjectId))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_activities_of_user(self,userId):
        """ Leer para una asignatura las distintas actividades que tiene """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT ActivityID, ActivityName, ActivityType, Description, EstimatedHours, EndOfActivity FROM vUserInterestedActivities WHERE UserID = %s",(userId))
        result = cursor.fetchall()
        cursor.close()
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
            cursor.execute("CALL usp_CreateOrUpdateUser(%s,%s,%s,NULL,@p_newId);",(username,userType,password))
            cursor.execute("SELECT @p_newId as userId;")
            result = cursor.fetchone()
            userId = result["userId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            if err.errno == 45000:
                return int(err.msg.lower), None
            else:
                return 505, None
        cursor.close()
        return 200, userId
    
    def update_user(self,username,password,userType,usernameId):
        """ Actualizar usuario """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newId = NULL;")
            cursor.execute("CALL usp_CreateOrUpdateUser(%s,%s,%s,%s,@p_newId);",(username,userType,password,usernameId))
            cursor.execute("SELECT @p_newId as userId;")
            result = cursor.fetchone()
            userId = result["userId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            if err.errno == 45000:
                return int(err.msg.lower), None
            else:
                return 505, None
        cursor.close()
        return 200, userId
    
    def create_subject(self,credits,semester,year):
        """ Crear asignatura """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newIdSubject = NULL;")
            cursor.execute("CALL usp_CreateOrUpdateSubject(%s,%s,%s,NULL,@p_newIdSubject);",(credits,semester,year))
            cursor.execute("SELECT @p_newIdSubject as subjectId;")
            result = cursor.fetchone()
            subjectId = result["subjectId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            if err.errno == 45000:
                return int(err.msg.lower), None
            else:
                return 505, None
        cursor.close()
        return 200, subjectId
    
    def update_subject(self,credits,semester,year,subjectId):
        """ Actualizar asignatura """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newIdSubject = NULL;")
            cursor.execute("CALL usp_CreateOrUpdateSubject(%s,%s,%s,%s,@p_newIdSubject);",(credits,semester,year,subjectId))
            cursor.execute("SELECT @p_newIdSubject as subjectId;")
            result = cursor.fetchone()
            subjectId = result["subjectId"] if result else None            
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            if err.errno == 45000:
                return int(err.msg.lower)
            else:
                return 505
        cursor.close()
        return 200, subjectId
    
    def create_activity(self,name,description,type,hours,subjectId,endOfAct=None):
        """ Crear actividad """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newId = NULL;")
            if endOfAct:
                cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,%s,NULL,@p_newId);",(name,description,type,hours,subjectId,endOfAct))
            else:
                cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,NULL,NULL,@p_newId);",(name,description,type,hours,subjectId))
            cursor.execute("SELECT @p_newId as activityId;")
            result = cursor.fetchone()
            activityId = result["activityId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            if err.errno == 45000:
                return int(err.msg.lower), None
            else:
                return 505, None
        cursor.close()
        return 200, activityId
    
    def update_activity(self,name,description,type,hours,subjectId,activityId,endOfAct=None):
        """ Actualizar actividad """
        connection = self.get_connection()
        if not connection:
            return 503, None
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET @p_newId = NULL;")
            if endOfAct:
                cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,%s,%s,@p_newId);",(name,description,type,hours,subjectId,endOfAct,activityId))
            else:
                cursor.execute("CALL usp_CreateOrUpdateActivity(%s,%s,%s,%s,%s,NULL,%s,@p_newId);",(name,description,type,hours,subjectId,activityId))
            cursor.execute("SELECT @p_newId as activityId;")
            result = cursor.fetchone()
            activityId = result["activityId"] if result else None
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            if err.errno == 45000:
                return int(err.msg.lower), None
            else:
                return 505, None
        cursor.close()
        return 200, activityId
    
    def assign_user_to_subject(self,userId,subjectId):
        """ Asignar asignatura a un usuario """
        connection = self.get_connection()
        if not connection:
            return 503
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("CALL usp_AssignSubjectToUser(%s,%s);",(userId,subjectId))
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            cursor.close()
            if err.errno == 45000:
                return int(err.msg.lower)
            else:
                return 505
        cursor.close()
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
            if err.errno == 45000:
                return int(err.msg.lower)
            else:
                return 505
        cursor.close()
        return 200
    
    """ Delete operations:
    - User
    - Subject
    - Activity
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
            if err.errno == 45000:
                return int(err.msg.lower)
            else:
                return 505
        cursor.close()
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
            if err.errno == 45000:
                return int(err.msg.lower)
            else:
                return 505
        cursor.close()
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
            if err.errno == 45000:
                return int(err.msg.lower)
            else:
                return 505
        cursor.close()
        return 200


db = Database()