package com.example.foment.service;

import com.example.foment.domain.Contato;
import com.example.foment.repository.ContatoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FomentServiceContato {

    private final ContatoRepository contatoRepository;

    public Contato salvar(Contato contato) {
        return contatoRepository.save(contato);
    }

    public List<Contato> listarTodos() {
        return contatoRepository.findAll();
    }

    public Contato buscarPorId(Integer id) {
        return contatoRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Contato não encontrado"));
    }

    public void deletar(Integer id) {
        contatoRepository.deleteById(id);
    }
}