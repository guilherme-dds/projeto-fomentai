package com.example.foment.service;

import com.example.foment.domain.Instituicao;
import com.example.foment.repository.InstituicaoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FomentServiceInstituicao {

    private final InstituicaoRepository instituicaoRepository;

    public Instituicao salvar(Instituicao instituicao) {
        return instituicaoRepository.save(instituicao);
    }

    public List<Instituicao> listarTodos() {
        return instituicaoRepository.findAll();
    }

    public Instituicao buscarPorId(Integer id) {
        return instituicaoRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Instituição não encontrada"));
    }

    public void deletar(Integer id) {
        instituicaoRepository.deleteById(id);
    }
}