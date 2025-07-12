import {BrowserRouter, Routes, Route} from 'react-router-dom'
import Inicio from './pages/Inicio'
import Organizador from './pages/Organizador'
import Perfil from './pages/Perfil'
import Main from './pages/Main'
import Asignador from './pages/Asignador'
import Calendario from './pages/Calendario'
import Pendientes from './pages/Pendientes'
import Asignaturas from './pages/Asignaturas'

export default function App() {
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
        </Routes>
    </BrowserRouter>
  )
}