package com.example.foment.service;

import com.example.foment.domain.*;
import com.example.foment.repository.FeiraRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FomentServiceFeira {

    private final FeiraRepository feiraRepository;

    public Feira cadastrarFeira(Feira feira) {
        // Inicializa objetos aninhados para evitar NullPointerException
        // se eles não forem 'owned' (CascadeType.ALL), esta lógica
        // precisaria ser trocada para buscar os IDs com outros repositórios.
        if (feira.getEndereco() == null) {
            feira.setEndereco(new Endereco());
        }
        if (feira.getContato() == null) {
            feira.setContato(new Contato());
        }
        if (feira.getDatas() == null) {
            feira.setDatas(new Datas());
        }
        if (feira.getPremiacao() == null) {
            feira.setPremiacao(new Premiacao());
        }
        return feiraRepository.save(feira);
    }

    public Feira editarFeira(Feira feiraAtualizada) {
        Feira feiraExistente = feiraRepository.findById(feiraAtualizada.getId())
                .orElseThrow(() -> new RuntimeException("Feira não encontrada"));

        // Atualiza campos simples
        feiraExistente.setNome(feiraAtualizada.getNome());
        feiraExistente.setVagas(feiraAtualizada.getVagas());
        feiraExistente.setResumo(feiraAtualizada.getResumo());
        feiraExistente.setEscolaridade(feiraAtualizada.getEscolaridade());
        feiraExistente.setUrl(feiraAtualizada.getUrl());
        feiraExistente.setDocumentacao(feiraAtualizada.getDocumentacao());
        feiraExistente.setEdital(feiraAtualizada.getEdital());
        feiraExistente.setTema(feiraAtualizada.getTema());
        feiraExistente.setModalidade(feiraAtualizada.getModalidade());
        feiraExistente.setCategoria(feiraAtualizada.getCategoria());
        feiraExistente.setIdade(feiraAtualizada.getIdade());

        // Atualiza referências (FKs para entidades que não são 'owned')
        // Estas entidades devem existir no banco
        if (feiraAtualizada.getOrganizador() != null) {
            // Assumindo que o ID do organizador é enviado
            feiraExistente.setOrganizador(feiraAtualizada.getOrganizador());
        }

        // Atualiza objetos aninhados (assumindo CascadeType.ALL)
        atualizarEnderecoFeira(feiraExistente, feiraAtualizada.getEndereco());
        atualizarContatoFeira(feiraExistente, feiraAtualizada.getContato());
        atualizarDatasFeira(feiraExistente, feiraAtualizada.getDatas());
        atualizarPremiacaoFeira(feiraExistente, feiraAtualizada.getPremiacao());

        // Gerenciamento de listas (Organizacoes, Projetos, Participantes)
        // pode ser adicionado aqui se necessário (ex: feiraExistente.getProjetos().clear(); feiraExistente.getProjetos().addAll(...))

        return feiraRepository.save(feiraExistente);
    }

    public void deletarFeira(Integer id) {
        feiraRepository.deleteById(id);
    }

    public List<Feira> buscarFeiras() {
        return feiraRepository.findAll();
    }

    public Feira buscarFeiraPorId(Integer id) {
        return feiraRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Feira não encontrada"));
    }

    // --- MÉTODOS HELPER PRIVADOS ---

    private void atualizarEnderecoFeira(Feira feiraExistente, Endereco enderecoAtualizado) {
        if (enderecoAtualizado != null) {
            Endereco enderecoExistente = feiraExistente.getEndereco();
            if (enderecoExistente == null) {
                enderecoExistente = new Endereco();
                feiraExistente.setEndereco(enderecoExistente);
            }
            enderecoExistente.setEstado(enderecoAtualizado.getEstado());
            enderecoExistente.setNumero(enderecoAtualizado.getNumero());
            enderecoExistente.setCep(enderecoAtualizado.getCep());
            enderecoExistente.setLogradouro(enderecoAtualizado.getLogradouro());
            enderecoExistente.setComplemento(enderecoAtualizado.getComplemento());
            enderecoExistente.setPais(enderecoAtualizado.getPais());
        }
    }

    private void atualizarContatoFeira(Feira feiraExistente, Contato contatoAtualizado) {
        if (contatoAtualizado != null) {
            Contato contatoExistente = feiraExistente.getContato();
            if (contatoExistente == null) {
                contatoExistente = new Contato();
                feiraExistente.setContato(contatoExistente);
            }
            contatoExistente.setTelefone(contatoAtualizado.getTelefone());
            contatoExistente.setEmail(contatoAtualizado.getEmail());
            // Se o Contato da Feira também tiver um Endereço aninhado,
            // um método helper para ele seria chamado aqui.
        }
    }

    private void atualizarDatasFeira(Feira feiraExistente, Datas datasAtualizadas) {
        if (datasAtualizadas != null) {
            Datas datasExistente = feiraExistente.getDatas();
            if (datasExistente == null) {
                datasExistente = new Datas();
                feiraExistente.setDatas(datasExistente);
            }
            datasExistente.setDataInicio(datasAtualizadas.getDataInicio());
            datasExistente.setDataFim(datasAtualizadas.getDataFim());
            datasExistente.setDataInicioInscricoes(datasAtualizadas.getDataInicioInscricoes());
            datasExistente.setDataFimInscricoes(datasAtualizadas.getDataFimInscricoes());
            datasExistente.setDataClassificacao(datasAtualizadas.getDataClassificacao());
            datasExistente.setDataPremiacao(datasAtualizadas.getDataPremiacao());
        }
    }

    private void atualizarPremiacaoFeira(Feira feiraExistente, Premiacao premiacaoAtualizada) {
        if (premiacaoAtualizada != null) {
            Premiacao premiacaoExistente = feiraExistente.getPremiacao();
            if (premiacaoExistente == null) {
                premiacaoExistente = new Premiacao();
                feiraExistente.setPremiacao(premiacaoExistente);
            }
            premiacaoExistente.setColocacao(premiacaoAtualizada.getColocacao());
            premiacaoExistente.setValor(premiacaoAtualizada.getValor());
            premiacaoExistente.setTipo(premiacaoAtualizada.getTipo());
            premiacaoExistente.setQuantidade(premiacaoAtualizada.getQuantidade());
            // Atualiza a data da premiação, se ela for 'owned' pela premiação
            if (premiacaoAtualizada.getDatas() != null) {
                // Lógica para atualizar a data da premiação (se aplicável)
            }
        }
    }
}