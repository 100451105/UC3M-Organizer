import axios from "axios";
import {useState} from "react";
import { UserCache } from "../common/Cache"

export default function LoginForm({ setLoadingState }) {
    {/* Funcion para construir el formulario de inicio de sesión */}
    const errorMessages = {
        401: "El correo electrónico no existe. Por favor, verifica el correo electrónico e inténtalo de nuevo.",
        402: "La contraseña es incorrecta. Por favor, verifica la contraseña e inténtalo de nuevo.",
        503: "Error de conexión con la base de datos. Por favor, inténtalo de nuevo más tarde.",
    };
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    {/* Funciones para realizar el inicio de sesión */}
    const handleLogin = async (e) => {
        e.preventDefault();
        setLoadingState(true);
        {/* Validación de los campos */}
        if (!email) {
            setLoadingState(false);
            return alert("Por favor, introduce el correo electrónico para iniciar sesión.");
        }
        if (!password) {
            setLoadingState(false);
            return alert("Por favor, introduce la contraseña para iniciar sesión.");
        }
        {/* Envío de datos al backend */}
        try {
            const loginResponse = await axios.post("http://localhost:8002/user/login/", {
                email: email,
                password: password
            });
            if (loginResponse.status === 200) {
                const userId = loginResponse.data.user.Id;
                await UserCache(userId);
                setLoadingState(false);
                alert("Inicio de sesión exitoso");
                window.location.href = "/main"; 
            }
        } catch (error) {
            setLoadingState(false);
            if (axios.isAxiosError(error)) {
                if (error.response) {
                    const message = "Error al iniciar sesión:\n" + (errorMessages[error.response.status] || "Error desconocido. Por favor, inténtalo de nuevo.");
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
            {/* Formulario de inicio de sesión */}
            <form onSubmit={handleLogin}
                className="flex flex-col items-center w-full"
            >
                <h2 className="text-[4.44vh] text-center font-bold font-montserrat text-black mb-[8vh]">
                    Iniciar Sesión
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