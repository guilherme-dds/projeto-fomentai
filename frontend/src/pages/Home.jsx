import background from "../assets/background.png";
import { Link } from "react-router-dom";
import styles from "../pages/Home.module.css";

function Home() {
  return (
    <div>
      <div className={styles.background}>
        <img src={background} alt="" />
      </div>
      <div className={styles.navBackground}>
        <div className={styles.nav}>
          <div className={styles.action}>
            <Link to="/login" className={styles.login}>
              Login
            </Link>
            <Link to="/signup" className={styles.signup}>
              Cadastre-se
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
