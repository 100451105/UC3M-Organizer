import {BrowserRouter, Routes, Route} from 'react-router-dom'
import Inicio from './pages/Inicio'
import Organizador from './pages/Organizador'
import Perfil from './pages/Perfil'
import Main from './pages/Main'
import Asignador from './pages/Asignador'
import Calendario from './pages/Calendario'
import Pendientes from './pages/Pendientes'
import Asignaturas from './pages/Asignaturas'
import Asignatura from './pages/Asignatura'
import Actividad from './pages/Actividad'
import CrearActividad from './pages/CrearActividad'


export default function App() {
  {/* Función principal para redirigir cada página a su correspondiente componente React */}
  return(  
    <BrowserRouter>
        <Routes>
            <Route path="/" element={<Inicio />} />
            <Route path="/main" element={<Main />} />
            <Route path="/organizador" element={<Organizador />} />
            <Route path="/calendario" element={<Calendario />} />
            <Route path="/perfil" element={<Perfil />} />
            <Route path="/asignador" element={<Asignador />} />
            <Route path="/pendientes" element={<Pendientes />} />
            <Route path="/asignaturas" element={<Asignaturas />} />
            <Route path="/asignatura" element={<Asignatura />} />
            <Route path="/actividad" element={<Actividad />} />
            <Route path="/crear/actividad" element={<CrearActividad />}/>
        </Routes>
    </BrowserRouter>
  )
}