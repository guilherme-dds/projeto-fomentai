package com.example.foment.repository;

import com.example.foment.domain.Datas;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DatasRepository extends JpaRepository<Datas, Integer> {
}