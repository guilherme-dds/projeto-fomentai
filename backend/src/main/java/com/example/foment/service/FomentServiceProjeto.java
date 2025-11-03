package com.example.foment.service;

import com.example.foment.domain.Projeto;
import com.example.foment.repository.ProjetoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FomentServiceProjeto {

    private final ProjetoRepository projetoRepository;

    public Projeto salvar(Projeto projeto) {
        return projetoRepository.save(projeto);
    }

    public List<Projeto> listarTodos() {
        return projetoRepository.findAll();
    }

    // A ID do projeto é a ID do usuário
    public Projeto buscarPorId(Integer usuarioId) {
        return projetoRepository.findById(usuarioId)
                .orElseThrow(() -> new RuntimeException("Projeto não encontrado"));
    }

    public void deletar(Integer usuarioId) {
        projetoRepository.deleteById(usuarioId);
    }
}