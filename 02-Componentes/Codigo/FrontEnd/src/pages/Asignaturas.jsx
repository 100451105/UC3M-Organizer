import { useState, useEffect } from 'react';
import axios from 'axios';
import Header from "../components/common/Header";
import { UserCache } from '../components/common/Cache';
import { mainColors } from "../components/common/Colors";

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

export default function Asignaturas() {
  {/* Función para crear la página de la información sobre las distintas asignaturas y creación de estas */}
  const [subjectList, setSubjectList] = useState([]);
  const [loading, setLoadingState] = useState(true);
  const [createMode, setCreateMode] = useState(false);
  const [tempData, setTempData] = useState({
    subjectName: "",
    subjectId: "",
    subjectCredits: 1,
    subjectSemester: 1,
    subjectYear: 1,
    subjectCoordinator: ""
  });

  {/* Carga de datos */}
  useEffect(() => {
    const fetchSubjectData = async () => {
      const user_info = JSON.parse(localStorage.getItem("user_info"));
      if (!user_info || user_info.Type !== "Administrador") {
        alert("Acceso denegado a la sección de asignaturas");
        window.location.href = "/main";
      }
      const Id = user_info.Id;
      await UserCache(Id);
      {/* Asignaturas a mostrar */}
      try {
        const subjectInfo = await axios.get("http://localhost:8002/subject/info/");
        if (subjectInfo.status === 200) {
          const subjects = subjectInfo.data.subjectList;
          setSubjectList(subjects);
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
    fetchSubjectData();
    setLoadingState(false);
  }, []);

  const handleConfirm = async () => {
    setLoadingState(true);
    {/* Petición para actualizar/crear la asignatura en el backend */}
    try {
        if (!tempData.subjectId || !tempData.subjectName || !tempData.subjectCredits || !tempData.subjectSemester || !tempData.subjectYear){
          alert("Alguno de los campos de texto introducidos está vacío. Por favor, rellene dichos campos antes de confirmar de nuevo")
          setLoadingState(false);
          return;
        }
        const updateResponse = await axios.post("http://localhost:8002/subject/update/", {
            credits: tempData.subjectCredits,
            semester: tempData.subjectSemester,
            year: tempData.subjectYear,
            name: tempData.subjectName,
            subjectId: tempData.subjectId,
            coordinator: tempData.subjectCoordinator
        });
        if (updateResponse.status == 200) {
          alert("Datos actualizados correctamente"); 
          window.location.href = '/asignaturas';
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
      setCreateMode(false);
      setLoadingState(false);
    }
  };

  return (
    <>
      <Header showIndex={true} loadingInProgress={loading}/>
      
      <h2 className="page-title">Panel de Asignaturas</h2>
      {/* Creación de Asignaturas */}
      <section className="bg-white rounded-xl p-6 w-[50vw] text-left">
        {/* Botón para crear asignatura */}
        {!createMode ? (
          <button
            onClick={() => setCreateMode(true)}
            className="custom-button rounded font-montserrat text-[3vh] px-4 py-2"
          >
            Crear Asignatura
          </button>
        ) : (
          <button
            onClick={() => {
              setCreateMode(false);
              setTempData({
                subjectName: "",
                subjectId: "",
                subjectCredits: 1,
                subjectSemester: 1,
                subjectYear: 1,
                subjectCoordinator: ""
              });
            }}
            className="bg-red-600 text-white rounded font-montserrat text-[3vh] px-4 py-2"
          >
            Cancelar
          </button>
        )}
        {createMode && (
          <div className="mt-4 space-y-3 text-[2.5vh] font-montserrat">
            <div>
              <span className="font-bold text-main-dark-blue">Nombre :</span>{' '}
              <input
                type="text"
                value={tempData.subjectName}
                onChange={(e) => setTempData({ ...tempData, subjectName: e.target.value })}
                className="ml-2 border-b-2 border-gray-400 focus:outline-none"
              />
            </div>
            <div>
              <span className="font-bold text-main-dark-blue">Código de Asignatura :</span>{' '}
              <input
                type="text"
                value={tempData.subjectId}
                onChange={(e) => setTempData({ ...tempData, subjectId: e.target.value })}
                className="ml-2 border-b-2 border-gray-400 focus:outline-none"
              />
            </div>
            <div>
              <span className="font-bold text-main-dark-blue">Créditos :</span>{' '}
              <input
                type="number"
                min={1}
                max={30}
                value={tempData.subjectCredits}
                onChange={(e) => setTempData({ ...tempData, subjectCredits: e.target.value === "" ? "" : parseInt(e.target.value) })}
                className="ml-2 w-16 border-b-2 border-gray-400 focus:outline-none"
              />
            </div>
            <div>
              <span className="font-bold text-main-dark-blue">Cuatrimestre :</span>{' '}
              <input
                type="number"
                min={1}
                max={2}
                value={tempData.subjectSemester}
                onChange={(e) => setTempData({ ...tempData, subjectSemester: e.target.value === "" ? "" : parseInt(e.target.value) })}
                className="ml-2 w-12 border-b-2 border-gray-400 focus:outline-none"
              />
            </div>
            <div>
              <span className="font-bold text-main-dark-blue">Año :</span>{' '}
              <input
                type="number"
                min={1}
                max={4}
                value={tempData.subjectYear}
                onChange={(e) => setTempData({ ...tempData, subjectYear: e.target.value === "" ? "" : parseInt(e.target.value) })}
                className="ml-2 w-12 border-b-2 border-gray-400 focus:outline-none"
              />
            </div>
            <div>
              <span className="font-bold text-main-dark-blue">Tutor :</span>{' '}
              <input
                type="email"
                value={tempData.subjectCoordinator}
                onChange={(e) => setTempData({ ...tempData, subjectCoordinator: e.target.value })}
                className="ml-2 border-b-2 border-gray-400 focus:outline-none"
              />
            </div>

            <button
              onClick={handleConfirm}
              className="custom-button mt-4 font-montserrat text-[3vh] px-4 py-2 rounded"
            >
              Confirmar
            </button>
          </div>
        )}
      </section>
      {/* Lista de Asignaturas Existentes */}
      <section className="absolute top-[25%] right-[5%] bg-white w-[40vw] text-center">
        <h2 className="section-title text-center mb-[1vh]">
          Asignaturas
        </h2>
        <div className="h-[60vh] border-main-dark-blue border-[0.5vh] overflow-y-auto">
          {subjectList.map((subject, index) => {
            const color = getRandomColor(subject.Name);
            return (
            <button
              key={subject.IdSubject}
              onClick={() =>{
                sessionStorage.removeItem('selectedSubjectID');
                sessionStorage.setItem('selectedSubjectID', subject.IdSubject);
                window.location.href = '/asignatura';
              }}
              className="border-main-dark-blue w-full border-b-[0.5vh] text-white font-montserrat text-[3vh] font-semibold py-2"
              style={{ backgroundColor: color }}
            >
              {subject.Name}
            </button>
            );
          })}
        </div>
      </section>
    </>
  )
}