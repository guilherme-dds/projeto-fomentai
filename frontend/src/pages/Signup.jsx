import styles from "../pages/Signup.module.css";
import { Link } from "react-router-dom";
import { useState } from "react";
import axios from "axios";
import { FiEye, FiEyeOff } from "react-icons/fi";

function Signup() {
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    nome: "",
    telefone: "",
    campoDeEstudo: "",
    dataNascimento: "",
    senha: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const userData = {
      nome: formData.nome,
      senha: formData.senha,
      dataNascimento: formData.dataNascimento || null,
      campoDeEstudo: formData.campoDeEstudo || null,
      contato: {
        email: formData.email,
        telefone: formData.telefone || null,
      },
      tokenSenha: null,
      fotoPerfil: null,
      tusCode: null,
      ativo: true,
      cpf: null,
      dataCriacao: new Date().toISOString().split("T")[0],
      endereco: null,
    };

    try {
      const response = await axios.post(
        "http://localhost:8080/foment/usuarios",
        userData
      );
      console.log("Usuário cadastrado com sucesso:", response.data);
      alert("Cadastro realizado com sucesso!");
    } catch (error) {
      console.error(
        "Erro ao cadastrar usuário:",
        error.response?.data || error.message
      );
      alert(
        "Erro ao realizar o cadastro. Verifique o console para mais detalhes."
      );
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
                name="email"
                placeholder="Endereço de EMAIL"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className={styles.line}>
              <div>
                <label>Nome</label>
                <input
                  type="text"
                  name="nome"
                  placeholder="Seu nome"
                  value={formData.nome}
                  onChange={handleChange}
                  required
                />
              </div>
              <div>
                <label>Número</label>
                <input
                  type="tel"
                  name="telefone"
                  placeholder="(00) 00000-0000"
                  value={formData.telefone}
                  onChange={handleChange}
                />
              </div>
            </div>
            <div className={styles.line}>
              <div>
                <label>Campo de estudo</label>
                <input
                  type="text"
                  name="campoDeEstudo"
                  placeholder="Ex: Tecnologia"
                  value={formData.campoDeEstudo}
                  onChange={handleChange}
                />
              </div>
              <div>
                <label>Data de nascimento</label>
                <input
                  type="date"
                  name="dataNascimento"
                  value={formData.dataNascimento}
                  onChange={handleChange}
                />
              </div>
            </div>
            <div className={styles.password}>
              <label>Crie sua senha</label>
              <div className={styles.passwordWrapper}>
                <input
                  type={showPassword ? "text" : "password"}
                  name="senha"
                  placeholder="Senha"
                  value={formData.senha}
                  onChange={handleChange}
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
          <button type="submit" className={styles.btn}>
            Cadastrar-se
          </button>
        </form>
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
