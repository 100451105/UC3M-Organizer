import {BrowserRouter, Routes, Route} from 'react-router-dom'
import Inicio from './pages/Inicio'
import Organizador from './pages/Organizador'
import Perfil from './pages/Perfil'

export default function App() {
  return(  
    <BrowserRouter>
        <Routes>
            <Route path="/" element={<Inicio />} />
            <Route path="/organizador" element={<Organizador />} />
            <Route path="/perfil" element={<Perfil />} />
        </Routes>
    </BrowserRouter>
  )
}