import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.abspath("Codigo/BackendAPI/FrontEndAPI"))
from Codigo.BackendAPI.FrontEndAPI.api_controller import app


client = TestClient(app)

def prepare_mock_db_function(returnValue,callType):
    # Definimos el mock de base de datos genérico para todos los tests
    mock= MagicMock()
    # Dependiendo de la llamada, el valor a devolver está en una ubicación distinta
    if callType == "POST":
        mock.fetchone.return_value = returnValue
    elif callType == "GETALL":
        mock.fetchall.return_value = returnValue
    elif callType == "GETONE":
        mock.fetchone.return_value = returnValue
    elif callType == "QUERY":
        mock.execute.return_value = returnValue
    else:
        pass
    
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock
    mock_connection.is_connected.return_value = True
    return mock_connection
    

class TestGetUser(unittest.TestCase):
    # get_user
    @patch("database_controller.Database.get_connection")
    def test_get_users(self, mock_get_connection):
        """Test: Recoger todos los usuarios"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "Id": 1,
                    "Username": "100451105@alumnos.uc3m.es",
                    "Type": "Estudiante"
                },
                {
                    "Id": 2,
                    "Username": "100400000@alumnos.uc3m.es",
                    "Type": "Administrador"
                }],
            callType="GETALL"
        )
        response = client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "Id": 1,
                    "Username": "100451105@alumnos.uc3m.es",
                    "Type": "Estudiante"
                },
                {
                    "Id": 2,
                    "Username": "100400000@alumnos.uc3m.es",
                    "Type": "Administrador"
                }])
    
    @patch("database_controller.Database.get_connection")
    def test_get_user(self, mock_get_connection):
        """Test: Recoger un usuario en base al Id"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "Id": 1,
                    "Username": "100451105@alumnos.uc3m.es",
                    "Type": "Estudiante"
                }],
            callType="GETONE"
        )
        response = client.get("/users/",params={"userId": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "Id": 1,
                    "Username": "100451105@alumnos.uc3m.es",
                    "Type": "Estudiante"
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_get_user_non_connection(self, mock_get_connection):
        """Test: Recoger todos los usuarios sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/users/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")
    
class TestGetUsersOfSubject(unittest.TestCase):
    # read_users_of_subject
    @patch("database_controller.Database.get_connection")
    def test_get_users(self, mock_get_connection):
        """Test: Recoger los usuarios de una asignatura"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "UserId": 1,
                    "Username": "100451105@alumnos.uc3m.es",
                    "UserType": "Estudiante"
                }],
            callType="GETALL"
        )
        response = client.get("/users/subject/", params={"subjectId": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "UserId": 1,
                    "Username": "100451105@alumnos.uc3m.es",
                    "UserType": "Estudiante"
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_get_user_non_connection(self, mock_get_connection):
        """Test: Recoger los usuarios de una asignatura sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/users/subject/", params={"subjectId": 1})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

class TestGetSubject(unittest.TestCase):
    # get_subject
    @patch("database_controller.Database.get_connection")
    def test_get_subjects(self, mock_get_connection):
        """Test: Recoger todas las asignaturas"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "IdSubject": 1,
                    "Credits": 12,
                    "Semester": 2,
                    "Year": 3,
                    "IdAdministrator": None
                },
                {
                    "IdSubject": 2,
                    "Credits": 6,
                    "Semester": 1,
                    "Year": 3,
                    "IdAdministrator": 1
                }],
            callType="GETALL"
        )
        response = client.get("/subjects/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "IdSubject": 1,
                    "Credits": 12,
                    "Semester": 2,
                    "Year": 3,
                    "IdAdministrator":  None
                },
                {
                    "IdSubject": 2,
                    "Credits": 6,
                    "Semester": 1,
                    "Year": 3,
                    "IdAdministrator": 1
                }])
    
    @patch("database_controller.Database.get_connection")
    def test_get_subject(self, mock_get_connection):
        """Test: Recoger una asignatura en base al Id"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "IdSubject": 1,
                    "Credits": 12,
                    "Semester": 2,
                    "Year": 3,
                    "IdAdministrator": None
                }],
            callType="GETONE"
        )
        response = client.get("/subjects/",params={"subjectId": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "IdSubject": 1,
                    "Credits": 12,
                    "Semester": 2,
                    "Year": 3,
                    "IdAdministrator": None
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_get_subject_non_connection(self, mock_get_connection):
        """Test: Recoger todas las asignaturas sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/subjects/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

