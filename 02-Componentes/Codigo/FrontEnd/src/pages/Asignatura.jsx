import { useState, useEffect } from 'react';
import axios from "axios";
import Header from "../components/common/Header";
import { mainColors } from "../components/common/Colors";
import { UserCache } from '../components/common/Cache';

let subjectColorMap = {};

const getRandomColor = (subjectName) => {
    if (subjectColorMap[subjectName]) {
        return subjectColorMap[subjectName]
    }

    // 1. Contar cuántas veces se ha asignado cada color
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

    // 2. Encontrar el menor uso de colores
    const minUsage = Math.min(...Object.values(colorUsage));

    // 3. Obtener todos los colores con el menor uso
    const leastUsedColors = Object.keys(colorUsage).filter(
      key => colorUsage[key] === minUsage
    );

    // 4. Seleccionar uno aleatorio entre los menos usados
    const chosenColorKey = leastUsedColors[Math.floor(Math.random() * leastUsedColors.length)];
    const chosenColorValue = mainColors[chosenColorKey];

    // 5. Asignar y devolver
    subjectColorMap[subjectName] = chosenColorValue;
    return chosenColorValue;
}

export default function Asignatura() {
    {/* Cambiar entre modo edición y modo lectura */}
    const [editMode, setEditMode] = useState(false);
    const [loading, setLoadingState] = useState(true);
    const [subjectData, setsubjectData] = useState({});
    const [userData, setUserData] = useState({});
    const [tempData, setTempData] = useState({...subjectData});
    const [activityList, setActivityList] = useState([]);

    useEffect(() => {
      const fetchData = async () => {
            await UserCache(false);
            const user_info = JSON.parse(localStorage.getItem("user_info"))

            {/* Get data of the subject in order to populate the page dinamically */}
            const subjectId = sessionStorage.getItem('selectedSubjectID');
            try {
                const subjectInfo = await axios.get("http://localhost:8002/subject/specific/info/", {
                    withCredentials: true,
                    params: {
                        subjectId: subjectId
                    }
                });
                console.log("Respuesta del servidor:", subjectInfo.status);
                if (subjectInfo.status == 200) {
                    setsubjectData(subjectInfo.data.subjectInfo);
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
            setUserData(user_info);
            try {
                const activities_info = await axios.get("http://localhost:8002/activities/info/subject/", {
                    withCredentials: true,
                    params: {
                        subjectId: subjectId
                    }
                });
                console.log("Respuesta del servidor:", activities_info.status);
                if (activities_info.status == 200) {
                  console.log(activities_info.data.activities);
                  setActivityList(activities_info.data.activities);
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
        fetchData();
    }, []);

    const handleUpdate = () => {
      setTempData({...subjectData});
      setEditMode(true);
    }

    const handleConfirm = async () => {
      setLoadingState(true);
      
      {/* Petición para actualizar la información del usuario en el backend */}
      
      try {
          if (!tempData.Credits || !tempData.Semester || !tempData.Year || !tempData.AdministratorName){
            alert("Alguno de los campos de texto introducidos está vacío. Por favor, rellene dichos campos antes de confirmar de nuevo")
            setLoadingState(false);
            return;
          }
          const updateResponse = await axios.post("http://localhost:8002/subject/update/", {
              credits: tempData.Credits,
              semester: tempData.Semester,
              year: tempData.Year,
              name: subjectData.Name,
              subjectId: subjectData.IdSubject,
              coordinator: tempData.AdministratorName
          });
          console.log("Respuesta del servidor:", updateResponse.status);
          if (updateResponse.status == 200) {
            alert("Datos actualizados correctamente"); 
            setsubjectData({...tempData});
            setEditMode(false);
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
      } finally {
        setLoadingState(false);
      }
    };

    const handleCancel = () => {
      setTempData({...subjectData});
      setEditMode(false);
    };

    useEffect(() => {
      setLoadingState(false);
    })
    
    return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      <h2 className="page-title">{subjectData.Name}</h2>
      <section className="bg-white rounded-xl p-6 w-[50vw] text-left">
        {/* Créditos */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Créditos :</span>{' '}
            {editMode ? (
            <input
                type="number"
                value={tempData.Credits}
                min={1}
                max={30}
                onChange={(e) => setTempData({ ...tempData, Credits: e.target.value === "" ? "" : parseInt(e.target.value) })}
                className="ml-2 border-b-2 border-main-dark-blue outline-none text-[3vh] font-montserrat text-black"
            />
          ) : (
            <>
              <span className="ml-2 font-montserrat text-[3vh] text-black">
                {subjectData.Credits}
              </span>
            </>
          )}
        </div>

        {/* Cuatrimestre */}
        <div className="mb-[3vh] flex items-center">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Cuatrismestre :</span>
          {editMode ? (
            <input
                type="number"
                value={tempData.Semester}
                min={1}
                max={2}
                onChange={(e) => setTempData({ ...tempData, Semester: e.target.value === "" ? "" : parseInt(e.target.value) })}
                className="ml-2 border-b-2 border-main-dark-blue outline-none text-[3vh] font-montserrat text-black"
            />
          ) : (
            <>
              <span className="ml-2 font-montserrat text-[3vh] text-black">
                {subjectData.Semester}
              </span>
            </>
          )}
        </div>

        {/* Año */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Año :</span>{' '}
          {editMode ? (
            <input
                type="number"
                value={tempData.Year}
                min={1}
                max={4}
                onChange={(e) => setTempData({ ...tempData, Year: e.target.value })}
                className="ml-2 text-black font-montserrat text-[3vh] border-b-2 border-main-dark-blue outline-none px-2 py-1"
            />
          ) : (
            <span className="text-black font-montserrat text-[3vh]">{subjectData.Year}</span>
          )}
        </div>

        {/* Tutor */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Tutor :</span>{' '}
          {editMode ? (
            <input
              value={tempData.AdministratorName}
              onChange={(e) => setTempData({ ...tempData, AdministratorName: e.target.value })}
              className="ml-2 text-black font-montserrat text-[3vh] border-b-2 border-main-dark-blue outline-none px-2 py-1"
            />
          ) : (
            <span className="text-black font-montserrat text-[3vh]">{subjectData.AdministratorName}</span>
          )}
        </div>

        {/* Actualizar, confirmar y cancelar */}
        {(userData.Type === "Administrador" || userData.Type === "Coordinador") ? (
            !editMode ? (
                <>
                    <button
                        className="custom-button absolute bottom-[3%] rounded font-montserrat text-[3vh] px-4 py-2"
                        onClick={handleUpdate}
                    >
                        Modificar Campos
                    </button>
                    <button
                        className="custom-button absolute bottom-[3%] left-[30%] rounded font-montserrat text-[3vh] px-4 py-2"
                        onClick={() => {
                            sessionStorage.removeItem("fromSubjectName");
                            sessionStorage.setItem('fromSubjectName', subjectData.Name);
                            window.location.href='/crear/actividad'
                        }}
                    >
                        Crear Actividad
                    </button>
                </>
            
            ) : (
            <div className="absolute bottom-[3%] flex gap-4">
                <button
                className="custom-button font-montserrat text-[3vh] px-4 py-2 rounded"
                onClick={handleConfirm}
                >
                Confirmar
                </button>
                <button
                className="custom-button font-montserrat text-[3vh] px-4 py-2 rounded bg-main-red hover:bg-red-900 "
                onClick={handleCancel}
                >
                Cancelar
                </button>
            </div>
            )
        ) : null}
      </section>
      <section className="absolute top-[25%] right-[5%] bg-white w-[40vw] text-center">
        <h2 className="section-title text-center mb-[1vh]">
          Actividades
        </h2>
        <div className="h-[60vh] border-main-dark-blue border-[0.5vh] overflow-y-auto">
          {activityList.map((activity, index) => {
            const color = getRandomColor(activity.ActivityID);
            return (
            <button
              key={activity.ActivityID}
              onClick={() =>{
                sessionStorage.removeItem('selectedActivityID');
                sessionStorage.setItem('selectedActivityID', activity.ActivityID);
                window.location.href = '/actividad';
              }}
              className="border-main-dark-blue w-full border-b-[0.5vh] text-white font-montserrat text-[3vh] font-semibold py-2"
              style={{ backgroundColor: color }}
            >
              {activity.ActivityName}
            </button>
            );
          })}
        </div>
      </section>
    </>
  )
}