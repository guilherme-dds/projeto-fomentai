import styles from "../pages/Login.module.css";
import { Link } from "react-router-dom";
import { useState } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";

function Login() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className={styles.background}>
      <div className={styles.container}>
        <h1 className={styles.title}>
          Bem-vindo ao{" "}
          <span>
            FOMENT<span className={styles.ai}>.AI</span>
          </span>
        </h1>
        <div className={styles.inputs}>
          <div className={styles.email}>
            <label>Email</label>
            <input type="email" placeholder="Endereço de EMAIL" />
          </div>
          <div className={styles.password}>
            <label>Crie sua senha</label>
            <div className={styles.passwordWrapper}>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Senha"
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
        <button className={styles.btn}>Cadastrar-se</button>
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