class TestGetSubjectsOfUser(unittest.TestCase):
    # get_subject_of_user
    @patch("database_controller.Database.get_connection")
    def test_get_subjects_of_user(self, mock_get_connection):
        """Test: Recoger todas las asignaturas de un usuario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "IdSubject": 1,
                    "Credits": 12,
                    "Semester": 2,
                    "Year": 3
                },
                {
                    "IdSubject": 2,
                    "Credits": 6,
                    "Semester": 1,
                    "Year": 3
                }],
            callType="GETALL"
        )
        response = client.get("/subjects/user/", params={"userId":1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "IdSubject": 1,
                    "Credits": 12,
                    "Semester": 2,
                    "Year": 3
                },
                {
                    "IdSubject": 2,
                    "Credits": 6,
                    "Semester": 1,
                    "Year": 3
                }])
    
    @patch("database_controller.Database.get_connection")
    def test_get_subjects_of_user_non_connection(self, mock_get_connection):
        """Test: Recoger todas las asignaturas de un usuario sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/subjects/user/", params={"userId":1})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

class TestGetActivityOfSubject(unittest.TestCase):
    # get_activities_of_subject
    @patch("database_controller.Database.get_connection")
    def test_get_activities_of_subject(self, mock_get_connection):
        """Test: Recoger todas las actividades de una asignatura"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "IdActivity": 1,
                    "Name": "Laboratorio de Tests",
                    "Description": "Laboratorio para hacer pruebas",
                    "Type": "Laboratorio",
                    "EstimatedHours": 1,
                    "EndOfActivity": None
                },
                {
                    "IdActivity": 2,
                    "Name": "Examen de Tests",
                    "Description": "Examen para hacer pruebas",
                    "Type": "Examen",
                    "EstimatedHours": 10,
                    "EndOfActivity": None
                }],
            callType="GETALL"
        )
        response = client.get("/activities/subject/", params={"subjectId":1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "IdActivity": 1,
                    "Name": "Laboratorio de Tests",
                    "Description": "Laboratorio para hacer pruebas",
                    "Type": "Laboratorio",
                    "EstimatedHours": 1,
                    "EndOfActivity": None
                },
                {
                    "IdActivity": 2,
                    "Name": "Examen de Tests",
                    "Description": "Examen para hacer pruebas",
                    "Type": "Examen",
                    "EstimatedHours": 10,
                    "EndOfActivity": None
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_get_activities_of_subject_non_connection(self, mock_get_connection):
        """Test: Recoger todas las actividades de una asignatura sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/activities/subject/", params={"subjectId":1})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

class TestGetActivityOfUser(unittest.TestCase):
    # get_activity
    @patch("database_controller.Database.get_connection")
    def test_get_activities_of_user(self, mock_get_connection):
        """Test: Recoger todas las actividades de un usuario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "IdActivity": 1,
                    "Name": "Laboratorio de Tests",
                    "Description": "Laboratorio para hacer pruebas",
                    "Type": "Laboratorio",
                    "EstimatedHours": 1,
                    "EndOfActivity": None
                },
                {
                    "IdActivity": 2,
                    "Name": "Examen de Tests",
                    "Description": "Examen para hacer pruebas",
                    "Type": "Examen",
                    "EstimatedHours": 10,
                    "EndOfActivity": None
                }],
            callType="GETALL"
        )
        response = client.get("/activities/user/", params={"userId":1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "IdActivity": 1,
                    "Name": "Laboratorio de Tests",
                    "Description": "Laboratorio para hacer pruebas",
                    "Type": "Laboratorio",
                    "EstimatedHours": 1,
                    "EndOfActivity": None
                },
                {
                    "IdActivity": 2,
                    "Name": "Examen de Tests",
                    "Description": "Examen para hacer pruebas",
                    "Type": "Examen",
                    "EstimatedHours": 10,
                    "EndOfActivity": None
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_get_activity_of_user_non_connection(self, mock_get_connection):
        """Test: Recoger todas las actividades de un usuario sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/activities/user/", params={"userId":1})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

