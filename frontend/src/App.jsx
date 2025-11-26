import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Admin from "./pages/Admin";
import Resultados from "./pages/Resultados";

function App() {
  const [user, setUser] = useState(null); // Estado para armazenar o usuário logado

  const handleLoginSuccess = (email) => {
    setUser({ email }); // Define o usuário no estado
  };

  const handleLogout = () => {
    setUser(null); // Limpa o estado do usuário
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home user={user} onLogout={handleLogout} />} />
        <Route path="/login" element={<Login onLoginSuccess={handleLoginSuccess} />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/resultados" element={<Resultados user={user} onLogout={handleLogout} />} />
      </Routes>
    </Router>
  );
}

export default App;
