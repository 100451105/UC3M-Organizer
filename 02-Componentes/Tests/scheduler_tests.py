import unittest
import sys
import os
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import date

sys.path.append(os.path.abspath("Codigo/Scheduler/"))
from Codigo.Scheduler.api_controller import app

client = TestClient(app)

""" Configuración global para los tests. Para cada test, se especifica: 
    - ID
    - resultCode
    - Número de soluciones (solutionsExpected) 
    - Comparación de EndDate (endDateCompare)
"""

TEST_CASES_CONFIG = {
    "test_aggresive_default_case": {
        "id": 1,
        "resultCode": 200,
        "solutionsExpected": 1,
        "endDateCompare": "NA"
    },
    "test_aggresive_more_solutions": {
        "id": 2,
        "resultCode": 200,
        "solutionsExpected": 5,
        "endDateCompare": "NA"
    },
    "test_aggresive_later_enddate": {
        "id": 3,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "greater"
    },
    "test_aggresive_earlier_enddate": {
        "id": 4,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "lower"
    },
    "test_aggresive_default_case_startdate": {
        "id": 5,
        "resultCode": 200,
        "solutionsExpected": 1,
        "endDateCompare": "NA"
    },
    "test_aggresive_later_enddate_startdate": {
        "id": 6,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "greater"
    },
    "test_aggresive_earlier_enddate_startdate": {
        "id": 7,
        "resultCode": 401,
        "solutionsExpected": 1,
        "endDateCompare": "lower"
    },
    "test_calm_default_case": {
        "id": 8,
        "resultCode": 200,
        "solutionsExpected": 1,
        "endDateCompare": "NA"
    },
    "test_calm_more_solutions": {
        "id": 9,
        "resultCode": 200,
        "solutionsExpected": 5,
        "endDateCompare": "NA"
    },
    "test_calm_later_enddate": {
        "id": 10,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "greater"
    },
    "test_calm_earlier_enddate": {
        "id": 11,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "lower"
    },
    "test_calm_default_case_startdate": {
        "id": 12,
        "resultCode": 200,
        "solutionsExpected": 1,
        "endDateCompare": "NA"
    },
    "test_calm_later_enddate_startdate": {
        "id": 13,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "greater"
    },
    "test_calm_earlier_enddate_startdate": {
        "id": 14,
        "resultCode": 401,
        "solutionsExpected": 1,
        "endDateCompare": "lower"
    },
    "test_complete_default_case": {
        "id": 15,
        "resultCode": 200,
        "solutionsExpected": 1,
        "endDateCompare": "NA"
    },
    "test_complete_more_solutions": {
        "id": 16,
        "resultCode": 200,
        "solutionsExpected": 5,
        "endDateCompare": "NA"
    },
    "test_complete_later_enddate": {
        "id": 17,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "greater"
    },
    "test_complete_earlier_enddate": {
        "id": 18,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "lower"
    },
    "test_complete_default_case_startdate": {
        "id": 19,
        "resultCode": 200,
        "solutionsExpected": 1,
        "endDateCompare": "NA"
    },
    "test_complete_later_enddate_startdate": {
        "id": 20,
        "resultCode": 201,
        "solutionsExpected": 1,
        "endDateCompare": "greater"
    },
    "test_complete_earlier_enddate_startdate": {
        "id": 21,
        "resultCode": 401,
        "solutionsExpected": 1,
        "endDateCompare": "lower"
    },
    "test_result_400": {
        "id": 22,
        "resultCode": 400,
        "solutionsExpected": 1,
        "endDateCompare": "NA"
    },
    "test_result_505": {
        "id": 23,
        "resultCode": 505,
        "solutionsExpected": 1,
        "endDateCompare": "NA"
    },
}


