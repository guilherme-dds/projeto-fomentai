import { useState, useEffect } from "react";
import axios from "axios";
import styles from "./Admin.module.css";
import { useRef } from "react";

function Admin() {
  const initialFormState = {
    nome: "",
    vagas: "",
    resumo: "",
    escolaridade: "",
    endereco: {
      logradouro: "",
      numero: "",
      cep: "",
      estado: "",
      complemento: "",
      pais: "Brasil",
    },
    datas: {
      dataInicio: "",
      dataFim: "",
      dataInicioInscricoes: "",
      dataFimInscricoes: "",
      dataClassificacao: "",
      dataPremiacao: "",
    },
    contato: {
      email: "",
      telefone: "",
    },
    organizacao: { nome: "", site: "" },
    url: "",
    edital: "",
    tema: "",
    modalidade: "Presencial",
    categoria: "",
    idade: "",
    premiacao: {
      colocacao: "",
      valor: "",
      tipo: "",
      quantidade: "",
      datas: {
        id: null,
      },
    },
  };
  const [formData, setFormData] = useState(initialFormState);

  const [fairs, setFairs] = useState([]);
  const [editingFairId, setEditingFairId] = useState(null);
  const formRef = useRef(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleEnderecoChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      endereco: { ...prev.endereco, [name]: value },
    }));
  };

  const handleDatasChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      datas: { ...prev.datas, [name]: value },
    }));
  };

  const handleContatoChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      contato: { ...prev.contato, [name]: value },
    }));
  };

  const handleOrganizacaoChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      organizacao: {
        ...prev.organizacao,
        [name]: value,
      },
    }));
  };
  const handlePremiacaoChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      premiacao: {
        ...prev.premiacao,
        [name]: value,
      },
    }));
  };

  const fetchFairs = async () => {
    try {
      const response = await axios.get("http://localhost:8080/foment/feiras");
      setFairs(response.data);
      console.log("Feiras carregadas:", response.data);
    } catch (error) {
      console.error("Erro ao buscar feiras:", error);
    }
  };

  useEffect(() => {
    fetchFairs();
  }, []);

  const formatDateForInput = (dateString) => {
    if (!dateString) return "";
    try {
      const date = new Date(dateString);
      return date.toISOString().split("T")[0];
    } catch (error) {
      return dateString;
    }
  };

  const handleEdit = (fair) => {
    setEditingFairId(fair.id);
    const formattedDatas = { ...initialFormState.datas };
    for (const key in fair.datas) {
      formattedDatas[key] = formatDateForInput(fair.datas[key]);
    }
    setFormData({
      ...initialFormState,
      ...fair,
      datas: formattedDatas,
    });
    formRef.current.scrollIntoView({ behavior: "smooth" });
  };

  const handleDelete = async (fairId) => {
    if (window.confirm("Tem certeza que deseja excluir esta feira?")) {
      try {
        await axios.delete(`http://localhost:8080/foment/feiras/${fairId}`);
        alert("Feira excluída com sucesso!");
        fetchFairs();
      } catch (error) {
        console.error("Erro ao excluir feira:", error);
        alert("Ocorreu um erro ao excluir a feira.");
      }
    }
  };

  const cancelEdit = () => {
    setEditingFairId(null);
    setFormData(initialFormState);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const payload = {
        nome: formData.nome,
        vagas: formData.vagas ? parseInt(formData.vagas, 10) : null,
        resumo: formData.resumo,
        escolaridade: formData.escolaridade,
        url: formData.url,
        edital: formData.edital,
        tema: formData.tema,
        modalidade: formData.modalidade,
        categoria: formData.categoria,
        idade: formData.idade ? parseInt(formData.idade, 10) : null,
        endereco: {
          ...formData.endereco,
          numero: formData.endereco.numero
            ? parseInt(formData.endereco.numero, 10)
            : null,
          cep: formData.endereco.cep
            ? parseInt(formData.endereco.cep, 10)
            : null,
        },
        datas: formData.datas,
        contato: formData.contato,
        organizacao: formData.organizacao,
        premiacao: {
          ...formData.premiacao,
          valor: formData.premiacao.valor
            ? parseFloat(formData.premiacao.valor)
            : null,
          quantidade: formData.premiacao.quantidade
            ? parseInt(formData.premiacao.quantidade, 10)
            : null,
        },
      };

      if (editingFairId) {
        await axios.put(
          `http://localhost:8080/foment/feiras/${editingFairId}`,
          payload
        );
        alert("Feira atualizada com sucesso!");
      } else {
        await axios.post("http://localhost:8080/foment/feiras", payload);
        alert("Feira cadastrada com sucesso!");
      }

      cancelEdit();
      fetchFairs();
    } catch (error) {
      console.error(
        "Erro no processo de cadastro:",
        error.response?.data || error.message
      );
      const action = editingFairId ? "atualizar" : "cadastrar";
      alert(`Ocorreu um erro ao ${action} a feira. Verifique o console.`);
    }
  };

  return (
    <div className={styles.adminContainer}>
      <div className={styles.panel} ref={formRef}>
        <div className={styles.header}>
          <h1 className={styles.title}>
            {editingFairId ? "Editando Feira" : "Cadastro de Feiras"}
          </h1>
        </div>
        <form onSubmit={handleSubmit} className={styles.form}>
          <fieldset className={styles.formSection}>
            <legend>Informações Gerais</legend>
            <div className={styles.formGrid}>
              <input
                name="nome"
                value={formData.nome}
                onChange={handleChange}
                placeholder="Nome da Feira"
                required
              />
              <input
                name="vagas"
                type="number"
                value={formData.vagas}
                onChange={handleChange}
                placeholder="Vagas"
              />
              <input
                name="escolaridade"
                value={formData.escolaridade}
                onChange={handleChange}
                placeholder="Escolaridade"
              />
              <input
                name="url"
                type="url"
                value={formData.url}
                onChange={handleChange}
                placeholder="URL da Feira"
              />
              <input
                name="edital"
                value={formData.edital}
                onChange={handleChange}
                placeholder="Edital (arquivo)"
              />
              <input
                name="tema"
                value={formData.tema}
                onChange={handleChange}
                placeholder="Tema"
              />
              <select
                name="modalidade"
                value={formData.modalidade}
                onChange={handleChange}
              >
                <option value="Presencial">Presencial</option>
                <option value="Online">Online</option>
                <option value="Híbrido">Híbrido</option>
              </select>
              <input
                name="categoria"
                value={formData.categoria}
                onChange={handleChange}
                placeholder="Categoria"
              />
              <input
                name="idade"
                type="number"
                value={formData.idade}
                onChange={handleChange}
                placeholder="Idade Mínima"
              />
            </div>
            <textarea
              name="resumo"
              value={formData.resumo}
              onChange={handleChange}
              placeholder="Resumo da feira..."
              className={styles.resumo}
            />
          </fieldset>

          <fieldset className={styles.formSection}>
            <legend>Endereço da Organização</legend>
            <div className={styles.formGrid}>
              <input
                name="logradouro"
                value={formData.endereco.logradouro}
                onChange={handleEnderecoChange}
                placeholder="Logradouro (Rua, Av.)"
                required
              />
              <input
                name="numero"
                type="number"
                value={formData.endereco.numero}
                onChange={handleEnderecoChange}
                placeholder="Número"
                required
              />
              <input
                name="cep"
                type="number"
                value={formData.endereco.cep}
                onChange={handleEnderecoChange}
                placeholder="CEP"
                required
              />
              <input
                name="estado"
                value={formData.endereco.estado}
                onChange={handleEnderecoChange}
                placeholder="Estado (Ex: SP)"
                required
              />
              <input
                name="complemento"
                value={formData.endereco.complemento}
                onChange={handleEnderecoChange}
                placeholder="Complemento"
              />
              <input
                name="pais"
                value={formData.endereco.pais}
                onChange={handleEnderecoChange}
                placeholder="País"
                required
              />
            </div>
          </fieldset>

          <fieldset className={styles.formSection}>
            <legend>Datas da Feira</legend>
            <div className={styles.formGrid}>
              <div className={styles.formField}>
                <label htmlFor="dataInicio">Início da Feira</label>
                <input
                  id="dataInicio"
                  name="dataInicio"
                  type="date"
                  value={formData.datas.dataInicio}
                  onChange={handleDatasChange}
                  required
                />
              </div>
              <div className={styles.formField}>
                <label htmlFor="dataFim">Fim da Feira</label>
                <input
                  id="dataFim"
                  name="dataFim"
                  type="date"
                  value={formData.datas.dataFim}
                  onChange={handleDatasChange}
                  required
                />
              </div>
              <div className={styles.formField}>
                <label htmlFor="dataInicioInscricoes">
                  Início das Inscrições
                </label>
                <input
                  id="dataInicioInscricoes"
                  name="dataInicioInscricoes"
                  type="date"
                  value={formData.datas.dataInicioInscricoes}
                  onChange={handleDatasChange}
                  required
                />
              </div>
              <div className={styles.formField}>
                <label htmlFor="dataFimInscricoes">Fim das Inscrições</label>
                <input
                  id="dataFimInscricoes"
                  name="dataFimInscricoes"
                  type="date"
                  value={formData.datas.dataFimInscricoes}
                  onChange={handleDatasChange}
                  required
                />
              </div>
              <div className={styles.formField}>
                <label htmlFor="dataClassificacao">Data de Classificação</label>
                <input
                  id="dataClassificacao"
                  name="dataClassificacao"
                  type="date"
                  value={formData.datas.dataClassificacao}
                  onChange={handleDatasChange}
                />
              </div>
              <div className={styles.formField}>
                <label htmlFor="dataPremiacao">Data da Premiação</label>
                <input
                  id="dataPremiacao"
                  name="dataPremiacao"
                  type="date"
                  value={formData.datas.dataPremiacao}
                  onChange={handleDatasChange}
                />
              </div>
            </div>
          </fieldset>

          <fieldset className={styles.formSection}>
            <legend>Contato</legend>
            <div className={styles.formGrid}>
              <input
                name="email"
                type="email"
                value={formData.contato.email}
                onChange={handleContatoChange}
                placeholder="Email de Contato"
                required
              />
              <input
                name="telefone"
                value={formData.contato.telefone}
                onChange={handleContatoChange}
                placeholder="Telefone de Contato"
              />
            </div>
          </fieldset>

          <fieldset className={styles.formSection}>
            <legend>Organização</legend>
            <div className={styles.formGrid}>
              <input
                name="nome"
                value={formData.organizacao.nome}
                onChange={handleOrganizacaoChange}
                placeholder="Nome da Organização"
                required
              />
              <input
                name="site"
                type="url"
                value={formData.organizacao.site}
                onChange={handleOrganizacaoChange}
                placeholder="Site da Organização"
              />
            </div>
          </fieldset>

          <fieldset className={styles.formSection}>
            <legend>Premiação</legend>
            <div className={styles.formGrid}>
              <input
                name="colocacao"
                value={formData.premiacao.colocacao}
                onChange={handlePremiacaoChange}
                placeholder="Colocação (Ex: 1º Lugar)"
              />
              <input
                name="valor"
                type="number"
                value={formData.premiacao.valor}
                onChange={handlePremiacaoChange}
                placeholder="Valor do Prêmio"
              />
              <input
                name="tipo"
                value={formData.premiacao.tipo}
                onChange={handlePremiacaoChange}
                placeholder="Tipo (Ex: Dinheiro)"
              />
              <input
                name="quantidade"
                type="number"
                value={formData.premiacao.quantidade}
                onChange={handlePremiacaoChange}
                placeholder="Quantidade"
              />
            </div>
          </fieldset>

          <div className={styles.formActions}>
            <button type="submit" className={styles.submitButton}>
              {editingFairId ? "Salvar Alterações" : "Cadastrar Feira"}
            </button>
            {editingFairId && (
              <button type="button" onClick={cancelEdit} className={styles.cancelButton}>
                Cancelar Edição
              </button>
            )}
          </div>
        </form>

        <div className={styles.fairsListContainer}>
          <h2 className={styles.fairsListTitle}>Feiras Cadastradas</h2>
          <div className={styles.fairsList}>
            {fairs.length > 0 ? (
              fairs.map((fair) => (
                <div key={fair.id} className={styles.fairItem}>
                  <h3 className={styles.fairItemTitle}>{fair.nome}</h3>
                  <p>
                    <strong>Modalidade:</strong> {fair.modalidade}
                  </p>
                  <p>
                    <strong>Local:</strong>{" "}
                    {fair.endereco?.estado || "Não informado"}
                  </p>
                  <div className={styles.fairActions}>
                    <button
                      onClick={() => handleEdit(fair)}
                      className={styles.editButton}
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleDelete(fair.id)}
                      className={styles.deleteButton}
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <p>Nenhuma feira cadastrada ainda.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Admin;
