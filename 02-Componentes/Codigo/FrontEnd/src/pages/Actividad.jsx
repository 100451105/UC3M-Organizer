import { useState, useEffect } from 'react';
import axios from "axios";
import Header from "../components/common/Header";
import { UserCache } from '../components/common/Cache';

export default function Asignatura() {
    {/* Cambiar entre modo edición y modo lectura */}
    const [editMode, setEditMode] = useState(false);
    const [loading, setLoadingState] = useState(true);
    const [activityData, setactivityData] = useState({});
    const [userData, setUserData] = useState({});
    const [tempData, setTempData] = useState({...activityData});

    useEffect(() => {
      const fetchData = async () => {
            await UserCache(false);
            const user_info = JSON.parse(localStorage.getItem("user_info"))

            {/* Get data of the subject in order to populate the page dinamically */}
            const activityId = sessionStorage.getItem('selectedActivityID');
            try {
                const activityInfo = await axios.get("http://localhost:8002/activities/specific/info/", {
                    withCredentials: true,
                    params: {
                        activityId: activityId
                    }
                });
                console.log("Respuesta del servidor:", activityInfo.status);
                if (activityInfo.status == 200) {
                    setactivityData(activityInfo.data.activityInfo);
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
        }
        fetchData();
    }, []);

    const handleUpdate = () => {
      setTempData({...activityData});
      setEditMode(true);
    }

    const handleConfirm = async () => {
      setLoadingState(true);
      
      {/* Petición para actualizar la información del usuario en el backend */}
      
      try {
          if (!tempData.Description || !tempData.ActivityType || !tempData.EndOfActivity){
            alert("Alguno de los campos de texto introducidos está vacío. Por favor, rellene dichos campos antes de confirmar de nuevo")
            setLoadingState(false);
            return;
          }
          const updateResponse = await axios.post("http://localhost:8002/activities/update/", {
              description: tempData.Description,
              type: tempData.ActivityType,
              startOfActivity: tempData.StartOfActivity,
              endOfActivity: tempData.EndOfActivity,
              subjectId: tempData.SubjectID,
              activityName: activityData.ActivityName,
              activityId: activityData.ActivityID,
              estimatedHours: tempData.EstimatedHours,
              strategy: tempData.Strategy
          });
          
          console.log("Respuesta del servidor:", updateResponse.status);
          if (updateResponse.status == 200) {
            alert("Actividad actualizada y reorganizada correctamente"); 
          }
      } catch (error) {
        console.log(error.response);
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
        window.location.href = '/actividad'
      }
    };

    const handleCancel = () => {
      setTempData({...activityData});
      setEditMode(false);
    };

    useEffect(() => {
      setLoadingState(false);
    })
    
    return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      <h2 className="page-title">{activityData.ActivityName}</h2>
      <section className="bg-white rounded-xl p-6 w-[70vw] text-left">
        {/* Descripción */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Descripción :</span>{' '}
            {editMode ? (
            <input
                value={tempData.Description}
                onChange={(e) => setTempData({ ...tempData, Description: e.target.value === "" ? "" : parseInt(e.target.value) })}
                className="ml-2 border-b-2 border-main-dark-blue outline-none text-[3vh] font-montserrat text-black"
            />
          ) : (
            <>
              <span className="ml-2 font-montserrat text-[3vh] text-black">
                {activityData.Description}
              </span>
            </>
          )}
        </div>

        {/* Tipo */}
        <div className="mb-[3vh] flex items-center">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Tipo :</span>
          {editMode ? (
            <select
              value={tempData.ActivityType}
              onChange={(e) => setTempData({ ...tempData, ActivityType: e.target.value })}
              className="ml-2 text-black font-montserrat text-[3vh] border-2 border-main-dark-blue rounded px-2 py-1"
            >
              <option value="Examen">Examen</option>
              <option value="Actividad">Actividad</option>
              <option value="Laboratorio">Laboratorio</option>
              <option value="Clase">Clase</option>
              <option value="Otros">Otros</option>
            </select>
          ) : (
            <>
              <span className="ml-2 font-montserrat text-[3vh] text-black">
                {activityData.ActivityType}
              </span>
            </>
          )}
        </div>

        {/* Comienzo */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Comienzo :</span>{' '}
          {editMode ? (
            <input
                type="date"
                value={tempData.StartOfActivity?.slice(0, 10)}
                onChange={(e) => setTempData({ ...tempData, StartOfActivity: e.target.value === "" ? null : e.target.value })}
                className="ml-2 text-black font-montserrat text-[3vh] border-b-2 border-main-dark-blue outline-none px-2 py-1"
            />
          ) : (
            <span className="text-black font-montserrat text-[3vh]">{activityData.StartOfActivity}</span>
          )}
        </div>

        {/* Final */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Fin :</span>{' '}
          {editMode ? (
            <input
              type="date"
              value={tempData.EndOfActivity?.slice(0, 10)}
              onChange={(e) => setTempData({ ...tempData, EndOfActivity: e.target.value })}
              className="ml-2 text-black font-montserrat text-[3vh] border-b-2 border-main-dark-blue outline-none px-2 py-1"
            />
          ) : (
            <span className="text-black font-montserrat text-[3vh]">{activityData.EndOfActivity}</span>
          )}
        </div>

        {/* Horas Estimadas */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Horas Estimadas :</span>{' '}
          {editMode ? (
            <input
              type="number"
              value={tempData.EstimatedHours}
              min={1}
              onChange={(e) => setTempData({ ...tempData, EstimatedHours: e.target.value === "" ? "" : parseInt(e.target.value) })}
              className="ml-2 text-black font-montserrat text-[3vh] border-b-2 border-main-dark-blue outline-none px-2 py-1"
            />
          ) : (
            <span className="text-black font-montserrat text-[3vh]">{activityData.EstimatedHours}</span>
          )}
        </div>

        {/* Asignatura a la que pertenece */}
        <div className="mb-[3vh]">
            <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">De Asignatura :</span>{' '}
            <span className="text-black font-montserrat text-[3vh]">{activityData.SubjectName}</span>
        </div>

        {/* Estado */}
        <div className="mb-[3vh]">
            <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Estado :</span>{' '}
            <span className="text-black font-montserrat text-[3vh]">{activityData.Status}</span>
        </div>

        {/* Estrategia */}
        <div>
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Estrategia :</span>{' '}
          {editMode ? (
            <select
              value={tempData.Strategy}
              onChange={(e) => setTempData({ ...tempData, Strategy: e.target.value })}
              className="ml-2 text-black font-montserrat text-[3vh] border-2 border-main-dark-blue rounded px-2 py-1"
            >
              <option value="Agresiva">Agresiva</option>
              <option value="Calmada">Calmada</option>
              <option value="Completa">Completa</option>
            </select>
          ) : (
            <span className="text-black font-montserrat text-[3vh]">{activityData.Strategy}</span>
          )}
        </div>

        {/* Actualizar, confirmar y cancelar */}
        {(userData.Type === "Administrador" || userData.Type === "Coordinador") ? (
            !editMode ? (
                <>
                    <button
                        className="custom-button absolute bottom-[3%] right-[3%] rounded font-montserrat text-[3vh] px-4 py-2"
                        onClick={handleUpdate}
                    >
                        Modificar Campos
                    </button>
                </>
            
            ) : (
            <div className="absolute bottom-[3%] right-[3%] flex gap-4">
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
    </>
  )
}