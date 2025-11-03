package com.example.foment.service;

import com.example.foment.domain.Datas;
import com.example.foment.repository.DatasRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FomentServiceDatas {

    private final DatasRepository datasRepository;

    public Datas salvar(Datas datas) {
        return datasRepository.save(datas);
    }

    public List<Datas> listarTodos() {
        return datasRepository.findAll();
    }

    public Datas buscarPorId(Integer id) {
        return datasRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Conjunto de datas não encontrado"));
    }

    public void deletar(Integer id) {
        datasRepository.deleteById(id);
    }
}