package com.example.foment.domain;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.sql.Date;
import java.util.List;

@Entity
@Getter
@Setter
@Table(name = "usuario")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "usu_id")
    private Integer id;

    @Column(name = "nome")
    private String nome;

    // O CAMPO EMAIL FOI REMOVIDO DAQUI
    // Ele deve ser acessado via 'contato.email'
    // @Column(unique = true, nullable = false)
    // private String email;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String senha;

    @Column(name = "token_senha", columnDefinition = "TEXT")
    private String tokenSenha;

    @Column(name = "foto_perfil")
    private String fotoPerfil;

    @Column(name = "tus_code")
    private Integer tusCode;

    @Column(name = "data_nascimento")
    private Date dataNascimento;

    @Column(name = "ativo")
    private Boolean ativo = true;

    @Column(name = "CPF", unique = true, length = 14) // O nome da coluna no DB era 'CPF'
    private String cpf;

    @Column(name = "campo_de_estudo")
    private String campoDeEstudo;

    @Column(name = "data_criacao")
    private Date dataCriacao;

    // --- RELACIONAMENTOS ---

    // RELACIONAMENTO COM CONTATO
    @OneToOne(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinColumn(name = "contato_id", referencedColumnName = "contato_id")
    private Contato contato;

    // Relacionamento com Endereco (FK: end_id)
    @ManyToOne(cascade = CascadeType.ALL) // <- adiciona CascadeType.ALL
    @JoinColumn(name = "end_id")
    private Endereco endereco;


    // Relacionamento com Instituicao (FK: inst_id)
    @ManyToOne
    @JoinColumn(name = "inst_id")
    private Instituicao instituicao;

    // Relacionamento 1 com Feira: A feira que este usuário ESTÁ INSCRITO
    // (Baseado na FK 'feir_id' na tabela 'Usuario')
    @ManyToOne
    @JoinColumn(name = "feir_id")
    @JsonBackReference("feira-participantes") // Referência de volta
    private Feira feiraInscrita;

    // Relacionamento 2 com Feira: As feiras que este usuário ORGANIZA
    // (Baseado na FK 'usu_id' na tabela 'Feira')
    @OneToMany(mappedBy = "organizador", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference("organizador-feiras") // Referência principal
    private List<Feira> feirasOrganizadas;

    // Relacionamento com Projeto
    @OneToOne(mappedBy = "usuario", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference("usuario-projeto")
    private Projeto projeto;
}