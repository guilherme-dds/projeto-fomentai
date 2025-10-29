import { useState } from "react";
import { Upload } from "lucide-react";
import { Link } from "react-router-dom";
import styles from "./Home.module.css";
import logo from "../assets/logo.png";

function Home() {
  const [fileName, setFileName] = useState(null);
  const [text, setText] = useState("");
  const maxLength = 2000;

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
    } else {
      setFileName(null);
    }
  };

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
        <p>
          Descubra, em poucos segundos, quais feiras combinam com o seu <br />{" "}
          projeto e aumente suas chances de <span>sucesso</span> e{" "}
          <span>reconhecimento</span>.
        </p>
      </div>
      <div className={styles.content}>
        <div className={styles.textArea}>
          <textarea
            value={text}
            maxLength={maxLength}
            onChange={(e) => setText(e.target.value)}
            placeholder="Descreva o seu projeto aqui"
            className={styles.projectDescription}
          />
        </div>
        <div className={styles.contentInfo}>
          <p className={styles.fileNameDisplay}>
            {fileName && <span>{fileName}</span>}
          </p>
          <span className={styles.couter}>
            {text.length}/{maxLength}
          </span>
        </div>
        <div className={styles.btnContent}>
          <div className={styles.uploadContainer}>
            <label htmlFor="pdf-upload" className={styles.uploadLabel}>
              <Upload size={20} />
              <span>UPLOAD</span>
            </label>
            <input
              id="pdf-upload"
              type="file"
              accept=".pdf"
              className={styles.hiddenInput}
              onChange={handleFileChange}
            />
          </div>
          <button className={styles.btnFind}>
            ENCONTRE AS MELHORES FEIRAS
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
