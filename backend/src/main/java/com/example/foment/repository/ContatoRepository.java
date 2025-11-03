package com.example.foment.repository;

import com.example.foment.domain.Contato;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ContatoRepository extends JpaRepository<Contato, Integer> {

    // Busca um contato pelo email
    Optional<Contato> findByEmail(String email);

    // Busca um contato pelo telefone
    Optional<Contato> findByTelefone(String telefone);

    // Verifica se existe contato com determinado email
    boolean existsByEmail(String email);
}
