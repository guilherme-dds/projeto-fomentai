package com.example.foment.repository;

import com.example.foment.domain.Projeto;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ProjetoRepository extends JpaRepository<Projeto, Integer> {
    // A chave primária (ID) do Projeto é o ID do Usuário
}