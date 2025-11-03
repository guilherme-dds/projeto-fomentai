package com.example.foment.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.sql.Date;

@Entity
@Getter
@Setter
@Table(name = "datas")
public class Datas {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "data_id")
    private Integer id;

    @Column(name = "data_premiacao")
    private Date dataPremiacao;

    @Column(name = "data_inicio")
    private Date dataInicio;

    @Column(name = "data_fim")
    private Date dataFim;

    @Column(name = "data_inicio_inscricoes")
    private Date dataInicioInscricoes;

    @Column(name = "data_fim_incricoes") // Corrigido (no seu SQL estava 'incricoes')
    private Date dataFimInscricoes;

    @Column(name = "data_classificacao")
    private Date dataClassificacao;
}