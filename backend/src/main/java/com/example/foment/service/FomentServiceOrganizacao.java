package com.example.foment.service;

import com.example.foment.domain.Organizacao;
import com.example.foment.repository.OrganizacaoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FomentServiceOrganizacao {

    private final OrganizacaoRepository organizacaoRepository;

    public Organizacao salvar(Organizacao organizacao) {
        return organizacaoRepository.save(organizacao);
    }

    public List<Organizacao> listarTodos() {
        return organizacaoRepository.findAll();
    }

    public Organizacao buscarPorId(Integer id) {
        return organizacaoRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Organização não encontrada"));
    }

    public void deletar(Integer id) {
        organizacaoRepository.deleteById(id);
    }
}