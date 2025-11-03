package com.example.foment.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "instituicao")
public class Instituicao {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "inst_id")
    private Integer id;

    @Column(name = "grau_escolaridade")
    private String grauEscolaridade;

    private String nome;

    @ManyToOne
    @JoinColumn(name = "end_id")
    private Endereco endereco;

    @ManyToOne
    @JoinColumn(name = "contato_id")
    private Contato contato;
}