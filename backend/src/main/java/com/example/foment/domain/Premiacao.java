package com.example.foment.domain;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "Premiacao")
public class Premiacao {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "prem_id")
    private Integer id;

    private String colocacao;
    private Integer valor;
    private String tipo;
    private Integer quantidade;

    @OneToOne(mappedBy = "premiacao")
    @JsonBackReference // Evita loop com Feira
    private Feira feira;

    @ManyToOne
    @JoinColumn(name = "data_id")
    private Datas datas;
}