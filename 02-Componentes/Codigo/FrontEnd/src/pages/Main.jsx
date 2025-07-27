import axios from "axios";
import { mainColors } from "../components/common/Colors"
import { ActivityCache } from "../components/common/Cache";
import { useState, useEffect } from "react";
import Header from "../components/common/Header";

{/* Sección de colores asignados a las asignaturas */}

let subjectColorMap = {};

const getRandomColor = (subjectName) => {
    if (subjectColorMap[subjectName]) {
        return subjectColorMap[subjectName]
    }

    {/* 1. Contar cuántas veces se ha asignado cada color */}
    const colorUsage = {};
    Object.keys(mainColors).forEach(colorKey => {
      colorUsage[colorKey] = 0;
    });
    
    Object.values(subjectColorMap).forEach(colorValue => {
      const colorKey = Object.keys(mainColors).find(key => mainColors[key] === colorValue);
      if (colorKey) {
        colorUsage[colorKey]++;
      }
    });

    {/* 2. Encontrar el menor uso de colores */}
    const minUsage = Math.min(...Object.values(colorUsage));

    {/* 3. Obtener todos los colores con el menor uso */}
    const leastUsedColors = Object.keys(colorUsage).filter(
      key => colorUsage[key] === minUsage
    );

    {/* 4. Seleccionar uno aleatorio entre los menos usados */}
    const chosenColorKey = leastUsedColors[Math.floor(Math.random() * leastUsedColors.length)];
    const chosenColorValue = mainColors[chosenColorKey];

    {/* 5. Asignar y devolver */}
    subjectColorMap[subjectName] = chosenColorValue;
    return chosenColorValue;
}

export default function Inicio() {
    {/* Función para crear la página de Inicio */}
    const [loading, setLoadingState] = useState(true);
    const [activities_list, setActivityList] = useState([]);
    const [daily_calendar, setDailyCalendar] = useState({
      "Activities": []
    });

    {/* Cargar cache de usuario (comprobar inicio de sesión) */}
    const user_info = JSON.parse(localStorage.getItem("user_info"))
    if (!user_info && !user_info.Id) {
      alert("No has iniciado sesión");
      window.location.href = "/";
    }
    
    {/* Cargar cache de actividades (refrescar si no existe) */}
    useEffect(() => {
      const getActivities = async () => {
        const activities = await ActivityCache();
        setActivityList(activities);
      }
      getActivities();
    }, []);

    {/* Cargar información de hoy del calendario */}
    useEffect(() => {
      if (activities_list.length === 0) return;
      const fetchCalendarDaily = async () => {
        try {
          const response = await axios.get("http://localhost:8002/calendar/info/daily/");
          if (response.status === 200) {
            if (response.data.calendar.length === 0) {
              return
            }
            let dailyCalendar = response.data.calendar[0];
            
            dailyCalendar.Activities = JSON.parse(dailyCalendar.Activities);
            {/* Filtrar por asignaturas que afecten al usuario */}
            const subjectMap = {};
            user_info.relatedSubjectsList.forEach(subject => {
              subjectMap[subject.SubjectID] = subject.SubjectName;
            });
            dailyCalendar.Activities = dailyCalendar.Activities
              .filter(activity => subjectMap.hasOwnProperty(activity.Subject));
            
            setDailyCalendar(dailyCalendar);
          }
        } catch (error) {
            console.error("Error al obtener el calendario de hoy:", error);
            setDailyCalendar({
              "Activities": []
            });
        }
      }
      fetchCalendarDaily();
      setLoadingState(false);
    }, [activities_list]);
    
    {/* Actividades a mostrar relevantes (4 más recientes mayores que hoy) */}
    const relevantActivities = activities_list
      .sort((a,b) => new Date(a.StartOfActivity) - new Date(b.StartOfActivity))
      .slice(0,4);

    return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      <h1 className="normal-page-title">
        Bienvenido {user_info.Username}
      </h1>
      <section className="main-diagram-section flex flex-col justify-center">
        {/* Sección del organizador de hoy */}
        <div className="w-1/3 h-full">
          <h2 className="section-title text-[clamp(4.0vh,3vw,4.5vh)] h-1/6 text-center items-center">
            Organización de Hoy
          </h2>
          <div className="h-5/6 w-full border-main-dark-blue border-[1vh]">
            {daily_calendar.Activities.length > 0 ? (
              daily_calendar.Activities.map((activity, index) => {
                const color = getRandomColor(activity.SubjectName);

                return (
                  <div key={index} className="flex shadow-lg rounded-xl overflow-hidden border border-gray-300">
                    {/* Parte izquierda: duración */}
                    <div
                      className="w-[20%] min-w-[120px] p-2 text-white flex flex-col justify-center items-center text-sm font-medium"
                      style={{ backgroundColor: color }}
                    >
                      <span>{activity.Hours} hora{activity.Hours !== 1 ? "s" : ""}</span>
                    </div>

                    {/* Parte derecha: contenido */}
                    <div className="flex-1 px-4 py-2 flex flex-col font-montserrat justify-center bg-white">
                      <span className="text-lg font-semibold text-main-dark-blue">
                        {activity.ActivityName}
                      </span>
                      <span className="text-sm text-main-dark-blue">
                        De {activity.SubjectName}
                      </span>
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-center text-gray-500">No hay actividades para hoy.</p>
            )}
          </div>
        </div>
      </section>
      <section className="main-diagram-section-2 flex flex-col justify-center">
        {/* Sección del calendario de actividades recientes */}
        <h2 className="section-title pt-[0vh] h-[10%] text-center items-center">
          Resumen de Calendario
        </h2>
        <div className="h-[90%] w-full border-main-dark-blue border-[1vh] p-4 flex flex-col gap-4 overflow-y-auto">
          {relevantActivities.length > 0 ? (
            relevantActivities.map((activity, index) => {
              const color = getRandomColor(activity.SubjectName);
              return (
              <div key={index} className="flex shadow-lg rounded-xl overflow-hidden border border-gray-300">
                {/* Parte izquierda: fechas */}
                <div
                  className="w-[20%] min-w-[120px] p-2 text-white flex flex-col justify-center items-center text-sm font-medium"
                  style={{ backgroundColor: color }}
                >
                  <span>{new Date(activity.StartOfActivity).toLocaleDateString()}</span>
                  <span className="text-xs">→</span>
                  <span>{new Date(activity.EndOfActivity).toLocaleDateString()}</span>
                </div>

                {/* Parte derecha: contenido */}
                <div className="flex-1 px-4 py-2 flex flex-col font-montserrat justify-center bg-white">
                  <span className="text-lg font-semibold text-main-dark-blue">
                    {activity.ActivityName}
                  </span>
                  <span className="text-sm text-main-dark-blue">
                    De {activity.SubjectName}
                  </span>
                </div>
              </div>
              );
          })
          ) : (
            <p className="text-center text-gray-500">No hay actividades próximas.</p>
          )}
        </div>
      </section>
    </>
  )
}