package com.example.foment.repository;

import com.example.foment.domain.Feira;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FeiraRepository extends JpaRepository<Feira, Integer> {
}