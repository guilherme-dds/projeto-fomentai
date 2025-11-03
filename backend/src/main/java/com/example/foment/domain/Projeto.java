package com.example.foment.domain;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "projeto")
public class Projeto {

    @Id
    @Column(name = "usu_id") // A PK é o próprio usu_id
    private Integer id;

    private String nome;
    private String resumo;
    private String categoria;

    @Column(name = "doc_projeto")
    private String docProjeto;

    // --- RELACIONAMENTOS ---

    @OneToOne
    @MapsId // Mapeia a PK da entidade (id) para a FK (usuario)
    @JoinColumn(name = "usu_id")
    @JsonBackReference("usuario-projeto")
    private User usuario;

    @ManyToOne
    @JoinColumn(name = "feira_id")
    @JsonBackReference("feira-projetos")
    private Feira feira;
}