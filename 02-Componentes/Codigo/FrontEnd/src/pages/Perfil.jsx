import { useState, useEffect } from 'react';
import axios from "axios";
import Header from "../components/common/Header";
import { mainColors } from "../components/common/Colors";
import { UserCache } from '../components/common/Cache';

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

export default function Perfil() {
    {/* Función para crear la página de información sobre el Usuario y las Asignaturas asignadas */}
    const [editMode, setEditMode] = useState(false);
    const [loading, setLoadingState] = useState(true);
    const [show, setShownPassword] = useState(false);
    const [userData, setUserData] = useState({});
    const [tempData, setTempData] = useState({...userData});
    const [subjectList, setSubjectList] = useState([]);

    {/* Carga de datos */}
    useEffect(() => {
      const fetchUserData = async () => {
        await UserCache(false);
        const user_info = JSON.parse(localStorage.getItem("user_info"))
        setUserData({
          username: user_info.Username,
          password: user_info.Password,
          type: user_info.Type,
          id: user_info.Id
        });
        setSubjectList(user_info.relatedSubjectsList);
      }
      fetchUserData();
      setLoadingState(false);
    }, []);

    const handleUpdate = () => {
      setTempData({...userData});
      setEditMode(true);
    }

    const handleConfirm = async () => {
      setLoadingState(true);
      {/* Petición para actualizar la información del usuario en el backend */}
      try {
          if (!tempData.username || !tempData.password){
            alert("Alguno de los campos de texto introducidos está vacío. Por favor, rellene dichos campos antes de confirmar de nuevo")
            setLoadingState(false);
            return;
          }
          const updateResponse = await axios.post("http://localhost:8002/user/update/", {
              username: tempData.username,
              password: tempData.password,
              userType: tempData.type,
              userId: tempData.id
          });
          if (updateResponse.status == 200) {
            alert("Datos actualizados correctamente"); 
            setUserData({...tempData});
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
        setEditMode(false);
        setLoadingState(false);
      }
    };

    const handleCancel = () => {
      setTempData({...userData});
      setEditMode(false);
    };
    
    return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      <h2 className="page-title">Perfil</h2>
      {/* Sección de información del Usuario / Formulario */}
      <section className="bg-white rounded-xl p-6 w-[50vw] text-left">
        {/* Usuario */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Usuario :</span>{' '}
            <span className="text-black font-montserrat text-[3vh]">{userData.username}</span>
        </div>

        {/* Contraseña */}
        <div className="mb-[3vh] flex items-center">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Contraseña :</span>
          {editMode ? (
            <input
              type="password"
              value={tempData.password}
              onChange={(e) => setTempData({ ...tempData, password: e.target.value })}
              className="ml-2 border-b-2 border-main-dark-blue outline-none text-[3vh] font-montserrat text-black"
            />
          ) : (
            <>
              <span className="ml-2 font-montserrat text-[3vh] tracking-widest text-black">
                {show ? userData.password : "*******************"}
              </span>
              <button 
                className="ml-2 text-gray-600 hover:text-black"
                onClick={() => setShownPassword(!show)}
              >👁️
              </button>
            </>
          )}
        </div>

        {/* Tipo de Usuario */}
        <div className="mb-[3vh]">
          <span className="text-main-dark-blue font-montserrat font-bold text-[3vh]">Tipo :</span>{' '}
          {editMode ? (
            <select
              value={tempData.type}
              onChange={(e) => setTempData({ ...tempData, type: e.target.value })}
              className="ml-2 text-black font-montserrat text-[3vh] border-2 border-main-dark-blue rounded px-2 py-1"
            >
              <option value="Estudiante">Estudiante</option>
              <option value="Profesor">Profesor</option>
              <option value="Otros">Otros</option>
            </select>
          ) : (
            <span className="text-black font-montserrat text-[3vh]">{userData.type}</span>
          )}
        </div>

        {/* Actualizar, confirmar y cancelar */}
        {!editMode ? (
          <button
            className="custom-button absolute bottom-[3%] rounded font-montserrat text-[3vh] px-4 py-2"
            onClick={handleUpdate}
          >
            Actualizar Campos
          </button>
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
        )}
      </section>
      {/* Sección de información de las Asignaturas que tiene Asignadas */}
      <section className="absolute top-[25%] right-[5%] bg-white w-[40vw] text-center">
        <h2 className="section-title text-center mb-[1vh]">
          Asignaturas
        </h2>
        <div className="h-[60vh] border-main-dark-blue border-[0.5vh] overflow-y-auto">
          {subjectList.map((subject, index) => {
            const color = getRandomColor(subject.SubjectName);
            return (
            <button
              key={subject.SubjectID}
              onClick={() =>{
                sessionStorage.removeItem('selectedSubjectID');
                sessionStorage.setItem('selectedSubjectID', subject.SubjectID);
                window.location.href = '/asignatura';
              }}
              className="border-main-dark-blue w-full border-b-[0.5vh] text-white font-montserrat text-[3vh] font-semibold py-2"
              style={{ backgroundColor: color }}
            >
              {subject.SubjectName}
            </button>
            );
          })}
        </div>
      </section>
    </>
  )
}