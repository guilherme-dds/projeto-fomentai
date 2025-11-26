package com.example.foment.controller;

import com.example.foment.domain.*;
import com.example.foment.service.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/foment")
@RequiredArgsConstructor
public class FomentController {

    // Services complexos
    private final FomentServiceUser fomentServiceUser;
    private final FomentServiceFeira fomentServiceFeira;

    // Services CRUD simples
    private final FomentServiceEndereco fomentServiceEndereco;
    private final FomentServiceContato fomentServiceContato;
    private final FomentServicePremiacao fomentServicePremiacao;
    private final FomentServiceDatas fomentServiceDatas; // Corrigido o nome
    private final FomentServiceInstituicao fomentServiceInstituicao; // Adicionado
    private final FomentServiceProjeto fomentServiceProjeto;         // Adicionado
    private final FomentServiceOrganizacao fomentServiceOrganizacao; // Adicionado

    // === Usuários ===
    @GetMapping("/usuarios")
    public List<User> buscarUsuarios() {
        return fomentServiceUser.buscarUsuarios();
    }

    @PostMapping("/login")
    public ResponseEntity<User> login(@RequestBody User payload) {
        User user = fomentServiceUser.login(payload.getContato().getEmail(), payload.getSenha());
        return ResponseEntity.ok(user);
    }

    @GetMapping("/usuarios/{id}")
    public User buscarUsuarioPorId(@PathVariable Integer id) {
        return fomentServiceUser.buscarUsuarioPorId(id);
    }

    @PostMapping(value = "/usuarios")
    @ResponseStatus(HttpStatus.CREATED)
    public User cadastrarUsuario(@RequestBody User usuario) {
        return fomentServiceUser.cadastrarUsuario(usuario);
    }

    @PatchMapping(value = "/usuarios/{id}")
    public User editarUsuario(@PathVariable Integer id, @RequestBody User usuario) {
        usuario.setId(id);
        return fomentServiceUser.editarUsuario(usuario);
    }

    @DeleteMapping("/usuarios/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarUsuario(@PathVariable Integer id) {
        fomentServiceUser.deletarUsuario(id);
    }

    // === Endereços ===
    @GetMapping("/enderecos")
    public List<Endereco> buscarEnderecos() {
        return fomentServiceEndereco.listarTodos(); // Método atualizado
    }

    @GetMapping("/enderecos/{id}")
    public Endereco buscarEnderecoPorId(@PathVariable Integer id) {
        return fomentServiceEndereco.buscarPorId(id); // Método atualizado
    }

    @PostMapping(value = "/enderecos")
    @ResponseStatus(HttpStatus.CREATED)
    public Endereco cadastrarEndereco(@RequestBody Endereco endereco) {
        return fomentServiceEndereco.salvar(endereco); // Método atualizado
    }

    @PatchMapping(value = "/enderecos/{id}")
    public Endereco editarEndereco(@PathVariable Integer id, @RequestBody Endereco endereco) {
        endereco.setId(id); // Corrigido
        return fomentServiceEndereco.salvar(endereco); // Método atualizado
    }

    @DeleteMapping("/enderecos/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarEndereco(@PathVariable Integer id) {
        fomentServiceEndereco.deletar(id); // Método atualizado
    }

    // === Contatos ===
    @GetMapping("/contatos")
    public List<Contato> buscarContatos() {
        return fomentServiceContato.listarTodos(); // Método atualizado
    }

    @GetMapping("/contatos/{id}")
    public Contato buscarContatoPorId(@PathVariable Integer id) {
        return fomentServiceContato.buscarPorId(id); // Método atualizado
    }

    @PostMapping(value = "/contatos")
    @ResponseStatus(HttpStatus.CREATED)
    public Contato cadastrarContato(@RequestBody Contato contato) {
        return fomentServiceContato.salvar(contato); // Método atualizado
    }

    @PatchMapping(value = "/contatos/{id}")
    public Contato editarContato(@PathVariable Integer id, @RequestBody Contato contato) {
        contato.setId(id); // Corrigido
        return fomentServiceContato.salvar(contato); // Método atualizado
    }

    @DeleteMapping("/contatos/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarContato(@PathVariable Integer id) {
        fomentServiceContato.deletar(id); // Método atualizado
    }

    // === Feiras ===
    @GetMapping("/feiras")
    public List<Feira> buscarFeiras() {
        return fomentServiceFeira.buscarFeiras(); // Corrigido
    }

    @GetMapping("/feiras/{id}")
    public Feira buscarFeiraPorId(@PathVariable Integer id) {
        return fomentServiceFeira.buscarFeiraPorId(id); // Corrigido
    }

    @PostMapping(value = "/feiras")
    @ResponseStatus(HttpStatus.CREATED)
    public Feira cadastrarFeira(@RequestBody Feira feira) {
        return fomentServiceFeira.cadastrarFeira(feira); // Corrigido
    }

    @PatchMapping(value = "/feiras/{id}")
    public Feira editarFeira(@PathVariable Integer id, @RequestBody Feira feira) {
        feira.setId(id); // Corrigido
        return fomentServiceFeira.editarFeira(feira); // Corrigido
    }

    @DeleteMapping("/feiras/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarFeira(@PathVariable Integer id) {
        fomentServiceFeira.deletarFeira(id); // Corrigido
    }

