import React from "react";
import ReactECharts from "echarts-for-react";
import { mainColors } from "../common/Colors"

const COLORS = {
    "Diseño": mainColors["main-dark-blue"],
    "Desarrollo": mainColors["main-green"],
    "QA": mainColors["main-red"]
}

const MONTHS = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre"
]

export default function GanttDiagram() {
    {/* Definición de meses a utilizar */}
    const UTCDate = new Date();
    const actualYear = UTCDate.getUTCFullYear();
    const actualMonth = UTCDate.getUTCMonth();
    const monthIndexes = [
        (actualMonth + 11) % 12,
        actualMonth,
        (actualMonth + 1) % 12,
        (actualMonth + 2) % 12
    ]
    const ganttMonths = monthIndexes.map(i => MONTHS[i]);


    {/* Datos para realización del diagrama de Gantt */}
    const data = [
        {
        name: "Diseño prototipo",
        resource: "Diseño",
        start: new Date("2025-07-01"),
        end: new Date("2025-07-05"),
        },
        {
        name: "Frontend",
        resource: "Desarrollo",
        start: new Date("2025-07-06"),
        end: new Date("2025-07-20"),
        },
        {
        name: "Backend",
        resource: "Desarrollo",
        start: new Date("2025-07-06"),
        end: new Date("2025-07-22"),
        },
        {
        name: "QA",
        resource: "QA",
        start: new Date("2025-07-23"),
        end: new Date("2025-08-10"),
        },
    ];
    const resources = [...new Set(data.map(d => d.resource))];
    const chartData = data.map((item) => ([
        resources.indexOf(item.resource),
        item.resource,
        item.start.getTime(),
        item.end.getTime(),
        item.name,
        COLORS[item.resource],
    ]));

    const option = {
        tooltip: {
            formatter: (params) => {
                const data = params.data
                const startStr = new Date(data[2]).toLocaleDateString();
                const endStr = new Date(data[3]).toLocaleDateString();
                return `<b>${data[4]}</b><br/>${startStr} → ${endStr}`;
            },
        },
        xAxis: {
            type: "time",
            min: new Date("2025-06-25").getTime(),
            max: new Date("2025-08-20").getTime(),
        },
        yAxis: {
            type: "category",
            data: resources,
            inverse: true,
        },
        grid: {
            top: 20,
            bottom: 40,
            left: 100,
            right: 20,
        },
        series: [
        {
            type: "custom",
            renderItem: function (params, api) {
                const color = api.value(5);
                const categoryIndex = api.value(0);
                const startCoord = api.coord([api.value(2), categoryIndex]);
                const endCoord = api.coord([api.value(3), categoryIndex]);
                const height = 20;

                return {
                    type: "rect",
                    shape: {
                        x: startCoord[0],
                        y: startCoord[1] - height / 2,
                        width: endCoord[0] - startCoord[0],
                        height: height,
                    },
                    style: {
                        fill: color,
                    },
                };
            },
            encode: {
                x: [1, 2],
                y: 0,
            },
            data: chartData,
            tooltip: {
                valueFormatter: () => "",
            },
        },
        ],
    };

    {/* HTML exportado como diagrama de Gantt */}
    return (
        <>
            <h1 className="nav-bar-text text-black">
                Gantt Diagram
            </h1>
            <section className="gantt-diagram-section">
                <ReactECharts option={option} style={{ height: "100%", width: "100%" }} />
            </section>
        </>
    );
}