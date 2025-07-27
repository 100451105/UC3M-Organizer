import {useState} from "react";
import axios from "axios";
import { UserCache } from "../common/Cache";

export default function RegisterForm({ setLoadingState }) {
    {/* Funcion para construir el formulario de crear una cuenta */}
    const errorMessages = {
        401: "Ya existe una cuenta con ese correo electrónico. Por favor, utiliza otro o inicia sesión en esa cuenta.",
        503: "Error de conexión con la base de datos. Por favor, inténtalo de nuevo más tarde.",
        505: "Error interno del servidor. Por favor, inténtalo de nuevo más tarde.",
    };
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    {/* Funciones para realizar el registro de la cuenta */}
    const handleRegister = async (e) => {
        e.preventDefault();
        setLoadingState(true);
        {/* Validación de los campos */}
        if (!email) {
            setLoadingState(false);
            return alert("Por favor, introduce el correo electrónico para crear una cuenta.");
        }
        if (!password) {
            setLoadingState(false);
            return alert("Por favor, introduce la contraseña para crear una cuenta.");
        }
        {/* Envío de datos al backend */}
        try {
            console.log("Enviando datos de inicio de sesión:", { email, password });
            const regitryResponse = await axios.post("http://localhost:8002/user/register/", {
                email: email,
                password: password
            });
            console.log("Respuesta del servidor:", regitryResponse.status);
            
            if (regitryResponse.status === 200) {
                const userId = regitryResponse.data.userId;
                console.log("Inicio de sesión exitoso:", userId);
                await UserCache(userId);
                setLoadingState(false);
                alert("Inicio de sesión exitoso");
                window.location.href = "/main"; 
            }
        } catch (error) {
            setLoadingState(false);
            if (axios.isAxiosError(error)) {
                if (error.response) {
                    const message = "Error al crear una cuenta:\n" + (errorMessages[error.response.status] || "Error desconocido. Por favor, inténtalo de nuevo.");
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
    };

    return (
        <>
            {/* Formulario de registro de cuenta */}
            <form onSubmit={handleRegister}
                className="flex flex-col items-center w-full"
            >
                <h2 className="text-[4.44vh] font-bold font-montserrat text-black mb-[8vh]">
                    Crear Cuenta
                </h2>
                <input
                    type="email"
                    placeholder="Correo electrónico"
                    value={email}
                    className="w-[29.95vw] h-[7.96vh] border-[0.37vh] border-main-dark-blue/75 
                            rounded-[3.98vh] text-center font-montserrat text-[2.96vh]
                            placeholder-opacity-50 placeholder:text-[clamp(2vh, 2.5vw, 2.96vh)] placeholder:text-center 
                            placeholder:font-montserrat placeholder:font-normal text-black mb-[5vh]"
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Contraseña"
                    value={password}
                    className="w-[29.95vw] h-[7.96vh] border-[0.37vh] border-main-dark-blue/75 
                            rounded-[3.98vh] text-center font-montserrat text-[2.96vh] 
                            placeholder-opacity-50 placeholder:text-[clamp(2vh, 2.5vw, 2.96vh)] placeholder:text-center 
                            placeholder:font-montserrat placeholder:font-normal text-black mb-[10vh]"
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button 
                    type="submit"
                    className="w-[18.59vw] h-[5vh] custom-button text-[2.96vh] 
                    font-montserrat font-normal border-[0.37vh] border-main-dark-blue 
                    rounded-[3.98vh]"
                >
                    Aceptar
                </button>
            </form>
        </>
    );
}