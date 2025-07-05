import {useState} from "react";

export default function RegisterForm() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleRegister = (e) => {
        e.PreventDefault();
        // Validación

        // Envío de datos al backend
        try {
            console.log("Email:", email);
            console.log("Password:", password);
        } catch (error) {
            console.error("Error al registrarse:", error);
        }
    };

    return (
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
                className="w-[18.59vw] h-[5vh] bg-main-blue-button text-white text-[2.96vh] 
                font-montserrat font-normal border-[0.37vh] border-main-dark-blue 
                rounded-[3.98vh]"
            >
                Aceptar
            </button>
        </form>
    );
}