class TestGetActivity(unittest.TestCase):
    # get_activity
    @patch("database_controller.Database.get_connection")
    def test_get_activities(self, mock_get_connection):
        """Test: Recoger todas las actividades"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "IdActivity": 1,
                    "Name": "Laboratorio de Tests",
                    "Description": "Laboratorio para hacer pruebas",
                    "Type": "Laboratorio",
                    "EstimatedHours": 1,
                    "EndOfActivity": None,
                    "IdSubject": 1
                },
                {
                    "IdActivity": 2,
                    "Name": "Examen de Tests",
                    "Description": "Examen para hacer pruebas",
                    "Type": "Examen",
                    "EstimatedHours": 10,
                    "EndOfActivity": None,
                    "IdSubject": 1
                }],
            callType="GETALL"
        )
        response = client.get("/activities/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "IdActivity": 1,
                    "Name": "Laboratorio de Tests",
                    "Description": "Laboratorio para hacer pruebas",
                    "Type": "Laboratorio",
                    "EstimatedHours": 1,
                    "EndOfActivity": None,
                    "IdSubject": 1
                },
                {
                    "IdActivity": 2,
                    "Name": "Examen de Tests",
                    "Description": "Examen para hacer pruebas",
                    "Type": "Examen",
                    "EstimatedHours": 10,
                    "EndOfActivity": None,
                    "IdSubject": 1
                }])
    
    @patch("database_controller.Database.get_connection")
    def test_get_activity(self, mock_get_connection):
        """Test: Recoger una actividad en base al Id"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "IdActivity": 1,
                    "Name": "Laboratorio de Tests",
                    "Description": "Laboratorio para hacer pruebas",
                    "Type": "Laboratorio",
                    "EstimatedHours": 1,
                    "EndOfActivity": None,
                    "IdSubject": 1
                }],
            callType="GETONE"
        )
        response = client.get("/activities/",params={"activityId": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "IdActivity": 1,
                    "Name": "Laboratorio de Tests",
                    "Description": "Laboratorio para hacer pruebas",
                    "Type": "Laboratorio",
                    "EstimatedHours": 1,
                    "EndOfActivity": None,
                    "IdSubject": 1
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_get_activity_non_connection(self, mock_get_connection):
        """Test: Recoger todas las actividades sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/activities/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

class TestCreateUser(unittest.TestCase):
    # create_user
    @patch("database_controller.Database.get_connection")
    def test_create_user(self, mock_get_connection):
        """Test: Crear un usuario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"userId": 1},
            callType="POST"
        )
        payload = {
            "username": "100451105@alumnos.uc3m.es", 
            "password": "boo", 
            "userType": "Estudiante"
        }
        response = client.post("/users/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "affected": 1})

    @patch("database_controller.Database.get_connection")
    def test_create_user_non_connection(self, mock_get_connection):
        """Test: Crear un usuario sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "username": "100451105@alumnos.uc3m.es", 
            "password": "boo", 
            "userType": "Estudiante"
        }
        response = client.post("/users/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.create_user")
    def test_create_user_unknown_error(self, mock_create_user):
        """Test: Crear un usuario habiendo un error inesperado en base de datos"""

        mock_create_user.return_value = (505, None)
        payload = {
            "username": "100451105@alumnos.uc3m.es", 
            "password": "boo", 
            "userType": "Estudiante"
        }
        response = client.post("/users/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.create_user")
    def test_create_user_unknown_code(self, mock_create_user):
        """Test: Crear un usuario habiendo un error con codigo desconocido"""

        mock_create_user.return_value = (478, None)
        payload = {
            "username": "100451105@alumnos.uc3m.es", 
            "password": "boo", 
            "userType": "Estudiante"
        }
        response = client.post("/users/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")
    
class TestUpdateUser(unittest.TestCase):
    # update_user
    @patch("database_controller.Database.get_connection")
    def test_update_user(self, mock_get_connection):
        """Test: Actualizar un usuario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"userId": 1},
            callType="POST"
        )
        payload = {
            "username": "100451105@alumnos.uc3m.es", 
            "password": "boo", 
            "userType": "Estudiante",
            "userId": 1
        }
        response = client.put("/users/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "affected": 1})

    @patch("database_controller.Database.get_connection")
    def test_update_user_non_connection(self, mock_get_connection):
        """Test: Actualizar un usuario sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "username": "100451105@alumnos.uc3m.es", 
            "password": "boo", 
            "userType": "Estudiante",
            "userId": 1
        }
        response = client.put("/users/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.update_user")
    def test_update_user_unknown_error(self, mock_update_user):
        """Test: Actualizar un usuario habiendo un error inesperado en base de datos"""
        mock_update_user.return_value = (505, None)
        payload = {
            "username": "100451105@alumnos.uc3m.es", 
            "password": "boo", 
            "userType": "Estudiante",
            "userId": 1
        }
        response = client.put("/users/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.update_user")
    def test_update_user_unknown_code(self, mock_update_user):
        """Test: Actualizar un usuario habiendo un error con codigo desconocido"""

        mock_update_user.return_value = (478, None)
        payload = {
            "username": "100451105@alumnos.uc3m.es", 
            "password": "boo", 
            "userType": "Estudiante",
            "userId": 1
        }
        response = client.put("/users/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

class TestDeleteUser(unittest.TestCase):
    # delete_user
    @patch("database_controller.Database.get_connection")
    def test_delete_user(self, mock_get_connection):
        """Test: Borrar un usuario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=0,
            callType="DELETE"
        )
        payload = {
            "userId": 1
        }
        response = client.post("/users/delete/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "message": "User successfully deleted"})

    @patch("database_controller.Database.get_connection")
    def test_delete_user_non_connection(self, mock_get_connection):
        """Test: Borrar un usuario sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "userId": 1
        }
        response = client.post("/users/delete/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.delete_user")
    def test_delete_user_unknown_error(self, mock_delete_user):
        """Test: Borrar un usuario habiendo un error inesperado en base de datos"""
        mock_delete_user.return_value = 505
        payload = {
            "userId": 1
        }
        response = client.post("/users/delete/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.delete_user")
    def test_delete_user_unknown_code(self, mock_delete_user):
        """Test: Borrar un usuario habiendo un error con codigo desconocido"""
        mock_delete_user.return_value = 478
        payload = {
            "userId": 1
        }
        response = client.post("/users/delete/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

class TestCreateSubject(unittest.TestCase):
    # create_subject
    @patch("database_controller.Database.get_connection")
    def test_create_subject(self, mock_get_connection):
        """Test: Crear una asignatura"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"subjectId": 1},
            callType="POST"
        )
        payload = {
            "credits": 12, 
            "semester": 2, 
            "year": 1,
            "subjectId": 1,
            "name": "Asignatura para probar"
        }
        response = client.post("/subjects/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "affected": 1})

    @patch("database_controller.Database.get_connection")
    def test_create_subject_non_connection(self, mock_get_connection):
        """Test: Crear una asignatura sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "credits": 12, 
            "semester": 2, 
            "year": 1,
            "subjectId": 1,
            "name": "Asignatura para probar"
        }
        response = client.post("/subjects/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.update_subject")
    def test_create_subject_unknown_error(self, mock_create_subject):
        """Test: Crear una asignatura habiendo un error inesperado en base de datos"""

        mock_create_subject.return_value = (505, None)
        payload = {
            "credits": 12, 
            "semester": 2, 
            "year": 1,
            "subjectId": 1,
            "name": "Asignatura para probar"
        }
        response = client.post("/subjects/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.update_subject")
    def test_create_subject_unknown_code(self, mock_create_subject):
        """Test: Crear una asignatura habiendo un error con codigo desconocido"""

        mock_create_subject.return_value = (478, None)
        payload = {
            "credits": 12, 
            "semester": 2, 
            "year": 1,
            "subjectId": 1,
            "name": "Asignatura para probar"
        }
        response = client.post("/subjects/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")
    
class TestUpdateSubject(unittest.TestCase):
    # update_subject
    @patch("database_controller.Database.get_connection")
    def test_update_subject(self, mock_get_connection):
        """Test: Actualizar una asignatura"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"subjectId": 1},
            callType="POST"
        )
        payload = {
            "credits": 12, 
            "semester": 2, 
            "year": 1,
            "subjectId": 1,
            "name": "Asignatura para probar"
        }
        response = client.put("/subjects/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "affected": 1})

    @patch("database_controller.Database.get_connection")
    def test_update_subject_non_connection(self, mock_get_connection):
        """Test: Actualizar una asignatura sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "credits": 12, 
            "semester": 2, 
            "year": 1,
            "subjectId": 1,
            "name": "Asignatura para probar"
        }
        response = client.put("/subjects/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.update_subject")
    def test_update_subject_unknown_error(self, mock_update_subject):
        """Test: Actualizar una asignatura habiendo un error inesperado en base de datos"""
        mock_update_subject.return_value = (505, None)
        payload = {
            "credits": 12, 
            "semester": 2, 
            "year": 1,
            "subjectId": 1,
            "name": "Asignatura para probar"
        }
        response = client.put("/subjects/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.update_subject")
    def test_update_subject_unknown_code(self, mock_update_subject):
        """Test: Actualizar una asignatura habiendo un error con codigo desconocido"""

        mock_update_subject.return_value = (478, None)
        payload = {
            "credits": 12, 
            "semester": 2, 
            "year": 1,
            "subjectId": 1,
            "name": "Asignatura para probar"
        }
        response = client.put("/subjects/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

class TestDeleteSubject(unittest.TestCase):
    # delete_subject
    @patch("database_controller.Database.get_connection")
    def test_delete_subject(self, mock_get_connection):
        """Test: Borrar una asignatura"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=0,
            callType="DELETE"
        )
        payload = {
            "subjectId": 1
        }
        response = client.post("/subjects/delete/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "message": "Subject successfully deleted"})

    @patch("database_controller.Database.get_connection")
    def test_delete_subject_non_connection(self, mock_get_connection):
        """Test: Borrar una asignatura sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "subjectId": 1
        }
        response = client.post("/subjects/delete/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.delete_subject")
    def test_delete_subject_unknown_error(self, mock_delete_subject):
        """Test: Borrar una asignatura habiendo un error inesperado en base de datos"""
        mock_delete_subject.return_value = 505
        payload = {
            "subjectId": 1
        }
        response = client.post("/subjects/delete/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.delete_subject")
    def test_delete_subject_unknown_code(self, mock_delete_subject):
        """Test: Borrar una asignatura habiendo un error con codigo desconocido"""
        mock_delete_subject.return_value = 478
        payload = {
            "subjectId": 1
        }
        response = client.post("/subjects/delete/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

class TestCreateActivity(unittest.TestCase):
    # create_activity
    @patch("database_controller.Database.get_connection")
    def test_create_activity(self, mock_get_connection):
        """Test: Crear una actividad"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"activityId": 1},
            callType="POST"
        )
        payload = {
            "name": "Laboratorio de Prácticas de Testeo", 
            "description": "Laboratorio para practicar y testear la aplicación", 
            "type": "Laboratorio",
            "estimatedHours": 0,
            "strategy": "Completa",
            "subjectId": 1
        }
        response = client.post("/activities/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "affected": 1})

    @patch("database_controller.Database.get_connection")
    def test_create_activity_non_connection(self, mock_get_connection):
        """Test: Crear una actividad sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "name": "Laboratorio de Prácticas de Testeo", 
            "description": "Laboratorio para practicar y testear la aplicación", 
            "type": "Laboratorio",
            "estimatedHours": 0,
            "strategy": "Completa",
            "subjectId": 1
        }
        response = client.post("/activities/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.create_activity")
    def test_create_activity_unknown_error(self, mock_create_activity):
        """Test: Crear una actividad habiendo un error inesperado en base de datos"""

        mock_create_activity.return_value = (505, None)
        payload = {
            "name": "Laboratorio de Prácticas de Testeo", 
            "description": "Laboratorio para practicar y testear la aplicación", 
            "type": "Laboratorio",
            "estimatedHours": 0,
            "strategy": "Completa",
            "subjectId": 1
        }
        response = client.post("/activities/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.create_activity")
    def test_create_activity_unknown_code(self, mock_create_activity):
        """Test: Crear una actividad habiendo un error con codigo desconocido"""

        mock_create_activity.return_value = (478, None)
        payload = {
            "name": "Laboratorio de Prácticas de Testeo", 
            "description": "Laboratorio para practicar y testear la aplicación", 
            "type": "Laboratorio",
            "estimatedHours": 0,
            "strategy": "Completa",
            "subjectId": 1
        }
        response = client.post("/activities/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")
    
class TestUpdateActivity(unittest.TestCase):
    # update_activity
    @patch("database_controller.Database.get_connection")
    def test_update_activity(self, mock_get_connection):
        """Test: Actualizar una actividad"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"activityId": 1},
            callType="POST"
        )
        payload = {
            "name": "Laboratorio de Prácticas de Testeo", 
            "description": "Laboratorio para practicar y testear la aplicación", 
            "type": "Laboratorio",
            "estimatedHours": 0,
            "strategy": "Completa",
            "subjectId": 1,
            "activityId": 1
        }
        response = client.put("/activities/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "affected": 1})

    @patch("database_controller.Database.get_connection")
    def test_update_activity_non_connection(self, mock_get_connection):
        """Test: Actualizar una actividad sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "name": "Laboratorio de Prácticas de Testeo", 
            "description": "Laboratorio para practicar y testear la aplicación", 
            "type": "Laboratorio",
            "estimatedHours": 0,
            "strategy": "Completa",
            "subjectId": 1,
            "activityId": 1
        }
        response = client.put("/activities/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.update_activity")
    def test_update_activity_unknown_error(self, mock_update_activity):
        """Test: Actualizar una actividad habiendo un error inesperado en base de datos"""
        mock_update_activity.return_value = (505, None)
        payload = {
            "name": "Laboratorio de Prácticas de Testeo", 
            "description": "Laboratorio para practicar y testear la aplicación", 
            "type": "Laboratorio",
            "estimatedHours": 0,
            "strategy": "Completa",
            "subjectId": 1,
            "activityId": 1
        }
        response = client.put("/activities/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.update_activity")
    def test_update_activity_unknown_code(self, mock_update_activity):
        """Test: Actualizar una actividad habiendo un error con codigo desconocido"""

        mock_update_activity.return_value = (478, None)
        payload = {
            "name": "Laboratorio de Prácticas de Testeo", 
            "description": "Laboratorio para practicar y testear la aplicación", 
            "type": "Laboratorio",
            "estimatedHours": 0,
            "strategy": "Completa",
            "subjectId": 1,
            "activityId": 1
        }
        response = client.put("/activities/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

class TestDeleteActivity(unittest.TestCase):
    # delete_activity
    @patch("database_controller.Database.get_connection")
    def test_delete_activity(self, mock_get_connection):
        """Test: Borrar una actividad"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=0,
            callType="DELETE"
        )
        payload = {
            "activityId": 1
        }
        response = client.post("/activities/delete/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "message": "Activity successfully deleted"})

    @patch("database_controller.Database.get_connection")
    def test_delete_activity_non_connection(self, mock_get_connection):
        """Test: Borrar una actividad sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "activityId": 1
        }
        response = client.post("/activities/delete/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.delete_activity")
    def test_delete_activity_unknown_error(self, mock_delete_activity):
        """Test: Borrar una actividad habiendo un error inesperado en base de datos"""
        mock_delete_activity.return_value = 505
        payload = {
            "activityId": 1
        }
        response = client.post("/activities/delete/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.delete_activity")
    def test_delete_activity_unknown_code(self, mock_delete_activity):
        """Test: Borrar una actividad habiendo un error con codigo desconocido"""
        mock_delete_activity.return_value = 478
        payload = {
            "activityId": 1
        }
        response = client.post("/activities/delete/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

class TestAssignUserToSubject(unittest.TestCase):
    # assign_user_to_subject
    @patch("database_controller.Database.get_connection")
    def test_assign_user_to_subject(self, mock_get_connection):
        """Test: Asignar un usuario a una asignatura"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=None,
            callType="ASSIGN"
        )
        payload = {
            "userId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/user/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "message": "Assigned user to subject successfully"})

    @patch("database_controller.Database.get_connection")
    def test_assign_user_to_subject_non_connection(self, mock_get_connection):
        """Test: Asignar un usuario a una asignatura sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "userId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/user/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.assign_user_to_subject")
    def test_assign_user_to_subject_unknown_error(self, mock_assign_user_to_subject):
        """Test: Asignar un usuario a una asignatura habiendo un error inesperado en base de datos"""
        mock_assign_user_to_subject.return_value = 505
        payload = {
            "userId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/user/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.assign_user_to_subject")
    def test_assign_user_to_subject_unknown_code(self, mock_assign_user_to_subject):
        """Test: Asignar un usuario a una asignatura habiendo un error con codigo desconocido"""
        mock_assign_user_to_subject.return_value = 478
        payload = {
            "userId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/user/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

    @patch("database_controller.Database.assign_user_to_subject")
    def test_assign_user_to_subject_user_not_existing(self, mock_assign_user_to_subject):
        """Test: Asignar un usuario a una asignatura sin existir el usuario"""
        mock_assign_user_to_subject.return_value = 401
        payload = {
            "userId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/user/", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "User doesn't exist")
    
    @patch("database_controller.Database.assign_user_to_subject")
    def test_assign_user_to_subject_subject_not_existing(self, mock_assign_user_to_subject):
        """Test: Asignar un usuario a una asignatura sin existir la asignatura"""
        mock_assign_user_to_subject.return_value = 402
        payload = {
            "userId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/user/", json=payload)
        self.assertEqual(response.status_code, 402)
        self.assertEqual(response.json()["detail"], "Subject doesn't exist")

class TestAssignCoordinatorToSubject(unittest.TestCase):
    # assign_coordinator_to_subject
    @patch("database_controller.Database.get_connection")
    def test_assign_coordinator_to_subject(self, mock_get_connection):
        """Test: Asignar un coordinador a una asignatura"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=None,
            callType="ASSIGN"
        )
        payload = {
            "adminId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/coordinator/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "message": "Assigned coordinator to subject successfully"})

    @patch("database_controller.Database.get_connection")
    def test_assign_coordinator_to_subject_non_connection(self, mock_get_connection):
        """Test: Asignar un coordinador a una asignatura sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = {
            "adminId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/coordinator/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.assign_coordinator_to_subject")
    def test_assign_coordinator_to_subject_unknown_error(self, mock_assign_coordinator_to_subject):
        """Test: Asignar un coordinador a una asignatura habiendo un error inesperado en base de datos"""
        mock_assign_coordinator_to_subject.return_value = 505
        payload = {
            "adminId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/coordinator/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.assign_coordinator_to_subject")
    def test_assign_coordinator_to_subject_unknown_code(self, mock_assign_coordinator_to_subject):
        """Test: Asignar un coordinador a una asignatura habiendo un error con codigo desconocido"""
        mock_assign_coordinator_to_subject.return_value = 478
        payload = {
            "adminId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/coordinator/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

    @patch("database_controller.Database.assign_coordinator_to_subject")
    def test_assign_coordinator_to_subject_subject_not_existing(self, mock_assign_coordinator_to_subject):
        """Test: Asignar un coordinador a una asignatura sin existir la asignatura"""
        mock_assign_coordinator_to_subject.return_value = 401
        payload = {
            "adminId": 1,
            "subjectId": 1
        }
        response = client.post("/subjects/assign/coordinator/", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Subject doesn't exist")
    
class TestReadCalendar(unittest.TestCase):
    # read_calendar
    @patch("database_controller.Database.get_connection")
    def test_read_calendar(self, mock_get_connection):
        """Test: Recoger multiples días del calendario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Ocupado"
                },
                {
                    "CalendarDate": "2025-04-29",
                    "DayType": "Normal",
                    "WeekDay": "Martes",
                    "Status": "Ocupado"
                }],
            callType="GETALL"
        )
        response = client.get("/scheduler/calendar/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Ocupado"
                },
                {
                    "CalendarDate": "2025-04-29",
                    "DayType": "Normal",
                    "WeekDay": "Martes",
                    "Status": "Ocupado"
                }])
    
    @patch("database_controller.Database.get_connection")
    def test_read_calendar_calendardate(self, mock_get_connection):
        """Test: Recoger un día del calendario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Ocupado"
                }],
            callType="GETONE"
        )
        response = client.get("/scheduler/calendar/", params={"calendarDate": "2025-04-28"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Ocupado"
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_read_calendar_non_connection(self, mock_get_connection):
        """Test: Recoger un día del calendario sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/scheduler/calendar/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")
    
