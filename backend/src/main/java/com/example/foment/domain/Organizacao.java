package com.example.foment.domain;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "Organizacao")
public class Organizacao {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "organizacao_id")
    private Integer id;

    private String nome;
    private String site;

    @ManyToOne
    @JoinColumn(name = "end_id")
    private Endereco endereco;

    @ManyToOne
    @JoinColumn(name = "feir_id")
    @JsonBackReference("feira-organizacao")
    private Feira feira;
}