import React from "react";
import axios from "axios";
import Calendar from "react-calendar";
import { UserCache } from "../common/Cache";
import { useState, useEffect } from "react";
import { mainColors } from "../common/Colors"

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

export default function CustomCalendar({ setLoadingState }) {
    const [selectedDate, setSelectedDate] = useState(null);
    const [currentDate, setCurrentDate] = useState(new Date());
    const [minDate, setMinDate] = useState(new Date(currentDate.getFullYear(), currentDate.getMonth(), 1));
    const [maxDate, setMaxDate] = useState(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0));
    const [selectedActivity, setSelectedActivity] = useState(null);
    const [pending_activities, setPendingActivities] = useState([]);
    const [popupPos, setPopupPos] = useState({ x: 0, y: 0 });

    function isSameDay(d1, d2) {
        return(
            d1.getFullYear() === d2.getFullYear()
            && d1.getMonth() === d2.getMonth()
            && d1.getDate() === d2.getDate() 
        );
    }

    {/* Funciones para el manejo de fechas del schedule y calendario */}

    const getScheduleBounds = (schedule) => {
        if (!schedule || schedule.length === 0) return null;

        const sorted = [...schedule].sort((a, b) => new Date(a.day) - new Date(b.day));
        const min = new Date(sorted[0].day);
        const max = new Date(sorted[sorted.length - 1].day);

        const minBound = new Date(min.getFullYear(), min.getMonth(), 1);
        const maxBound = new Date(max.getFullYear(), max.getMonth() + 1, 0);

        return { min: minBound, max: maxBound };
    };

    const canGoPrev = () => {
        if (!minDate) return true;
        // Mes anterior al seleccionado en el calendario
        const prevMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
        return prevMonth >= minDate;
    };

    const canGoNext = () => {
        if (!maxDate) return true;
        // Mes siguiente al seleccionado en el calendario
        const nextMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
        return nextMonth <= maxDate;
    };

    const getHoursForDate = (date) => {
        if (!selectedActivity || !selectedActivity.schedule) return 0;
        const match = selectedActivity.schedule.find(sch =>
        new Date(sch.day).toDateString() === date.toDateString()
        );
        return match ? match.hours : 0;
    };

    const handleDayClick = (date, event) => {
        setSelectedDate(date);
        setPopupPos({ x: event.clientX, y: event.clientY });
    };

    const closePopup = () => {
        setSelectedDate(null);
    };

    const handleConfirm = async () => {
        try {
            const confirmActivity = await axios.post("http://localhost:8002/activities/confirm/", {
                activityId: selectedActivity.id
            });
            console.log("Respuesta del servidor:", confirmActivity.status);
            if (confirmActivity.status === 200) {
                alert("Confirmada actividad correctamente");
                // Forzar refresh de las actividades
                localStorage.removeItem("activity_info");
                window.location.href = '/pendientes';
            }
        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response) {
                    const message = "Error al modificar los datos:\n" + error.response.status || "Error desconocido. Por favor, inténtalo de nuevo.";
                    console.error(message);
                    alert(message);
                } else if (error.request) {
                    console.error("No se recibió respuesta del servidor:", error.request);
                    alert("No se recibió respuesta del servidor. Por favor, inténtalo de nuevo más tarde.");
                } else {
                    console.error("Error al configurar la solicitud:", error.message);
                    alert("Error al configurar la solicitud. Por favor, inténtalo de nuevo más tarde.");
                }
            }
        }
    }

    {/* Carga de actividades pendientes y horarios */}
    useEffect(() => {
        const fetchPendingActivities = async () => {
            const user_info = JSON.parse(localStorage.getItem("user_info"));
            if (!user_info || (user_info.Type !== "Administrador" && user_info.Type !== "Coordinador")) {
                alert("Acceso denegado a la sección de asignaturas");
                window.location.href = "/main";
            }
            const Id = user_info.Id;
            await UserCache(Id);
            try {
                const response = await axios.get("http://localhost:8002/activities/pending/info/", {
                    withCredentials: true,
                    params: {
                        userId: Id
                    }
                });
                if (response.status === 200) {
                    let activities = response.data.pendingList;
                    // Parsear Activities y adaptar calendarDate para el calendario
                    const parsedActivities = activities.map(activity => ({
                        id: activity.ActivityID,
                        name: activity.ActivityName,
                        subjectId: activity.SubjectID,
                        subjectName: activity.SubjectName,
                        start: new Date(activity.StartOfActivity),
                        end: new Date(activity.EndOfActivity),
                        newEnd: new Date(activity.NewEndOfActivity),
                        schedule: JSON.parse(activity.ScheduleJSON).map(item => ({
                            ...item,
                            day: new Date(item.day),
                        }))
                    }));
                    setPendingActivities(parsedActivities);

                }
            } catch (error) {
                console.error("Error al obtener las actividades pendientes:", error);
                setPendingActivities([]);
            }
            }
        fetchPendingActivities();
    }, []);

    useEffect(() => {
        if (!selectedActivity) {
            const today = new Date();
            const start = new Date(today.getFullYear(), today.getMonth(), 1);
            const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);

            setMinDate(start);
            setMaxDate(end);
            setCurrentDate(start);
        }
    }, [selectedActivity]);

    setLoadingState(false);

    {/* HTML exportado como Calendario */}
    return (
        <>
            <h1 className="page-title">
                Pendientes
            </h1>
            <section className="class-diagram-section">
                {/* Visualización de actividad seleccionada */}
                <div className="w-1/4 mr-[5vw] p-4 flex flex-col gap-4 overflow-y-auto h-[70vh]">
                {selectedActivity ? (
                    <>
                    <div className="flex flex-col gap-6">
                        <div>
                        <h2 className="text-lg font-bold text-main-dark-blue mb-2">Fecha de Fin Original</h2>
                        <div className="border-2 border-main-dark-blue rounded-lg p-3 text-center bg-white text-black text-md font-semibold">
                            {new Date(selectedActivity.end).toLocaleDateString()}
                        </div>
                        </div>

                        <div>
                        <h2 className="text-lg font-bold text-main-dark-blue mb-2">Fecha de Fin Nueva</h2>
                        <div className="border-2 border-main-dark-blue rounded-lg p-3 text-center bg-white text-black text-md font-semibold">
                            {new Date(selectedActivity.newEnd).toLocaleDateString()}
                        </div>
                        </div>
                    </div>

                    <button
                        onClick={handleConfirm}
                        className="custom-button absolute bottom-[3%] left-[0%] w-1/4 font-bold py-2 px-4 mt-6 rounded"
                    >
                        Confirmar
                    </button>
                    </>
                ) : (
                    <p className="text-center text-gray-500 mt-8">Selecciona una actividad para obtener información adicional y confirmarla</p>
                )}
                </div>
                {/* Calendario de horarios */}
                <div className="bg-white p-6 rounded-xl shadow-lg w-1/3 h-full">
                    <Calendar
                    view="month"
                    defaultView="month"
                    minDetail="month"
                    locale="es-ES"
                    onClickDay={handleDayClick}
                    value={null}
                    minDate={minDate}
                    maxDate={maxDate}
                    activeStartDate={currentDate}
                    onActiveStartDateChange={({ activeStartDate }) =>
                        setCurrentDate(activeStartDate)
                    }
                    navigationLabel={({ label }) => (
                        <div className="w-full text-right text-xl font-montserrat font-bold text-main-dark-blue">
                            {label}
                        </div>
                    )}
                    prevLabel={canGoPrev() ? <span className="text-2xl mr-[0.2vw] text-black font-bold hover:text-black">&lt;</span> : null}
                    nextLabel={canGoNext() ? <span className="text-2xl ml-[0.2vw] text-black font-bold hover:text-black">&gt;</span> : null}
                    prev2Label={null}
                    next2Label={null}
                    tileClassName={({ date: tileDate, view, activeStartDate }) => {
                        if (view !== "month") return "";

                        {/* Encontrar día en el calendario y aplicar lógica */}
                        let day_style = "text-lg aspect-square text-white ";

                        if (!(tileDate.getMonth() === activeStartDate.getMonth())) return day_style + "bg-gray-700 ";

                        if (!selectedActivity || !selectedActivity.schedule) {
                            return day_style + "bg-gray-700 ";
                        }

                        const scheduleItem = selectedActivity.schedule.find((s) => 
                            new Date(s.day).toDateString() === tileDate.toDateString()
                        );

                        if (!scheduleItem) {
                            return day_style + "bg-gray-700 ";
                        }
                        

                        if (scheduleItem.dayType.toUpperCase() === "FESTIVO") {
                            day_style += "border-2 border-green-500 ";
                        }

                        const totalHours = scheduleItem.hours;

                        if (totalHours >= 4) {
                            day_style += "bg-main-red ";
                        } else if (totalHours >= 2) {
                            day_style += "bg-main-yellow ";
                        } else {
                            day_style += "bg-main-light-blue ";
                        }

                        return day_style;
                    }}
                    />
                    {selectedDate && (
                        <div
                        style={{
                            position: "fixed",
                            top: popupPos.y + 10,
                            left: popupPos.x + 10,
                            backgroundColor: "rgba(0,0,0,0.85)",
                            color: "white",
                            padding: "8px 12px",
                            borderRadius: "6px",
                            zIndex: 1000,
                            fontSize: "13px",
                            cursor: "pointer",
                            userSelect: "none"
                        }}
                        onClick={closePopup}
                        title="Haz click para cerrar"
                        >
                        Horas: {getHoursForDate(selectedDate)}
                        </div>
                    )}
                    {selectedActivity && <p className="mt-1 text-center">Seleccionado: {selectedActivity.name}</p>}
                    {!selectedActivity && <p className="mt-1 text-center">Seleccionado: Ninguno</p>}
                    
                </div>
                {/* Selector de actividades */}
                
                <div className="w-1/3 ml-[5vw] border-main-dark-blue bg-grey-300 border-[1vh] flex flex-col overflow-y-auto h-[70vh]">
                    <h2 className="text-center text-main-dark-blue font-montserrat font-bold text-xl py-4 border-b border-main-dark-blue">
                        Actividades pendientes
                    </h2>
                    {pending_activities.length > 0 ? (
                        pending_activities.map((activity) => {
                            const color = getRandomColor(activity.name);
                            return (
                                <button
                                key={activity.id}
                                onClick={() => {
                                    setSelectedActivity(activity);
                                    const bounds = getScheduleBounds(activity.schedule);
                                    if (bounds) {
                                        setMinDate(bounds.min);
                                        setMaxDate(bounds.max),
                                        setCurrentDate(bounds.min);
                                    }
                                }}
                                className="border-main-dark-blue w-full border-b-[0.5vh] text-white font-montserrat text-[2.5vh] font-semibold py-2"
                                style={{ backgroundColor: color }}
                                >
                                {activity.name} <br />
                                <span className="text-sm font-normal">
                                    de {activity.subjectName}
                                </span>
                                </button>
                            );
                        })
                    ) : (
                        <div className="w-full h-full flex justify-center items-center text-main-dark-blue font-semibold text-lg text-center px-4">
                        No hay actividades pendientes de confirmar actualmente
                        </div>
                    )}
                </div>
            </section>
        </>
    );
}