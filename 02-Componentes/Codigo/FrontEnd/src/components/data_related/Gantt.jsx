import { ActivityCache } from "../common/Cache";
import { useState, useEffect } from "react";
import ReactECharts from "echarts-for-react";
import { mainColors } from "../common/Colors"

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

{/* Sección de colores asignados a las asignaturas */}

let COLORS = {};

const getRandomColor = (subjectName) => {
    if (COLORS[subjectName]) {
        return COLORS[subjectName]
    }

    {/* 1. Contar cuántas veces se ha asignado cada color */}
    const colorUsage = {};
    Object.keys(mainColors).forEach(colorKey => {
      colorUsage[colorKey] = 0;
    });
    
    Object.values(COLORS).forEach(colorValue => {
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
    COLORS[subjectName] = chosenColorValue;
    return chosenColorValue;
}

export default function GanttDiagram({ setLoadingState }) {
    {/* Sección relacionada con la construcción del diagrama de Gantt */}
    const [activity_list, setActivityList] = useState([]);

    {/* Definición de meses a utilizar */}
    const UTCDate = new Date();
    const actualYear = UTCDate.getUTCFullYear();
    const actualMonth = UTCDate.getUTCMonth();
    const monthIndexes = [-1,0,1,2];

    const ganttMonths = monthIndexes.map(offset => {
        const date = new Date(Date.UTC(actualYear, actualMonth + offset, 1));
        return {
            "month": date.getUTCMonth(),
            "year": date.getUTCFullYear()
        };
    });

    const minDate = new Date(Date.UTC(ganttMonths[0].year, ganttMonths[0].month, 1));
    const maxDate = new Date(Date.UTC(ganttMonths[3].year, ganttMonths[3].month + 1, 0));

    const labelMonths = ganttMonths.map(({ month, year }) => ({
        timestamp: new Date(Date.UTC(year, month, 1)).getTime(),
        label: MONTHS[month]
    }));


    {/* Datos para realización del diagrama de Gantt */}
    useEffect(() => {
        const getActivities = async () => {
            let activities = await ActivityCache();
            activities = activities.map(activity => {
                return {
                    name: activity.ActivityName,
                    start: new Date(activity.StartOfActivity),
                    end: new Date(activity.EndOfActivity),
                    type: activity.ActivityType,
                    resource: activity.SubjectName
                }
            })
            setActivityList(activities);
        }
        getActivities();
    }, []);
    
    const resources = [...new Set(activity_list.map(d => d.resource))];
    const resourceKeys = Object.fromEntries(
        resources.map(resource => [
            resource,
            resource.replace(/\s+/g, "_").normalize("NFD").replace(/[\u0300-\u036f]/g, "") // quita tildes y espacios
        ])
    );

    const colorValues = Object.values(mainColors);
    resources.forEach(resource => {
        getRandomColor(resource);
    });

    {/* Cálculo del tamaño del Gantt dinámicamente */}
    const [windowHeight, setWindowHeight] = useState(window.innerHeight);

    useEffect(() => {
        function onResize() {
            setWindowHeight(window.innerHeight);
        }
        window.addEventListener("resize", onResize);
        return () => window.removeEventListener("resize", onResize);
    }, []);

    const containerHeightvh = 70;
    const visibleRows = 7;
    const rowHeight = windowHeight * ((containerHeightvh / visibleRows) / 100);

    const chartHeight = Math.max(resources.length * rowHeight, windowHeight  * (containerHeightvh / 100));
    
    {/* Agrupar para mostrar múltiples barras */}
    const groupedData = {};
    activity_list.forEach((activity) => {
        if (!groupedData[activity.resource]) groupedData[activity.resource] = [];
        groupedData[activity.resource].push(activity);
    })

    const chartData = [];
    Object.entries(groupedData).forEach(([subject, tasks]) => {
        tasks.forEach((activity, subIndex) => {
            const startTime = activity.start.getTime();
            const endTime = activity.end.getTime();
            chartData.push([
                resources.indexOf(subject),
                subject,
                startTime,
                endTime,
                activity.name,
                COLORS[activity.resource],
                subIndex,
                tasks.length,
                activity.type
            ]);
        });
    });

    const endOfMonthLines = ganttMonths.map(({ year, month }) => {
        const lastDayTimestamp = Date.UTC(year, month + 1, 0);
        return lastDayTimestamp;
    });
    
    {/* Opciones personalizadas para el diagrama de Gantt */}
    const option = {
        
        tooltip: {
            trigger: "item",
            formatter: (params) => {
                const data = params.data;
                const startStr = new Date(data[2]).toLocaleDateString();
                const endStr = new Date(data[3]).toLocaleDateString();
                const color = data[5] || "#333";

                return `
                    <div style="
                        background-color: ${color};
                        color: white;
                        padding: 10px;
                        border-radius: 6px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                        border: 1px solid ${mainColors['main-dark-blue']}
                    ">
                        <div style="font-weight: bold; margin-bottom: 4px;">${data[4]}</div>
                        <div> ${startStr} → ${endStr}</div>
                        <div><b>Tipo:</b> ${data[8]}</div>
                    </div>
                `;
            },
            backgroundColor: 'transparent',
            borderWidth: 0,
            textStyle: {
                color: "#fff",
                fontSize: 13,
            },
            padding: 0,
            extraCssText: 'box-shadow: none;',
        },
        xAxis: {
            type: "time",
            min: minDate.getTime(),
            max: maxDate.getTime(),
            axisTick: {
                alignWithLabel: true
            },
            data: labelMonths,
            axisLabel: {
                formatter: (value) => {
                    const current = new Date(value);
                    const match = labelMonths.find(({ timestamp }) => {
                        const currentUTC = Date.UTC(current.getUTCFullYear(), current.getUTCMonth(), 1);
                        return currentUTC === timestamp;
                    });
                    return match ? match.label : "";
                },
                hideOverlap: false,
                showMinLabel: true,
                showMaxLabel: true,
            },
            splitNumber: labelMonths.length,
        },
        yAxis: {
            type: "category",
            data: resources,
            inverse: true,
            axisLabel: {
                width: 200,
                overflow: "break",
                lineHeight: 16,
                formatter: (value) => {
                    const key = resourceKeys[value];
                    return `{${key}|${value}}`;
                },
                rich: Object.fromEntries(
                    resources.map(resource => {
                        const key = resourceKeys[resource];
                        return [key, {
                            backgroundColor: COLORS[resource],
                            color: "#fff",
                            padding: [4,8],
                            borderRadius: 6,
                            fontWeight: "bold",
                            fontSize: 12,
                            align: "center",
                        }];
                    })
                ), 
            },
        },
        grid: {
            top: 20,
            bottom: 40,
            left: 220,
            right: 40,
        },
        series: [
        {
            type: "custom",
            markLine: {
                silent: true,
                symbol: "none",
                lineStyle: {
                    color: "#aaa",
                    width: 1,
                    type: "dashed"
                },
                label: {
                    show: false,
                },
                data: [
                    endOfMonthLines.map(timestamp => ({
                    xAxis: timestamp
                })),
                {
                    xAxis: new Date(), 
                    lineStyle: {
                        color: "#2563eb",
                        type: "dashed",
                        width: 2
                    },
                    label: {
                        show: true,
                        formatter: "Hoy",
                        position: "insideEndTop",
                        color: mainColors["main-dark-blue"],
                        fontWeight: "bold"
                    }
                    }
                ]
            },
            renderItem: function (params, api) {
                const color = api.value(5);
                const categoryIndex = api.value(0);
                const subIndex = api.value(6);
                const totalInGroup = api.value(7);

                const startCoord = api.coord([api.value(2), categoryIndex]);
                const endCoord = api.coord([api.value(3), categoryIndex]);
                const fullHeight = api.size([0,1])[1];
                const subBarHeight = fullHeight/totalInGroup;
                const y = startCoord[1] - fullHeight/2 + subBarHeight * subIndex;

                return {
                    type: "rect",
                    shape: {
                        x: startCoord[0],
                        y: y,
                        width: endCoord[0] - startCoord[0],
                        height: subBarHeight - 2,
                    },
                    style: {
                        fill: color,
                    },
                    
                };
            },
            encode: {
                x: [1, 2],
                y: 0,
                tooltip: [0,1,2,3,4,5,6,7,8]
            },
            data: chartData,
            clip: true,

        },
        ],
    };

    setLoadingState(false);
    {/* HTML exportado como diagrama de Gantt */}
    return (
        <>
            <h1 className="section-title text-[clamp(4.0vh,3vw,4.5vh)] h-1/6 items-center pt-[1.5vh] ml-[2vw] underline">
                Calendario
            </h1>
            <section className="gantt-diagram-section" style={{height: `${containerHeightvh}vh`}}>
                <ReactECharts option={option} style={{ height: `${chartHeight}px`, width: "100%" }} />
            </section>
        </>
    );
}