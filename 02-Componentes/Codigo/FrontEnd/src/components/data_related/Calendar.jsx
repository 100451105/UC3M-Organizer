import React from "react";
import Calendar from "react-calendar";
import { useState } from "react";
import { mainColors } from "../common/Colors"




export default function CustomCalendar() {
    const [date, setDate] = useState(new Date());
    const [currentDate, setCurrentDate] = useState(new Date());

    const data = [
        {
        CalendarDate: new Date("2025-07-11"),
        DayType: "Normal",
        WeekDay: "Viernes",
        Status: "Libre",
        Activities: [
            {
                Activity: 1,
                Hours: 1,
                Subject: 1
            },
            {
                Activity: 2,
                Hours: 3,
                Subject: 1
            }
        ]
        },
        {
        CalendarDate: new Date("2025-07-12"),
        DayType: "Festivo",
        WeekDay: "Sabado",
        Status: "Libre",
        Activities: [
            {
                Activity: 1,
                Hours: 1,
                Subject: 1
            },
            {
                Activity: 2,
                Hours: 3,
                Subject: 1
            }
        ]
        },
        {
        CalendarDate: new Date("2025-07-13"),
        DayType: "Festivo",
        WeekDay: "Domingo",
        Status: "Libre",
        Activities: []
        },
        {
        CalendarDate: new Date("2025-07-07"),
        DayType: "Normal",
        WeekDay: "Lunes",
        Status: "Libre",
        Activities: [
            {
                Activity: 1,
                Hours: 1,
                Subject: 1
            },
            {
                Activity: 2,
                Hours: 1,
                Subject: 1
            }
        ]
        },
        {
        CalendarDate: new Date("2025-07-08"),
        DayType: "Normal",
        WeekDay: "Martes",
        Status: "Libre",
        Activities: []
        },
        {
        CalendarDate: new Date("2025-07-09"),
        DayType: "Festivo",
        WeekDay: "Miercoles",
        Status: "Libre",
        Activities: []
        },
        {
        CalendarDate: new Date("2025-07-10"),
        DayType: "Festivo",
        WeekDay: "Jueves",
        Status: "Libre",
        Activities: [
            {
                Activity: 1,
                Hours: 1,
                Subject: 1
            },
            {
                Activity: 2,
                Hours: 1,
                Subject: 1
            }
        ]
        },
    ];

    function isSameDay(d1, d2) {
        return(
            d1.getFullYear() === d2.getFullYear()
            && d1.getMonth() === d2.getMonth()
            && d1.getDate() === d2.getDate() 
        );
    }

    {/* HTML exportado como Calendario */}
    return (
        <>
            <h1 className="page-title">
                Organizador
            </h1>
            <section className="class-diagram-section">
                <div className="w-1/3 mr-[8vw] border-main-dark-blue bg-grey-300 border-[1vh]">

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

                        const matchedDay = data.find((entry) => isSameDay(entry.CalendarDate, tileDate));
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

                        console.log(day_style)

                        return day_style;
                    }}
                    />
                    <p className="mt-4 text-center">Seleccionado: {date.toLocaleDateString()}</p>
                </div>
            </section>
        </>
    );
}