package com.example.foment.repository;

import com.example.foment.domain.Premiacao;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PremiacaoRepository extends JpaRepository<Premiacao, Integer> {
}