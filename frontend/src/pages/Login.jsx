import styles from "../pages/Login.module.css";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";
import axios from "axios";

function Login({ onLoginSuccess }) {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await axios.post("http://localhost:8080/login", {
        email: email,
        senha: password,
      });

      if (response.status === 200) {
        alert("Login realizado com sucesso!");
        onLoginSuccess(email);
        navigate("/");
      }
    } catch (err) {
      console.error("Erro ao fazer login:", err);
      setError("Email ou senha inválidos. Por favor, tente novamente.");
    }
  };

  return (
    <div className={styles.background}>
      <div className={styles.container}>
        <h1 className={styles.title}>
          Bem-vindo ao{" "}
          <span>
            FOMENT<span className={styles.ai}>.AI</span>
          </span>
        </h1>
        <form onSubmit={handleSubmit}>
          <div className={styles.inputs}>
            <div className={styles.email}>
              <label>Email</label>
              <input
                type="email"
                placeholder="Endereço de EMAIL"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className={styles.password}>
              <label>Sua senha</label>
              <div className={styles.passwordWrapper}>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Senha"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <span
                  onClick={() => setShowPassword(!showPassword)}
                  className={styles.eyeIcon}
                >
                  {showPassword ? <FiEyeOff /> : <FiEye />}
                </span>
              </div>
            </div>
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" className={styles.btn}>
            Entrar
          </button>
        </form>
        <p className={styles.footer}>
          Não possui uma conta?{" "}
          <Link to="/signup" className={styles.link}>
            Crie aqui
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
