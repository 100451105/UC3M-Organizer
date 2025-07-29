from ortools.sat.python import cp_model
from datetime import timedelta


class MultipleSolutionsCollector(cp_model.CpSolverSolutionCallback):
    """ Clase relacionada con la librería ORTools para recoger múltiples soluciones con restricciones """
    def __init__(self, variables, valid_days, estimated_hours, max_solutions=5):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.valid_days = valid_days
        self.estimated_hours = estimated_hours
        self.max_solutions = max_solutions
        self.solutions = []
        self.solution_count = 0
    
    def on_solution_callback(self):
        solution = []
        totalHours = 0
        for i, var in enumerate(self.variables):
            hours = self.Value(var)
            if hours > 0:
                solution.append({
                    "calendarDate": self.valid_days[i]["calendarDate"],
                    "dayType": self.valid_days[i]["dayType"],
                    "assignedHours": hours
                })
                totalHours += hours
        if totalHours == self.estimated_hours and solution:
            self.solutions.append(solution)
            self.solution_count += 1
        if self.solution_count >= self.max_solutions:
            self.StopSearch()

    def get_solutions(self):
        return self.solutions
    
class Scheduler():
    """ Clase del Organizador con las implementaciones de las distintas lógicas de organización """
    def __check_available_days(self, activity, calendar, busy_days):
        """ Devuelve los días que se pueden utilizar para organizar y el tiempo disponible de cada día """
        fecha_inicio = activity["startDate"]
        fecha_fin = activity["endDate"]
        if not fecha_inicio:
            fecha_inicio = fecha_fin - timedelta(days=14) 
        available_days = []
        for day in calendar:
            if not (fecha_inicio <= day["calendarDate"] <= fecha_fin):
                continue
            max_total = 4 if day["dayType"] == "Normal" else 8
            ya_ocupadas = busy_days.get(day["calendarDate"], 0)
            disponible = max_total - ya_ocupadas
            if disponible > 0:
                available_days.append({
                    "calendarDate": day["calendarDate"],
                    "dayType": day["dayType"],
                    "timeAvailable": disponible
                })
        return available_days

    def __aggresive_strategy(self, activity, calendar, busy_days):
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = False
        available_days = self.__check_available_days(activity, calendar, busy_days)
        total_hours = activity["estimatedHours"]

        # Restricción: la suma de todas las horas asignadas deben cubrir todas las horas estimadas
        day_availability = []
        for i, day in enumerate(available_days):
            limit = min(day["timeAvailable"], 4 if day["dayType"] == "Normal" else 8)
            var = model.NewIntVar(0, limit, f'horas_{day["calendarDate"]}')
            day_availability.append(var)
        model.Add(sum(day_availability) == total_hours)

        # Estrategia agresiva: Prioriza siempre los primeros días del rango con todas las horas asignadas
        solver.parameters.search_branching = cp_model.FIXED_SEARCH
        model.AddDecisionStrategy(
            day_availability,
            cp_model.CHOOSE_FIRST,
            cp_model.SELECT_MAX_VALUE
        )

        callback = MultipleSolutionsCollector(day_availability, available_days, activity["estimatedHours"] , max_solutions=5)
        solver.SearchForAllSolutions(model, callback)
        result = callback.get_solutions()
        result = sorted(result, key=lambda sol: [
        -sum(entry["assignedHours"] for entry in sol[:3]),
        sol[0]["calendarDate"]])
        if result:
            return [result,activity["endDate"]]
        else:
            return None
        
    def __calm_strategy(self, activity, calendar, busy_days):
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = False
        available_days = self.__check_available_days(activity, calendar, busy_days)
        total_hours = activity["estimatedHours"]

        # Restricción: la suma de todas las horas asignadas deben cubrir todas las horas estimadas
        day_availability = []
        for i, day in enumerate(available_days):
            limit = min(day["timeAvailable"], 4 if day["dayType"] == "Normal" else 8)
            var = model.NewIntVar(0, limit, f'horas_{day["calendarDate"]}')
            day_availability.append(var)
        model.Add(sum(day_availability) == total_hours)

        # Estrategia calmada: Distribuye equitativamente las horas asignadas entre todos los días del rango
        solver.parameters.search_branching = cp_model.FIXED_SEARCH
        model.AddDecisionStrategy(
            day_availability,
            cp_model.CHOOSE_FIRST,
            cp_model.SELECT_MIN_VALUE
        )
        callback = MultipleSolutionsCollector(day_availability, available_days, activity["estimatedHours"] , max_solutions=5)
        solver.SearchForAllSolutions(model, callback)
        result = callback.get_solutions()
        if result:
            return [result,activity["endDate"]]
        else:
            return None

    def __complete_strategy(self, activity, calendar, busy_days):
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = False
        available_days = self.__check_available_days(activity, calendar, busy_days)
        total_hours = activity["estimatedHours"]

        # Restricción: la suma de todas las horas asignadas deben cubrir todas las horas estimadas
        day_availability = []
        for i, day in enumerate(available_days):
            limit = min(day["timeAvailable"], 4 if day["dayType"] == "Normal" else 8)
            var = model.NewIntVar(0, limit, f'horas_{day["calendarDate"]}')
            day_availability.append(var)
        model.Add(sum(day_availability) == total_hours)

        callback = MultipleSolutionsCollector(day_availability, available_days, activity["estimatedHours"] , max_solutions=5)
        solver.SearchForAllSolutions(model, callback)
        result = callback.get_solutions()
        if result:
            return [result,activity["endDate"]]
        else:
            return None


    def search_day_to_assign(self, activity, calendar):
        # Procesado de la entrada
        schedulerOutput = None
        end_date_margin = [activity["endOfActivity"]] + \
            [activity["endOfActivity"] + timedelta(days=i) for i in range(1,4)] + \
            [activity["endOfActivity"] - timedelta(days=i) for i in range(1,4)]
        if activity["startOfActivity"]:
            end_date_margin = [f for f in end_date_margin if activity["startOfActivity"] <= f <= activity["endOfActivity"] + timedelta(days=3)]
        busy_days = {}
        for day in calendar:
            busy_days[day["calendarDate"]] = day["totalHoursBusy"]
        
        # Procesado de la estrategia
        match activity["strategy"]:
            case "Agresiva":
                for endDate in end_date_margin:
                    activity_to_schedule = {
                        "endDate": endDate,
                        "estimatedHours": activity["estimatedHours"],
                        "startDate": activity["startOfActivity"]
                    }
                    result = self.__aggresive_strategy(activity_to_schedule,calendar,busy_days)
                    if result:
                        schedulerOutput = result
                        break 
            case "Calmada":
                for endDate in end_date_margin:
                    activity_to_schedule = {
                        "endDate": endDate,
                        "estimatedHours": activity["estimatedHours"],
                        "startDate": activity["startOfActivity"]
                    }
                    result = self.__calm_strategy(activity_to_schedule,calendar,busy_days)
                    if result:
                        schedulerOutput = result
                        break 
            case "Completa":
                for endDate in end_date_margin:
                    activity_to_schedule = {
                        "endDate": endDate,
                        "estimatedHours": activity["estimatedHours"],
                        "startDate": activity["startOfActivity"]
                    }
                    result = self.__complete_strategy(activity_to_schedule,calendar,busy_days)
                    if result:
                        schedulerOutput = result
                        break       
            case _:
                return 505
        
        # Preparación de la salida
        if schedulerOutput:
            solutions = []
            for solution in schedulerOutput[0]:
                newSchedule = []
                newCalendar = []
                for schedule in solution:
                    date = schedule["calendarDate"]
                    max_hours = 4 if schedule["dayType"] == "Normal" else 8
                    newSchedule.append({
                        "calendarDate": date,
                        "assignedHours": schedule["assignedHours"]
                    })
                    newCalendar.append({
                        "calendarDate": date,
                        "dayType": schedule["dayType"],
                        "status": "Ocupado" if schedule["assignedHours"] == max_hours else "Libre"
                    })
                solutions.append({
                    "newEndDate": schedulerOutput[1],
                    "schedule": newSchedule,
                    "modifiedCalendar": newCalendar
                })
            if (schedulerOutput[1] == activity["endOfActivity"]):
                # Asignado correctamente
                return 200, solutions
            else:
                # Asignado correctamente con la fecha de fin cambiada
                return 201, solutions   
        else:
            # No ha sido posible asignar la actividad
            return 401, None