class TestReadCalendarScheduledOnDate(unittest.TestCase):
    # read_calendar_scheduled_on_date
    @patch("database_controller.Database.get_connection")
    def test_read_calendar_scheduled_on_date(self, mock_get_connection):
        """Test: Recoger días organizados en base a la fecha"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activities": "[{\"Hours\": 2, \"Subject\": 198237, \"Activity\": 1},{\"Hours\": 1, \"Subject\": 198237, \"Activity\": 2}]"
                },
            callType="GETONE"
        )
        response = client.get("/scheduler/date/", params={"calendarDate": "2025-04-28"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activities": "[{\"Hours\": 2, \"Subject\": 198237, \"Activity\": 1},{\"Hours\": 1, \"Subject\": 198237, \"Activity\": 2}]"
                })
    
    @patch("database_controller.Database.get_connection")
    def test_read_calendar_scheduled_on_date_non_connection(self, mock_get_connection):
        """Test: Recoger días organizados en base a la fecha sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/scheduler/date/", params={"calendarDate": "2025-04-28"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")
    
class TestReadCalendarScheduledOnActivity(unittest.TestCase):
    # read_calendar_scheduled_on_activity
    @patch("database_controller.Database.get_connection")
    def test_read_calendar_scheduled_on_activity(self, mock_get_connection):
        """Test: Recoger días organizados en base al id de actividad"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activity": 1,
                    "Hours": 2
                },
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activity": 2,
                    "Hours": 2
                }],
            callType="GETALL"
        )
        response = client.get("/scheduler/activity/", params={"activityId": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activity": 1,
                    "Hours": 2
                },
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activity": 2,
                    "Hours": 2
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_read_calendar_scheduled_on_activity_non_connection(self, mock_get_connection):
        """Test: Recoger días organizados en base al id de actividad sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/scheduler/activity/", params={"activityId": 1})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")
    
