package com.example.foment.service;

import com.example.foment.domain.Premiacao;
import com.example.foment.repository.PremiacaoRepository;
import lombok.RequiredArgsConstructor; // Adicionado para consistência
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor // Substitui o construtor manual
public class FomentServicePremiacao {

    private final PremiacaoRepository premiacaoRepository;

    /* O construtor manual abaixo não é mais necessário devido ao @RequiredArgsConstructor
    public FomentServicePremiacao(PremiacaoRepository premiacaoRepository) {
        this.premiacaoRepository = premiacaoRepository;
    }
    */

    // Criar ou atualizar premiação
    public Premiacao salvar(Premiacao premiacao) {
        // Esta lógica está correta.
        // Para atualizar, o objeto 'premiacao' deve vir com o 'prem_id'.
        // Para criar, deve vir sem o 'prem_id'.
        return premiacaoRepository.save(premiacao);
    }

    // Buscar todas as premiações
    public List<Premiacao> listarTodas() {
        return premiacaoRepository.findAll();
    }

    // Buscar premiação por ID
    public Optional<Premiacao> buscarPorId(Integer id) {
        return premiacaoRepository.findById(id);
    }

    // Deletar premiação por ID
    public void deletar(Integer id) {
        // Antes de deletar, você pode precisar verificar
        // se a premiação está sendo usada por uma Feira para evitar erros.
        // Mas a operação em si está correta.
        premiacaoRepository.deleteById(id);
    }
}