def load_json_input(testId: int):
    """ Función para precargar un input en un archivo json"""
    filename = f"TestInput_{testId}.json"
    path = os.path.join(os.path.dirname(__file__), "TestInputs", "Scheduler", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class TestAggresiveScheduler(unittest.TestCase):
    
    def run_scheduler_test(self):
        """Funcion generica para cada test"""
        method_name = self._testMethodName
        case = TEST_CASES_CONFIG[method_name]

        input = load_json_input(case["id"])
        response = client.post("/scheduler/logic/activity/", json=input)
        result = response.json()
        resultCode = result.get("result")
        # Validación para cada resultCode probado
        match resultCode:
            case 200:
                self.assertEqual(response.status_code, case["resultCode"])
                match case["solutionsExpected"]:
                    case 1:
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertEqual(new_date, original_date, f"Solution 1 newEndDate {new_date} is not equal to {original_date}")
                    case _:
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), case["solutionsExpected"])
                        for i, solution in enumerate(solutions):
                            new_date, original_date = date.fromisoformat(solution.get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                            self.assertEqual(new_date, original_date, f"Solution {i} newEndDate {new_date} is not equal to {original_date}")
            case 201:
                self.assertEqual(response.status_code, case["resultCode"])
                match case["endDateCompare"]:
                    case "greater":
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertGreater(new_date, original_date, f"Solution 1 newEndDate {new_date} is not greater than {original_date}")
                    case "lower":
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertLess(new_date, original_date, f"Solution 1 newEndDate {new_date} is not less than {original_date}")
            case 401:
                self.assertEqual(response.status_code, case["resultCode"])
                self.assertEqual(result["detail"], "Could not assign the activity to the scheduler successfully.")

    def test_aggresive_default_case(self):
        """01 Test: Agresiva, una solución, sin startDate, resultCode 200"""
        self.run_scheduler_test()

    def test_aggresive_more_solutions(self):
        """02 Test: Agresiva, más de una solución, sin startDate, resultCode 200"""
        self.run_scheduler_test()
        
    def test_aggresive_later_enddate(self):
        """03 Test: Agresiva, una solución, sin startDate, resultCode 201, endDate posterior"""
        self.run_scheduler_test()

    def test_aggresive_earlier_enddate(self):
        """04 Test: Agresiva, una solución, sin startDate, resultCode 201, endDate anterior"""
        self.run_scheduler_test()

    def test_aggresive_default_case_startdate(self):
        """05 Test: Agresiva, una solución, con startDate, resultCode 200"""
        self.run_scheduler_test()
        
    def test_aggresive_later_enddate_startdate(self):
        """06 Test: Agresiva, una solución, con startDate, resultCode 201, endDate posterior"""
        self.run_scheduler_test()

    def test_aggresive_earlier_enddate_startdate(self):
        """07 Test: Agresiva, una solución, con startDate, resultCode 401, endDate anterior"""
        self.run_scheduler_test()
    
class TestCalmScheduler(unittest.TestCase):
    
    def run_scheduler_test(self):
        """Funcion generica para cada test"""
        method_name = self._testMethodName
        case = TEST_CASES_CONFIG[method_name]

        input = load_json_input(case["id"])
        response = client.post("/scheduler/logic/activity/", json=input)
        result = response.json()
        resultCode = result.get("result")
        # Validación para cada resultCode probado
        match resultCode:
            case 200:
                self.assertEqual(response.status_code, case["resultCode"])
                match case["solutionsExpected"]:
                    case 1:
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertEqual(new_date, original_date, f"Solution 1 newEndDate {new_date} is not equal to {original_date}")
                    case _:
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), case["solutionsExpected"])
                        for i, solution in enumerate(solutions):
                            new_date, original_date = date.fromisoformat(solution.get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                            self.assertEqual(new_date, original_date, f"Solution {i} newEndDate {new_date} is not equal to {original_date}")
            case 201:
                self.assertEqual(response.status_code, case["resultCode"])
                match case["endDateCompare"]:
                    case "greater":
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertGreater(new_date, original_date, f"Solution 1 newEndDate {new_date} is not greater than {original_date}")
                    case "lower":
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertLess(new_date, original_date, f"Solution 1 newEndDate {new_date} is not less than {original_date}")
            case 401:
                self.assertEqual(response.status_code, case["resultCode"])
                self.assertEqual(result["detail"], "Could not assign the activity to the scheduler successfully.")

    def test_calm_default_case(self):
        """08 Test: Calmada, una solución, sin startDate, resultCode 200"""
        self.run_scheduler_test()

    def test_calm_more_solutions(self):
        """09 Test: Calmada, más de una solución, sin startDate, resultCode 200"""
        self.run_scheduler_test()
        
    def test_calm_later_enddate(self):
        """10 Test: Calmada, una solución, sin startDate, resultCode 201, endDate posterior"""
        self.run_scheduler_test()

    def test_calm_earlier_enddate(self):
        """11 Test: Calmada, una solución, sin startDate, resultCode 201, endDate anterior"""
        self.run_scheduler_test()

    def test_calm_default_case_startdate(self):
        """12 Test: Calmada, una solución, con startDate, resultCode 200"""
        self.run_scheduler_test()
        
    def test_calm_later_enddate_startdate(self):
        """13 Test: Calmada, una solución, con startDate, resultCode 201, endDate posterior"""
        self.run_scheduler_test()

    def test_calm_earlier_enddate_startdate(self):
        """14 Test: Calmada, una solución, con startDate, resultCode 401, endDate anterior"""
        self.run_scheduler_test()
    
class TestCompleteScheduler(unittest.TestCase):
    
    def run_scheduler_test(self):
        """Funcion generica para cada test"""
        method_name = self._testMethodName
        case = TEST_CASES_CONFIG[method_name]

        input = load_json_input(case["id"])
        response = client.post("/scheduler/logic/activity/", json=input)
        result = response.json()
        resultCode = result.get("result")
        # Validación para cada resultCode probado
        match resultCode:
            case 200:
                self.assertEqual(response.status_code, case["resultCode"])
                match case["solutionsExpected"]:
                    case 1:
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertEqual(new_date, original_date, f"Solution 1 newEndDate {new_date} is not equal to {original_date}")
                    case _:
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), case["solutionsExpected"])
                        for i, solution in enumerate(solutions):
                            new_date, original_date = date.fromisoformat(solution.get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                            self.assertEqual(new_date, original_date, f"Solution {i} newEndDate {new_date} is not equal to {original_date}")
            case 201:
                self.assertEqual(response.status_code, case["resultCode"])
                match case["endDateCompare"]:
                    case "greater":
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertGreater(new_date, original_date, f"Solution 1 newEndDate {new_date} is not greater than {original_date}")
                    case "lower":
                        solutions = result.get("solutions")
                        self.assertEqual(len(solutions), 1)
                        new_date, original_date = date.fromisoformat(solutions[0].get("newEndDate")), date.fromisoformat(input.get("activity").get("endOfActivity"))
                        self.assertLess(new_date, original_date, f"Solution 1 newEndDate {new_date} is not less than {original_date}")
            case 401:
                self.assertEqual(response.status_code, case["resultCode"])
                self.assertEqual(result["detail"], "Could not assign the activity to the scheduler successfully.")

    def test_complete_default_case(self):
        """15 Test: Completa, una solución, sin startDate, resultCode 200"""
        self.run_scheduler_test()

    def test_complete_more_solutions(self):
        """16 Test: Completa, más de una solución, sin startDate, resultCode 200"""
        self.run_scheduler_test()
        
    def test_complete_later_enddate(self):
        """17 Test: Completa, una solución, sin startDate, resultCode 201, endDate posterior"""
        self.run_scheduler_test()

    def test_complete_earlier_enddate(self):
        """18 Test: Completa, una solución, sin startDate, resultCode 201, endDate anterior"""
        self.run_scheduler_test()

    def test_complete_default_case_startdate(self):
        """19 Test: Completa, una solución, con startDate, resultCode 200"""
        self.run_scheduler_test()
        
    def test_complete_later_enddate_startdate(self):
        """20 Test: Completa, una solución, con startDate, resultCode 201, endDate posterior"""
        self.run_scheduler_test()

    def test_complete_earlier_enddate_startdate(self):
        """21 Test: Completa, una solución, con startDate, resultCode 401, endDate anterior"""
        self.run_scheduler_test()
    
class TestResultCodeAPI(unittest.TestCase):

    def run_scheduler_test(self, mock_search_day_to_assign):
        """Funcion generica para cada test"""
        method_name = self._testMethodName
        case = TEST_CASES_CONFIG[method_name]

        input = load_json_input(case["id"])
        mock_search_day_to_assign.return_value = case["resultCode"], None
        response = client.post("/scheduler/logic/activity/", json=input)
        result = response.json()
        resultCode = result.get("result")
        # Validación para cada resultCode probado
        match resultCode:
            case 400:
                self.assertEqual(response.status_code, case["resultCode"])
                self.assertEqual(result["detail"], "Unknown Code")
            case 505:
                self.assertEqual(response.status_code, case["resultCode"])
                self.assertEqual(result["detail"], "Unknown Error")


    @patch("scheduler.Scheduler.search_day_to_assign")
    def test_result_400(self, mock_search_day_to_assign):
        """22 Test: Codigo 400 en la respuesta"""
        self.run_scheduler_test(mock_search_day_to_assign)

    @patch("scheduler.Scheduler.search_day_to_assign")
    def test_result_505(self, mock_search_day_to_assign):
        """23 Test: Codigo 505 en la respuesta"""
        self.run_scheduler_test(mock_search_day_to_assign)


if __name__ == "__main__":
    unittest.main()
