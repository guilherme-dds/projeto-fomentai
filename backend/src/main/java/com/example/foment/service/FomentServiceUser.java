package com.example.foment.service;

import com.example.foment.domain.Contato;
import com.example.foment.domain.Endereco;
import com.example.foment.domain.User;
import com.example.foment.repository.ContatoRepository;
import com.example.foment.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FomentServiceUser {

    private final UserRepository userRepository;
    private final ContatoRepository contatoRepository;
    private final BCryptPasswordEncoder encoder;


    public User cadastrarUsuario(User usuario) {

        // Criptografa a senha ANTES de salvar
        if (usuario.getSenha() != null) {
            usuario.setSenha(encoder.encode(usuario.getSenha()));
        }

        // --- ENDEREÇO PRINCIPAL ---
        if (usuario.getEndereco() == null) {
            usuario.setEndereco(new Endereco());
        }

        // --- CONTATO ---
        if (usuario.getContato() == null) {
            usuario.setContato(new Contato());
        } else if (usuario.getContato().getId() != null) {
            Contato contatoGerenciado = contatoRepository.findById(usuario.getContato().getId())
                    .orElseThrow(() -> new RuntimeException("Contato não encontrado"));
            usuario.setContato(contatoGerenciado);
        }

        // --- ENDEREÇO DO CONTATO ---
        if (usuario.getContato().getEndereco() == null) {
            usuario.getContato().setEndereco(new Endereco());
        }

        return userRepository.save(usuario);
    }


    public User editarUsuario(User usuario) {
        User userExistente = userRepository.findById(usuario.getId())
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));

        userExistente.setNome(usuario.getNome());
        userExistente.setFotoPerfil(usuario.getFotoPerfil());
        userExistente.setTusCode(usuario.getTusCode());
        userExistente.setDataNascimento(usuario.getDataNascimento());
        userExistente.setDataCriacao(usuario.getDataCriacao());
        userExistente.setAtivo(usuario.getAtivo());
        userExistente.setCpf(usuario.getCpf());
        userExistente.setCampoDeEstudo(usuario.getCampoDeEstudo());

        // Se o usuário quiser mudar a senha → criptografa de novo
        if (usuario.getSenha() != null) {
            userExistente.setSenha(encoder.encode(usuario.getSenha()));
        }

        atualizarEnderecoUsuario(userExistente, usuario.getEndereco());
        atualizarContato(userExistente, usuario.getContato());

        if (usuario.getInstituicao() != null) {
            userExistente.setInstituicao(usuario.getInstituicao());
        }
        if (usuario.getFeiraInscrita() != null) {
            userExistente.setFeiraInscrita(usuario.getFeiraInscrita());
        }

        return userRepository.save(userExistente);
    }

    public void deletarUsuario(Integer id) {
        userRepository.deleteById(id);
    }

    public List<User> buscarUsuarios() {
        return userRepository.findAll();
    }

    public User buscarUsuarioPorId(Integer id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Usuário não encontrado"));
    }

    public User login(String email, String senha) {

        User user = userRepository.findByContatoEmail(email)
                .orElseThrow(() -> new RuntimeException("Credenciais inválidas"));

        // Compare com BCrypt — nunca usando equals()
        if (!encoder.matches(senha, user.getSenha())) {
            throw new RuntimeException("Credenciais inválidas");
        }

        user.setTokenSenha("TOKEN-" + System.currentTimeMillis());
        userRepository.save(user);

        return user;
    }


    private void atualizarContato(User userExistente, Contato contatoAtualizado) {
        if (contatoAtualizado != null) {
            Contato contatoExistente = userExistente.getContato();
            if (contatoExistente == null) {
                contatoExistente = new Contato();
                userExistente.setContato(contatoExistente);
            }

            contatoExistente.setTelefone(contatoAtualizado.getTelefone());
            contatoExistente.setEmail(contatoAtualizado.getEmail());
            atualizarEnderecoContato(contatoExistente, contatoAtualizado.getEndereco());
        }
    }

    private void atualizarEnderecoUsuario(User userExistente, Endereco enderecoAtualizado) {
        if (enderecoAtualizado != null) {
            Endereco enderecoExistente = userExistente.getEndereco();
            if (enderecoExistente == null) {
                enderecoExistente = new Endereco();
                userExistente.setEndereco(enderecoExistente);
            }

            enderecoExistente.setEstado(enderecoAtualizado.getEstado());
            enderecoExistente.setNumero(enderecoAtualizado.getNumero());
            enderecoExistente.setCep(enderecoAtualizado.getCep());
            enderecoExistente.setLogradouro(enderecoAtualizado.getLogradouro());
            enderecoExistente.setComplemento(enderecoAtualizado.getComplemento());
            enderecoExistente.setPais(enderecoAtualizado.getPais());
        }
    }

    private void atualizarEnderecoContato(Contato contatoExistente, Endereco enderecoAtualizado) {
        if (enderecoAtualizado != null) {
            Endereco enderecoExistente = contatoExistente.getEndereco();
            if (enderecoExistente == null) {
                enderecoExistente = new Endereco();
                contatoExistente.setEndereco(enderecoExistente);
            }

            enderecoExistente.setEstado(enderecoAtualizado.getEstado());
            enderecoExistente.setNumero(enderecoAtualizado.getNumero());
            enderecoExistente.setCep(enderecoAtualizado.getCep());
            enderecoExistente.setLogradouro(enderecoAtualizado.getLogradouro());
            enderecoExistente.setComplemento(enderecoAtualizado.getComplemento());
            enderecoExistente.setPais(enderecoAtualizado.getPais());
        }
    }
}