class TestReadCalendarScheduledOnSubject(unittest.TestCase):
    # read_calendar_scheduled_on_subject
    @patch("database_controller.Database.get_connection")
    def test_read_calendar_scheduled_on_subject(self, mock_get_connection):
        """Test: Recoger días organizados en base al id de asignatura"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue=[
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activity": 1,
                    "Hours": 2
                },
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activity": 2,
                    "Hours": 2
                }],
            callType="GETALL"
        )
        response = client.get("/scheduler/subject/", params={"subjectId": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activity": 1,
                    "Hours": 2
                },
                {
                    "CalendarDate": "2025-04-28",
                    "DayType": "Normal",
                    "WeekDay": "Lunes",
                    "Status": "Libre",
                    "Activity": 2,
                    "Hours": 2
                }])
        
    @patch("database_controller.Database.get_connection")
    def test_read_calendar_scheduled_on_subject_non_connection(self, mock_get_connection):
        """Test: Recoger días organizados en base al id de asignatura sin conexión a base de datos"""
        mock_get_connection.return_value = None
        response = client.get("/scheduler/subject/", params={"subjectId": 1})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")
    
class TestCreateCalendarDays(unittest.TestCase):
    # create_calendar_days
    @patch("database_controller.Database.get_connection")
    def test_create_calendar_days(self, mock_get_connection):
        """Test: Crear un día organizado en el calendario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"subjectId": 1},
            callType="POST"
        )
        payload = [{
            "calendarDate": "2025-04-28",
            "dayType": "Normal",
            "weekDay": "Lunes",
            "status": "Libre"
        },
        {
            "calendarDate": "2025-04-29",
            "dayType": "Normal",
            "weekDay": "Martes",
            "status": "Libre"
        }]
        response = client.post("/scheduler/days/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "message": "Successfully created/updated the calendar days"})

    @patch("database_controller.Database.get_connection")
    def test_create_calendar_days_non_connection(self, mock_get_connection):
        """Test: Crear un día organizado en el calendario sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = [{
            "calendarDate": "2025-04-28",
            "dayType": "Normal",
            "weekDay": "Lunes",
            "status": "Libre"
        },
        {
            "calendarDate": "2025-04-29",
            "dayType": "Normal",
            "weekDay": "Martes",
            "status": "Libre"
        }]
        response = client.post("/scheduler/days/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.create_calendar_days")
    def test_create_calendar_days_unknown_error(self, mock_create_calendar_days):
        """Test: Crear un día organizado en el calendario habiendo un error inesperado en base de datos"""

        mock_create_calendar_days.return_value = 505
        payload = [{
            "calendarDate": "2025-04-28",
            "dayType": "Normal",
            "weekDay": "Lunes",
            "status": "Libre"
        },
        {
            "calendarDate": "2025-04-29",
            "dayType": "Normal",
            "weekDay": "Martes",
            "status": "Libre"
        }]
        response = client.post("/scheduler/days/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.create_calendar_days")
    def test_create_calendar_days_unknown_code(self, mock_create_calendar_days):
        """Test: Crear un día organizado en el calendario habiendo un error con codigo desconocido"""

        mock_create_calendar_days.return_value = 478
        payload = [{
            "calendarDate": "2025-04-28",
            "dayType": "Normal",
            "weekDay": "Lunes",
            "status": "Libre"
        },
        {
            "calendarDate": "2025-04-29",
            "dayType": "Normal",
            "weekDay": "Martes",
            "status": "Libre"
        }]
        response = client.post("/scheduler/days/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")
    
class TestCreateCalendarScheduledActivities(unittest.TestCase):
    # create_calendar_scheduled_activities
    @patch("database_controller.Database.get_connection")
    def test_create_calendar_scheduled_activities(self, mock_get_connection):
        """Test: Crear una actividad organizada en el calendario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"subjectId": 1},
            callType="POST"
        )
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1,
            "hours": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2,
            "hours": 3
        }]
        response = client.post("/scheduler/days/activities/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "message": "Assigned activities to the scheduler successfully"})

    @patch("database_controller.Database.get_connection")
    def test_create_calendar_scheduled_activities_non_connection(self, mock_get_connection):
        """Test: Crear una actividad organizada en el calendario sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1,
            "hours": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2,
            "hours": 3
        }]
        response = client.post("/scheduler/days/activities/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.assign_activity_to_day")
    def test_create_calendar_scheduled_activities_unknown_error(self, mock_assign_activity_to_day):
        """Test: Crear una actividad organizada en el calendario habiendo un error inesperado en base de datos"""

        mock_assign_activity_to_day.return_value = 505
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1,
            "hours": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2,
            "hours": 3
        }]
        response = client.post("/scheduler/days/activities/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.assign_activity_to_day")
    def test_create_calendar_scheduled_activities_unknown_code(self, mock_assign_activity_to_day):
        """Test: Crear una actividad organizada en el calendario habiendo un error con codigo desconocido"""

        mock_assign_activity_to_day.return_value = 478
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1,
            "hours": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2,
            "hours": 3
        }]
        response = client.post("/scheduler/days/activities/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

    @patch("database_controller.Database.assign_activity_to_day")
    def test_create_calendar_scheduled_activities_activity_not_existing(self, mock_assign_activity_to_day):
        """Test: Crear una actividad organizada en el calendario sin existir la actividad"""
        mock_assign_activity_to_day.return_value = 401
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1,
            "hours": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2,
            "hours": 3
        }]
        response = client.post("/scheduler/days/activities/", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "One of the activityIds given does not exist")
    
    @patch("database_controller.Database.assign_activity_to_day")
    def test_create_calendar_scheduled_activities_calendardate_not_existing(self, mock_assign_activity_to_day):
        """Test: Crear una actividad organizada en el calendario sin existir el día del calendario"""
        mock_assign_activity_to_day.return_value = 402
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1,
            "hours": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2,
            "hours": 3
        }]
        response = client.post("/scheduler/days/activities/", json=payload)
        self.assertEqual(response.status_code, 402)
        self.assertEqual(response.json()["detail"], "One of the calendarDates given does not exist")
    
class TestDeleteCalendarScheduledActivities(unittest.TestCase):
    # delete_calendar_scheduled_activities
    @patch("database_controller.Database.get_connection")
    def test_delete_calendar_scheduled_activities(self, mock_get_connection):
        """Test: Borrar una actividad planificada de un día del calendario"""
        mock_get_connection.return_value = prepare_mock_db_function(
            returnValue={"subjectId": 1},
            callType="POST"
        )
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2
        }]
        response = client.post("/scheduler/activities/delete/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"result": 200, "message": "Deleted scheduled activities successfully"})

    @patch("database_controller.Database.get_connection")
    def test_delete_calendar_scheduled_activities_non_connection(self, mock_get_connection):
        """Test: Borrar una actividad planificada de un día del calendario sin conexión a la base de datos"""
        mock_get_connection.return_value = None
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2
        }]
        response = client.post("/scheduler/activities/delete/", json=payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service Unavailable: Could not connect to the database")

    @patch("database_controller.Database.delete_scheduled_activities")
    def test_delete_calendar_scheduled_activities_unknown_error(self, mock_delete_scheduled_activities):
        """Test: Borrar una actividad planificada de un día del calendario habiendo un error inesperado en base de datos"""

        mock_delete_scheduled_activities.return_value = 505
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2
        }]
        response = client.post("/scheduler/activities/delete/", json=payload)
        self.assertEqual(response.status_code, 505)
        self.assertEqual(response.json()["detail"], "Unknown Error")
    
    @patch("database_controller.Database.delete_scheduled_activities")
    def test_delete_calendar_scheduled_activities_unknown_code(self, mock_delete_scheduled_activities):
        """Test: Borrar una actividad planificada de un día del calendario habiendo un error con codigo desconocido"""

        mock_delete_scheduled_activities.return_value = 478
        payload = [{
            "calendarDate": "2025-04-28",
            "activityId": 1
        },
        {
            "calendarDate": "2025-04-28",
            "activityId": 2
        }]
        response = client.post("/scheduler/activities/delete/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Unknown Code")

if __name__ == "__main__":
    unittest.main()
