package com.example.foment.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "endereco")
public class Endereco {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "end_id")
    private Integer id;

    private String estado;
    private Integer numero;
    private Integer cep;
    private String logradouro;
    private String complemento;
    private String pais;
}