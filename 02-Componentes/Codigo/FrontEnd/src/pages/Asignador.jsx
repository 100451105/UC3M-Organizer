import { useState, useEffect } from 'react';
import Header from "../components/common/Header";
import axios from 'axios'
import { UserCache } from "../components/common/Cache";
import { mainColors } from "../components/common/Colors";

let subjectColorMap = {};

const getRandomColor = (userType) => {
    if (subjectColorMap[userType]) {
        return subjectColorMap[userType]
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
    subjectColorMap[userType] = chosenColorValue;
    return chosenColorValue;
}

export default function Asignador() {
  const [loading, setLoadingState] = useState(true);
  const [userList, setUserList] = useState([]);
  const [subjectList, setSubjectList] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  {/* Carga de datos de usuarios y asignaturas */}

  useEffect(() => {
    const fetchData = async () => {
      const user_info = JSON.parse(localStorage.getItem("user_info"));
      if (!user_info || (user_info.Type !== "Administrador" && user_info.Type !== "Coordinador")) {
        alert("Acceso denegado a la sección del asignador");
        window.location.href = "/main";
        return;
      }

      const Id = user_info.Id;
      await UserCache(Id);

      // Obtener asignaturas que el usuario es coordinador (si es administrador, todas las asignaturas)
      try {
        let subjectInfo = 0
        if (user_info.Type === "Administrador") {
          subjectInfo = await axios.get("http://localhost:8002/subject/coordinator/info/");
        }
        else {
          subjectInfo = await axios.get("http://localhost:8002/subject/coordinator/info/", {
            withCredentials: true,
            params: {
                userId: Id
            }
          });
        }
        console.log("Respuesta del servidor:", subjectInfo.status);
        if (subjectInfo.status === 200) {
          let subjects = subjectInfo.data.subjectList;
          // Asignatura por defecto, ninguno
          const noneSubject = { IdSubject: -1, Name: "Ninguno" };
          subjects = [noneSubject, ...subjects];
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

      setSelectedSubject({ IdSubject: -1, Name: "Ninguno" });
      setLoadingState(false);
    };

    fetchData();
  }, []);

  useEffect(() => {
    let initiallyAssigned = userList
      .filter((u) => u.assigned)
      .map((u) => u.user);

    setSelectedUsers(initiallyAssigned);
  }, [userList]);

  let filteredUsers = userList.filter((u) =>
    u.user.toLowerCase().includes(searchTerm.toLowerCase())
  );


  {/* Funciones para asignar/desasignar usuarios */}

  const handleUserToggle = (email) => {
    setSelectedUsers((prev) =>
      prev.includes(email)
        ? prev.filter((u) => u !== email)
        : [...prev, email]
    );
  };

  const handleSelectAll = () => {
    const filtered = filteredUsers.map((u) => u.user);
    const allSelected = filtered.every((email) => selectedUsers.includes(email));
    setSelectedUsers(allSelected ? selectedUsers.filter((u) => !filtered.includes(u)) : [...new Set([...selectedUsers, ...filtered])]);
  };

  {/* Handlers que requieren peticiones al backend */}

  const handleConfirm = async () => {
    setLoadingState(true);
    if (selectedSubject.IdSubject === -1){
      alert("No puedes asignar usuarios sin seleccionar una asignatura")
      setLoadingState(false);
      return;
    }
    try {
      console.log(userList)
      const changedUsers = userList
        .filter((u) => {
          const wasAssigned = u.assigned;
          const isNowAssigned = selectedUsers.includes(u.user);
          return wasAssigned !== isNowAssigned;
        })
        .map((u) => ({
          userId: Number(u.id),
          assigned: selectedUsers.includes(u.user),
        }));
      console.log(changedUsers);
      const confirmation = await axios.post("http://localhost:8002/subject/assignments/", {
        users: changedUsers,
        subjectId: Number(selectedSubject.IdSubject)
      });
      console.log("Respuesta del servidor:", confirmation.status);
      if (confirmation.status === 200) {
        alert("Usuarios asignados correctamente a la asignatura");
        window.location.href = '/asignador';
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response) {
            const message = "Error al modificar los datos:\n" + error.response.status || "Error desconocido. Por favor, inténtalo de nuevo.";
            console.error(message);
            console.error(error.response);
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
    finally{
      setLoadingState(false);
    }
  }

  const handleSubjectSelection = async (e) => {
    setLoadingState(true);
    const selectedId = parseInt(e.target.value);
    const selected = subjectList.find((s) => s.IdSubject === selectedId);
    setSelectedSubject(selected);

    if (selectedId === -1) {
      // Asignatura "Ninguno" seleccionada → vaciar usuarios
      setUserList([]);
      setSelectedUsers([]);
      setLoadingState(false);
      return;
    }
    
    try {
      const response = await axios.get("http://localhost:8002/subject/assigned/info/", {
        withCredentials: true,
        params: {
          subjectId: selectedId
        }
      });
      if (response.status === 200) {
        const user_list = response.data.userList.map((userItem) => ({
          user: userItem.Username,
          userType: userItem.Type,
          id: userItem.Id,
          assigned: Boolean(userItem.IsAssigned)
        }));
        const initiallyAssigned = user_list
          .filter((u) => u.assigned)
          .map((u) => u.user);
        setUserList(user_list);
        setSelectedUsers(initiallyAssigned);
      }
    } catch (error) {
      console.error("Error al cargar los usuarios de la asignatura:", error);
      alert("Hubo un error al obtener los usuarios de esta asignatura.");
      setUserList([]); // Vaciar como fallback de error
    }
    setLoadingState(false);
  }

  

  return (
    <>
      <Header showIndex={true} loadingInProgress={loading} />
      <h2 className="page-title">Asignador</h2>

      {/* 🔴 Parte Izquierda */}
      <section className="absolute top-[30%] left-[2%] bg-white w-[45vw] h-[60vh] text-left rounded-xl">
        <p className="text-[3vh] font-bold text-main-dark-blue font-montserrat mb-4">
          Asignando Usuarios a la Asignatura:
          <select
            value={selectedSubject?.IdSubject || ""}
            onChange={handleSubjectSelection}
            className="ml-3 p-1 border border-gray-400 rounded text-[2.2vh]"
          >
            {subjectList.map((subject) => (
              <option key={subject.IdSubject} value={subject.IdSubject}>
                {subject.Name}
              </option>
            ))}
          </select>
        </p>
        {/* Contenedor de usuarios con cambios */}
        <p className="text-[3vh] font-bold text-main-dark-blue font-montserrat mb-2"> Cambios realizados: </p>
        <div className="bg-[#f9f9f9] border border-gray-300 rounded p-3 h-[35vh] overflow-y-auto">
          {userList
            .filter((u) => {
              const wasAssigned = u.assigned;
              const isNowAssigned = selectedUsers.includes(u.user);
              return wasAssigned !== isNowAssigned;
            })
            .map((u, index) => {
              const isNowAssigned = selectedUsers.includes(u.user);
              return (
                <div
                  key={u.user}
                  className="flex justify-between items-center border-b border-gray-300 py-2 px-1 text-[2.2vh] font-montserrat"
                >
                  <span>{u.user}</span>
                  {isNowAssigned ? (
                    <span className="text-green-600 text-[2.5vh] font-bold">✔️</span>
                  ) : (
                    <span className="text-red-600 text-[2.5vh] font-bold">❌</span>
                  )}
                </div>
              );
            })}
          {/* Si no hay cambios */}
          {userList.filter((u) => u.assigned !== selectedUsers.includes(u.user)).length === 0 && (
            <p className="text-gray-500 italic text-[2vh] text-center">No hay cambios pendientes.</p>
          )}
        </div>

        <button
          onClick={handleConfirm}
          className="absolute bottom-[1%] custom-button rounded font-montserrat text-[2.5vh] px-4 py-2 mt-4"
        >
          Asignar Usuarios
        </button>
      </section>

      {/* 🟢 Parte Derecha */}
      <section className="absolute top-[20%] right-[5%] bg-white w-[40vw] text-left p-4 rounded-xl">
        <h2 className="section-title mb-2 text-center">Usuarios</h2>

        {/* Search */}
        <div className="mb-2 relative">
          <input
            type="text"
            placeholder="Buscar..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full border border-gray-400 rounded-xl px-3 py-2 bg-gray-100"
          />
        </div>

        {/* Select All */}
        <div className="flex items-center mb-2">
          <input
            type="checkbox"
            checked={filteredUsers.length > 0 && filteredUsers.every((u) => selectedUsers.includes(u.user))}
            onChange={handleSelectAll}
            className="mr-2 w-5 h-5 accent-main-dark-blue"
          />
          <label className="text-[2.5vh] font-semibold">Select All</label>
        </div>

        {/* User List */}
        <div className="h-[40vh] overflow-y-auto border border-main-dark-blue">
          {filteredUsers.length > 0 ? (
            filteredUsers.map((u, i) => {
            const color = getRandomColor(u.userType)
            return (
            <div
              key={u.user}
              className="flex items-center border-b border-gray-300 px-2 py-2"
              style={{ backgroundColor: color || "#ccc" }}
            >
              <input
                type="checkbox"
                checked={selectedUsers.includes(u.user)}
                onChange={() => handleUserToggle(u.user)}
                className="mr-2 w-5 h-5 accent-main-dark-blue"
              />
              <span className="text-white font-montserrat text-[2vh]">
                {u.user}
              </span>
            </div>
          );
          })
          ) : (
            <p className="text-center text-gray-500 p-1 font-montserrat">Selecciona una asignatura para visualizar los usuarios asignados y desasignados de dicha asignatura</p>
          )
          }
        </div>

        <p className="mt-3 text-[3vh] font-semibold">
          Seleccionados: {selectedUsers.length} usuario{selectedUsers.length !== 1 && "s"}
        </p>
      </section>
    </>
  );
}