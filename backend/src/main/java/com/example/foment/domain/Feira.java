package com.example.foment.domain;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Entity
@Getter
@Setter
@Table(name = "Feira")
public class Feira {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "feir_id")
    private Integer id;

    private Integer vagas;

    @Column(columnDefinition = "TEXT")
    private String resumo;

    private String escolaridade;
    private String url;
    private String documentacao;
    private String edital;
    private String tema;
    private String nome;
    private String modalidade;
    private String categoria;
    private Integer idade;

    // --- RELACIONAMENTOS ---

    // Relacionamento 1 com User: O usuário ORGANIZADOR desta feira
    // (Baseado na FK 'usu_id' na tabela 'Feira')
    @ManyToOne
    @JoinColumn(name = "usu_id")
    @JsonBackReference("organizador-feiras") // Referência de volta
    private User organizador;

    // Relacionamento 2 com User: Os usuários PARTICIPANTES desta feira
    // (Baseado na FK 'feir_id' na tabela 'Usuario')
    @OneToMany(mappedBy = "feiraInscrita")
    @JsonIgnore
    private List<User> participantes;

    @ManyToOne
    @JoinColumn(name = "end_id")
    private Endereco endereco;

    @ManyToOne
    @JoinColumn(name = "data_id")
    private Datas datas;

    @ManyToOne
    @JoinColumn(name = "contato_id")
    private Contato contato;

    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "prem_id", referencedColumnName = "prem_id")
    private Premiacao premiacao;

    @OneToMany(mappedBy = "feira", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference("feira-organizacao")
    private List<Organizacao> organizacoes;

    @OneToMany(mappedBy = "feira", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference("feira-projetos")
    private List<Projeto> projetos;
}