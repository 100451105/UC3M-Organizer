import Logo from "../../images/Logo_UC3M.png"
import {useState} from "react";
import Loading from "./Loading";

const TITULOS = [
    "Inicio",
    "Organizador",
    "Calendario",
    "Mi Perfil",
    "Asignador",
    "Pendientes",
    "Asignaturas",
]

const REDIRECTS = {
    "Inicio": "/main",
    "Organizador": "/organizador",
    "Calendario": "/calendario",
    "Mi Perfil": "/perfil",
    "Asignador": "/asignador",
    "Pendientes": "/pendientes",
    "Asignaturas": "/asignaturas",
}

export default function Header({ showIndex, loadingInProgress }) {
    {/* Función común a todas las páginas para la creación de la cabecera y la pantalla de carga */}
    const [index, setIndex] = useState(0);

    const previous = () => {
        {/* Mover la lista de títulos hacia atrás */}
        if (index - 4 >= 0) {
            setIndex(index - 4);
        }
    };

    const next = () => {
        {/* Mover la lista de títulos hacia delante */}
        if (index + 4 < TITULOS.length) {
            setIndex(index + 4);
        }
    }

    return (
        <>
            <header className="fixed top-0 left-0 w-full h-[12.5vh] bg-main-dark-blue z-50">
                <div className="header-content">
                    <img src={Logo} alt="UC3M Organizer Logo" className="header-logo" />
                    <h1 className="header-title">Organizador</h1>
                </div>

                <Loading loadingInProgress={loadingInProgress}/>
                {/* Cabecera de navegación para ordenador */}
                {showIndex && (
                    <div className= "w-full h-[7.5vh] mt-[12.5vh] bg-white border-[0.37vh] border-main-dark-blue flex items-center justify-between px-[1.77vw]">
                        {/* Botón de la izquierda */}
                        {index > 0 ? (
                            <button 
                                className="w-[6.48vh] h-[6.48vh] custom-button rounded-full flex items-center justify-center"
                                onClick={previous}
                            >
                                <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="white"
                                strokeWidth="0.65vh"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="w-[4vh] h-[4vh]"
                                >
                                <polyline points="13 22 2 12 13 2 2 12 22 12" vectorEffect="non-scaling-stroke"></polyline>
                                </svg>
                            </button>
                        ) : (
                            <div className="w-[6.48vh]" />
                        )}

                        {/* Títulos de las distintas secciones */}
                        <div className="flex gap-[3.5vw] justify-center items-center flex-1">
                            {TITULOS.slice(index, index + 4).map((titulo, i) => (
                                <button 
                                    key={i}
                                    className="w-[17.5vw] h-[5.46vh] custom-button flex items-center justify-center"
                                    onClick={() => window.location.href = REDIRECTS[titulo]}
                                >
                                    <span className="nav-bar-text">
                                        {titulo}
                                    </span>
                                </button>
                            ))}
                        </div>

                        {/* Botón de la derecha */}
                        {index + 4 < TITULOS.length ? (
                            <button 
                                className="w-[6.48vh] h-[6.48vh] custom-button rounded-full flex items-center justify-center"
                                onClick={next}
                            >
                                <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="white"
                                strokeWidth="0.65vh"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="w-[4vh] h-[4vh]"
                                >
                                <polyline points="11 22 22 12 11 2 22 12 2 12" vectorEffect="non-scaling-stroke"></polyline>
                                </svg>
                            </button>
                            ) : (
                            <div className="w-[6.48vh]" />
                        )}
                    </div>
                )}
            </header>
            {!showIndex && (
                <div className="h-[12.5vh]"></div>
            )}
            {showIndex && (
                <div className="h-[20vh]"></div>
            )}
        </>
    );
}