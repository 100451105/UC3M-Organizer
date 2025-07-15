import axios from "axios";
import { mainColors } from "../components/common/Colors"
import { ActivityCache } from "../components/common/Cache";
import { useState, useEffect } from "react";
import Header from "../components/common/Header";

let subjectColorMap = {};

const getRandomColor = (subjectName) => {
  if (subjectColorMap[subjectName]) {
    return subjectColorMap[subjectName]
  }
  const keys = Object.keys(mainColors);
  const randomColor = keys[Math.floor(Math.random() * keys.length)];
  subjectColorMap[subjectName] = mainColors[randomColor];
  return mainColors[randomColor];
}

export default function Inicio() {
    const [loading, setLoadingState] = useState(true);
    const [activities_list, setActivityList] = useState([]);
    const [daily_calendar, setDailyCalendar] = useState({
      "Activities": []
    });

    // Cargar cache de usuario (comprobar inicio de sesión)
    const user_info = JSON.parse(localStorage.getItem("user_info"))
    if (!user_info && !user_info.Id) {
      alert("No has iniciado sesión");
      window.location.href = "/";
    }
    
    // Cargar cache de actividades (refrescar si no existe)
    useEffect(() => {
      const getActivities = async () => {
        const activities = await ActivityCache();
        setActivityList(activities);
      }
      getActivities();
    }, []);

    // Cargar información de hoy del calendario
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
            // Filtrar por asignaturas que afecten al usuario
            const subjectMap = {};
            user_info.relatedSubjectsList.forEach(subject => {
              subjectMap[subject.SubjectID] = subject.SubjectName;
            });
            dailyCalendar.Activities = dailyCalendar.Activities
              .filter(activity => subjectMap.hasOwnProperty(activity.Subject));

            console.log(dailyCalendar);
            
            setDailyCalendar(dailyCalendar);
          }
        } catch (error) {
            console.error("Error al obtener el calendario de hoy:", error);
            setDailyCalendar({});
        }
      }
      fetchCalendarDaily();
    }, [activities_list]);
    
    // Actividades a mostrar relevantes (4 más recientes mayores que hoy)
    const relevantActivities = activities_list
      // .filter(activity => new Date(activity.StartOfActivity) >= now)
      .sort((a,b) => new Date(a.StartOfActivity) - new Date(b.StartOfActivity))
      .slice(0,4);

    
    useEffect(() => {
      setLoadingState(false);
    }, []);

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