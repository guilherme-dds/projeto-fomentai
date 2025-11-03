package com.example.foment.repository;

import com.example.foment.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Integer> {

    /**
     * Busca um usuário pelo email que está dentro da entidade Contato associada.
     * Exemplo de consulta: "SELECT u FROM User u WHERE u.contato.email = ?1"
     */
    Optional<User> findByContatoEmail(String email);

    // Você pode adicionar outros métodos de consulta personalizados aqui
    // Ex: Optional<User> findByCpf(String cpf);
}