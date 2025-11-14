import { useState } from "react";
import { useLocation, Link } from "react-router-dom";
import { ExternalLink, Menu, X } from "lucide-react";
import styles from "./Resultados.module.css";
import logo from "../assets/logo.png";
import placeholder from "../assets/placeholder.png";

function Resultados() {
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const analysisResults = location.state?.results || [];

  return (
    <div className={styles.resultsContainer}>
      <div className={styles.navContainer}>
        <Link to="/">
          <img src={logo} className={styles.logo} alt="FomentAI Logo" />
        </Link>

        <div
          className={`${styles.navMenu} ${
            isMenuOpen ? styles.navMenuOpen : ""
          }`}
        >
          <ul className={styles.navSections}></ul>
          <div className={styles.action}>
            <Link to="/login" className={styles.login}>
              Login
            </Link>
            <Link to="/signup" className={styles.signup}>
              Cadastre-se
            </Link>
          </div>
        </div>
        <div
          className={styles.menuBtn}
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <X size={30} /> : <Menu size={30} />}
        </div>
      </div>

      <div className={styles.header}>
        <h1>RESULTADOS DA ANÁLISE</h1>
        <p>Estas são as feiras que mais combinam com o seu projeto.</p>
      </div>

      <div className={styles.content}>
        {analysisResults.length > 0 ? (
          <div className={styles.fairsList}>
            {analysisResults.map((fair, index) => (
              <div className={styles.fairsContent} key={index}>
                <img src={placeholder} alt="Imagem da feira" />
                <div className={styles.fairsInfo}>
                  <div className={styles.fairsAction}>
                    <span className={styles.fairName}>{fair.nome_feira}</span>
                    <p className={styles.justification}>{fair.justificativa}</p>
                    <a
                      href={fair.url_feira}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.saibaMaisBtn}
                    >
                      SAIBA MAIS <ExternalLink size={16} />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className={styles.noResults}>
            <h2>Nenhuma feira compatível foi encontrada.</h2>
            <p>
              Tente refinar a descrição do seu projeto para obter melhores
              resultados.
            </p>
            <Link to="/" className={styles.backButton}>
              Voltar para a Home
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default Resultados;
