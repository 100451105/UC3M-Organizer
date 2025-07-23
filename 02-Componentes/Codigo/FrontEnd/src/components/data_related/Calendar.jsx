import React from "react";
import axios from "axios";
import Calendar from "react-calendar";
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
    const [date, setDate] = useState(null);
    const [currentDate, setCurrentDate] = useState(new Date());
    const [calendar_days, setCalendarDays] = useState([]);

    function isSameDay(d1, d2) {
        return(
            d1.getFullYear() === d2.getFullYear()
            && d1.getMonth() === d2.getMonth()
            && d1.getDate() === d2.getDate() 
        );
    }

    useEffect(() => {
        const fetchCalendar = async () => {
        try {
            const response = await axios.get("http://localhost:8002/calendar/info/", {
                withCredentials: true,
                params: {
                    calendarDate: new Date().toISOString().split("T")[0]
                }
            });
            if (response.status === 200) {
            let calendar = response.data.calendar;
            // Parsear Activities y adaptar calendarDate para el calendario
            calendar = calendar.map(day => ({
                ...day,
                Activities: JSON.parse(day.Activities).filter(activity => activity.ActivityName),
                CalendarDate: new Date(day.CalendarDate)
            }));
            
            setCalendarDays(calendar);
            }
        } catch (error) {
            console.error("Error al obtener el calendario de hoy:", error);
            setCalendarDays([]);
        }
        }
        fetchCalendar();
    }, []);

    setLoadingState(false);

    {/* HTML exportado como Calendario */}
    return (
        <>
            <h1 className="page-title">
                Organizador
            </h1>
            <section className="class-diagram-section">
                {/* Visualización del día seleccionado */}
                <div className="w-1/3 mr-[8vw] border-main-dark-blue bg-grey-300 border-[1vh] p-4 flex flex-col gap-4 overflow-y-auto h-[70vh]">
                    {(calendar_days
                        .find(entry => entry.CalendarDate.toDateString() === date?.toDateString() && entry.Activities.length > 0)
                        ?.Activities.map((activity, index) => {
                        const color = getRandomColor(activity.SubjectName);
                        return (
                            <div key={index} className="flex shadow-lg rounded-xl overflow-hidden border border-gray-300">
                            <div
                                className="w-[30%] min-w-[100px] p-2 text-white flex flex-col justify-center items-center text-sm font-medium"
                                style={{ backgroundColor: color }}
                            >
                                <span>{activity.Hours} {activity.Hours > 1 ? "Horas" : "Hora"}</span>
                            </div>

                            <div className="flex-1 px-4 py-2 flex flex-col font-montserrat justify-center bg-white">
                                <span className="text-lg font-semibold text-main-dark-blue">
                                {activity.ActivityName}
                                </span>
                                <span className="text-sm text-main-dark-blue">
                                de {activity.SubjectName}
                                </span>
                            </div>
                            </div>
                        );
                    }) ?? (
                        <p className="text-center text-gray-500">No hay actividades para este día.</p>
                    ))}
                </div>
                <div className="bg-white p-6 rounded-xl shadow-lg w-1/3 h-full">
                    <Calendar
                    view="month"
                    defaultView="month"
                    minDetail="month"
                    locale="es-ES"
                    onChange={setDate}
                    value={date}
                    activeStartDate={currentDate}
                    onActiveStartDateChange={({ activeStartDate }) =>
                        setCurrentDate(activeStartDate)
                    }
                    navigationLabel={({ label }) => (
                        <div className="w-full text-right text-xl font-montserrat font-bold text-main-dark-blue">
                            {label}
                        </div>
                    )}
                    prevLabel={<span className="text-2xl mr-[0.2vw] text-black font-bold hover:text-black">&lt;</span>}
                    nextLabel={<span className="text-2xl ml-[0.2vw] text-black font-bold hover:text-black">&gt;</span>}
                    prev2Label={null}
                    next2Label={null}
                    tileClassName={({ date: tileDate, view, activeStartDate }) => {
                        if (view !== "month") return "";

                        {/* Encontrar día en el calendario y aplicar lógica */}
                        let day_style = "text-lg aspect-square text-white ";

                        if (!(tileDate.getMonth() === activeStartDate.getMonth())) return day_style + "bg-gray-700 ";

                        const matchedDay = calendar_days.find((entry) => isSameDay(entry.CalendarDate, tileDate));
                        if (!matchedDay) return day_style + "bg-gray-700 ";

                        const totalHours = matchedDay.Activities.reduce(
                            (sum, activity) => sum + activity.Hours,
                            0
                        );
                        

                        if (matchedDay.DayType.toUpperCase() === "FESTIVO") {
                            day_style += "border-2 border-green-500 ";
                        }

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
                    {date && <p className="mt-1 text-center">Seleccionado: {date.toLocaleDateString()}</p>}
                    {!date && <p className="mt-1 text-center">Seleccionado: Ninguno</p>}
                    
                </div>
            </section>
        </>
    );
}