package com.example.foment.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "Contato")
public class Contato {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "contato_id")
    private Integer id;

    private String telefone;

    @Column(unique = true) // O email deve ser único
    private String email;

    @OneToOne(cascade = CascadeType.ALL) // <- ADICIONADO CascadeType.ALL
    @JoinColumn(name = "end_id", referencedColumnName = "end_id")
    private Endereco endereco;

}