    // === Premiações ===
    @GetMapping("/premiacoes")
    public List<Premiacao> buscarPremiacoes() {
        return fomentServicePremiacao.listarTodas();
    }

    @GetMapping("/premiacoes/{id}")
    public Premiacao buscarPremiacaoPorId(@PathVariable Integer id) {
        // Correto, pois o service de premiacao do usuário retorna Optional
        return fomentServicePremiacao.buscarPorId(id)
                .orElseThrow(() -> new RuntimeException("Premiação não encontrada com o ID: " + id));
    }

    @PostMapping(value = "/premiacoes")
    @ResponseStatus(HttpStatus.CREATED)
    public Premiacao cadastrarPremiacao(@RequestBody Premiacao premiacao) {
        return fomentServicePremiacao.salvar(premiacao);
    }

    @PatchMapping(value = "/premiacoes/{id}")
    public Premiacao editarPremiacao(@PathVariable Integer id, @RequestBody Premiacao premiacao) {
        premiacao.setId(id); // Corrigido
        return fomentServicePremiacao.salvar(premiacao);
    }

    @DeleteMapping("/premiacoes/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarPremiacao(@PathVariable Integer id) {
        fomentServicePremiacao.deletar(id);
    }

    // === Datas ===
    @GetMapping("/datas")
    public List<Datas> buscarDatas() {
        return fomentServiceDatas.listarTodos(); // Corrigido
    }

    @GetMapping("/datas/{id}")
    public Datas buscarDataPorId(@PathVariable Integer id) {
        // Corrigido - Nosso service já retorna a entidade ou lança exceção
        return fomentServiceDatas.buscarPorId(id);
    }

    @PostMapping(value = "/datas")
    @ResponseStatus(HttpStatus.CREATED)
    public Datas cadastrarData(@RequestBody Datas datas) {
        return fomentServiceDatas.salvar(datas); // Corrigido
    }

    @PatchMapping(value = "/datas/{id}")
    public Datas editarData(@PathVariable Integer id, @RequestBody Datas datas) {
        datas.setId(id); // Corrigido
        return fomentServiceDatas.salvar(datas); // Corrigido
    }

    @DeleteMapping("/datas/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarData(@PathVariable Integer id) {
        fomentServiceDatas.deletar(id); // Corrigido
    }

    // === Instituições (Adicionado) ===
    @GetMapping("/instituicoes")
    public List<Instituicao> buscarInstituicoes() {
        return fomentServiceInstituicao.listarTodos();
    }

    @GetMapping("/instituicoes/{id}")
    public Instituicao buscarInstituicaoPorId(@PathVariable Integer id) {
        return fomentServiceInstituicao.buscarPorId(id);
    }

    @PostMapping(value = "/instituicoes")
    @ResponseStatus(HttpStatus.CREATED)
    public Instituicao cadastrarInstituicao(@RequestBody Instituicao instituicao) {
        return fomentServiceInstituicao.salvar(instituicao);
    }

    @PatchMapping(value = "/instituicoes/{id}")
    public Instituicao editarInstituicao(@PathVariable Integer id, @RequestBody Instituicao instituicao) {
        instituicao.setId(id);
        return fomentServiceInstituicao.salvar(instituicao);
    }

    @DeleteMapping("/instituicoes/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarInstituicao(@PathVariable Integer id) {
        fomentServiceInstituicao.deletar(id);
    }

    // === Projetos (Adicionado) ===
    @GetMapping("/projetos")
    public List<Projeto> buscarProjetos() {
        return fomentServiceProjeto.listarTodos();
    }

    @GetMapping("/projetos/{id}")
    public Projeto buscarProjetoPorId(@PathVariable Integer id) {
        return fomentServiceProjeto.buscarPorId(id);
    }

    @PostMapping(value = "/projetos")
    @ResponseStatus(HttpStatus.CREATED)
    public Projeto cadastrarProjeto(@RequestBody Projeto projeto) {
        return fomentServiceProjeto.salvar(projeto);
    }

    @PatchMapping(value = "/projetos/{id}")
    public Projeto editarProjeto(@PathVariable Integer id, @RequestBody Projeto projeto) {
        projeto.setId(id);
        return fomentServiceProjeto.salvar(projeto);
    }

    @DeleteMapping("/projetos/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarProjeto(@PathVariable Integer id) {
        fomentServiceProjeto.deletar(id);
    }

    // === Organizações (Adicionado) ===
    @GetMapping("/organizacoes")
    public List<Organizacao> buscarOrganizacoes() {
        return fomentServiceOrganizacao.listarTodos();
    }

    @GetMapping("/organizacoes/{id}")
    public Organizacao buscarOrganizacaoPorId(@PathVariable Integer id) {
        return fomentServiceOrganizacao.buscarPorId(id);
    }

    @PostMapping(value = "/organizacoes")
    @ResponseStatus(HttpStatus.CREATED)
    public Organizacao cadastrarOrganizacao(@RequestBody Organizacao organizacao) {
        return fomentServiceOrganizacao.salvar(organizacao);
    }

    @PatchMapping(value = "/organizacoes/{id}")
    public Organizacao editarOrganizacao(@PathVariable Integer id, @RequestBody Organizacao organizacao) {
        organizacao.setId(id);
        return fomentServiceOrganizacao.salvar(organizacao);
    }

    @DeleteMapping("/organizacoes/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletarOrganizacao(@PathVariable Integer id) {
        fomentServiceOrganizacao.deletar(id);
    }
}