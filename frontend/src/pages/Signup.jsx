import styles from "../pages/Signup.module.css";
import { Link } from "react-router-dom";
import { useState } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";

function Signup() {
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
          <div className={styles.line}>
            <div>
              <label>Nome</label>
              <input type="text" placeholder="Seu nome" />
            </div>
            <div>
              <label>Número</label>
              <input type="tel" placeholder="(00) 00000-0000" />
            </div>
          </div>
          <div className={styles.line}>
            <div>
              <label>Campo de estudo</label>
              <input type="text" placeholder="Ex: Tecnologia" />
            </div>
            <div>
              <label>Data de nascimento</label>
              <input type="date" />
            </div>
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
        {/* prettier-ignore */}
        <p className={styles.footer}>
          Já possui uma conta?{" "}
          <Link to="/login" className={styles.link}>Entre aqui</Link>
        </p>
      </div>
    </div>
  );
}
export default Signup;
