import { useState, useEffect } from 'react';
import axios from 'axios';
import Header from "../components/common/Header";
import { UserCache } from '../components/common/Cache';
import { mainColors } from "../components/common/Colors";

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

export default function Asignaturas() {
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

  useEffect(() => {
    const fetchSubjectData = async () => {
      await UserCache(false);
      const user_info = JSON.parse(localStorage.getItem("user_info"));
      if (!user_info || user_info.Type === "Administrador") {
        alert("Acceso denegado a la sección de asignaturas");
        window.location.href = "/main";
      }
      // Asignaturas a mostrar
      try {
        const subjectInfo = await axios.get("http://localhost:8002/subject/info/");
        console.log("Respuesta del servidor:", subjectInfo.status);
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
  }, []);

  return (
    <>
      <Header showIndex={true} loadingInProgress={false}/>
      <h2 className="page-title">Panel de Asignaturas</h2>
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
              onClick={() => {
                // Aquí puedes hacer un POST al backend
                console.log("Confirmar asignatura:", tempData);
              }}
              className="custom-button mt-4 font-montserrat text-[3vh] px-4 py-2 rounded"
            >
              Confirmar
            </button>
          </div>
        )}
      </section>
      <section className="absolute top-[25%] right-[5%] bg-white w-[40vw] text-center">
        <h2 className="section-title text-center mb-[1vh]">
          Asignaturas
        </h2>
        <div className="h-[60vh] border-main-dark-blue border-[0.5vh] overflow-y-auto">
          {subjectList.map((subject, index) => {
            const color = getRandomColor(subject.SubjectName);
            return (
            <button
              key={subject.IdSubject}
              onClick={() =>{
                sessionStorage.setItem('selectedSubjectID', subject.IdSubject);
                window.location.href = '/asignaturas';
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