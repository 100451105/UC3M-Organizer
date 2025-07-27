import { useState, useEffect } from 'react';
import axios from "axios";
import Header from "../components/common/Header";
import { UserCache } from '../components/common/Cache';

export default function CrearActividad() {
    {/* Función para crear la página de creación de actividades para una Asignatura */}
    const [loading, setLoadingState] = useState(true);
    const [userData, setUserData] = useState({});
    const [tempData, setTempData] = useState({});

    {/* Carga de datos */}
    useEffect(() => {
      const fetchData = async () => {
            await UserCache(false);
            const user_info = JSON.parse(localStorage.getItem("user_info"))

            {/* Asignatura a la que pertenece la actividad */}
            const subjectIdFrom = sessionStorage.getItem('selectedSubjectID');
            const subjectNameFrom = sessionStorage.getItem('fromSubjectName');
            setUserData(user_info);
            setTempData({
                Description: "",
                ActivityType: "Otros",
                StartOfActivity: null,
                EndOfActivity: new Date().toISOString().split("T")[0],
                SubjectID: subjectIdFrom,
                SubjectName: subjectNameFrom,
                ActivityName: "",
                EstimatedHours: 1,
                Strategy: "Completa"
            })
        }
        fetchData();
        setLoadingState(false);
    }, []);

    const handleConfirm = async () => {
      setLoadingState(true);
      {/* Petición para actualizar la información del usuario en el backend */}
      try {
          if (!tempData.Description || !tempData.ActivityType || !tempData.EndOfActivity || !tempData.ActivityName){
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
              activityName: tempData.ActivityName,
              estimatedHours: tempData.EstimatedHours,
              strategy: tempData.Strategy
          });
          if (updateResponse.status == 200) {
            alert("Actividad actualizada y reorganizada correctamente"); 
            window.location.href = '/asignatura'  
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
        localStorage.removeItem("activity_info");
      }
    };

    const handleCancel = () => {
      setTempData({});
      window.location.href = '/asignatura'
    };
    
    return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      {/* Formulario para Crear Actividad */}
      <h2 className="page-title">Crear Actividad</h2>
      <section className="bg-white rounded-xl p-6 w-[70vw] text-left">
        {/* Nombre */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Nombre :</span>{' '}
            <input
                value={tempData.ActivityName}
                onChange={(e) => setTempData({ ...tempData, ActivityName: e.target.value })}
                className="ml-2 border-b-2 border-main-dark-blue outline-none text-[3vh] font-montserrat text-black"
            />
        </div>
        {/* Descripción */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Descripción :</span>{' '}
            <input
                value={tempData.Description}
                onChange={(e) => setTempData({ ...tempData, Description: e.target.value })}
                className="ml-2 border-b-2 border-main-dark-blue outline-none text-[3vh] font-montserrat text-black"
            />
        </div>

        {/* Tipo */}
        <div className="mb-[3vh] flex items-center">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Tipo :</span>
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
        </div>

        {/* Comienzo */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Comienzo :</span>{' '}
            <input
                type="date"
                value={tempData.StartOfActivity?.slice(0, 10)}
                onChange={(e) => setTempData({ ...tempData, StartOfActivity: e.target.value === "" ? null : e.target.value })}
                className="ml-2 text-black font-montserrat text-[3vh] border-b-2 border-main-dark-blue outline-none px-2 py-1"
            />
        </div>

        {/* Final */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Fin :</span>{' '}
            <input
              type="date"
              value={tempData.EndOfActivity?.slice(0, 10)}
              onChange={(e) => setTempData({ ...tempData, EndOfActivity: e.target.value })}
              className="ml-2 text-black font-montserrat text-[3vh] border-b-2 border-main-dark-blue outline-none px-2 py-1"
            />
        </div>

        {/* Horas Estimadas */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Horas Estimadas :</span>{' '}
            <input
              type="number"
              value={tempData.EstimatedHours}
              min={1}
              onChange={(e) => setTempData({ ...tempData, EstimatedHours: e.target.value === "" ? "" : parseInt(e.target.value) })}
              className="ml-2 text-black font-montserrat text-[3vh] border-b-2 border-main-dark-blue outline-none px-2 py-1"
            />
        </div>

        {/* Asignatura a la que pertenece */}
        <div className="mb-[3vh]">
            <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">De Asignatura :</span>{' '}
            <span className="text-black font-montserrat text-[3vh]">{tempData.SubjectName}</span>
        </div>

        {/* Estrategia */}
        <div>
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Estrategia :</span>{' '}
            <select
              value={tempData.Strategy}
              onChange={(e) => setTempData({ ...tempData, Strategy: e.target.value })}
              className="ml-2 text-black font-montserrat text-[3vh] border-2 border-main-dark-blue rounded px-2 py-1"
            >
              <option value="Agresiva">Agresiva</option>
              <option value="Calmada">Calmada</option>
              <option value="Completa">Completa</option>
            </select>
        </div>

        {/* Actualizar, confirmar y cancelar */}
        {(userData.Type === "Administrador" || userData.Type === "Coordinador") ? (
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
            ) : null}
      </section>
    </>
  )
}