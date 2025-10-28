import { Link } from "react-router-dom";
import styles from "../pages/Home.module.css";
import logo from "../assets/logo.png";

function Home() {
  return (
    <div className={styles.homeContainer}>
      <div className={styles.navContainer}>
        <img src={logo} className={styles.logo} />
        <ul className={styles.navSections}>
          <li>Principais Feiras</li>
          <li>Sec 2</li>
          <li>Sec 3</li>
        </ul>
        <div className={styles.action}>
          <Link to="/login" className={styles.login}>
            Login
          </Link>
          <Link to="/signup" className={styles.signup}>
            Cadastre-se
          </Link>
        </div>
      </div>
      <div className={styles.header}>
        <h1>ENCONTRE OS LUGARES CERTOS</h1>
        <h2>PARA O SEU PROJETO</h2>
      </div>
    </div>
  );
}

export default Home;
