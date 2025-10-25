import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./reset.css";
import App from "./App.jsx"; // Importa o componente App

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App /> {/* Renderiza o App */}
  </StrictMode>
);
