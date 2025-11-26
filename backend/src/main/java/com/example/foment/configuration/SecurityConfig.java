package com.example.foment.configuration;

import com.example.foment.domain.User;
import com.example.foment.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.util.Arrays;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Autowired
    private UserRepository userRepository;

    @Bean
    public UserDetailsService userDetailsService() {
        return username -> {
            com.example.foment.domain.User usuario = userRepository.findByContatoEmail(username)
                    .orElseThrow(() -> new UsernameNotFoundException("Usuário não encontrado com o email: " + username));
            
            // Constrói um objeto UserDetails a partir dos dados do seu usuário do banco.
            return org.springframework.security.core.userdetails.User.builder()
                    .username(usuario.getContato().getEmail())
                    .password(usuario.getSenha())
                    .roles("USER") // Você pode adicionar perfis (roles) aqui
                    .build();
        };
    }
    @Bean
    public BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http, AuthenticationManager authenticationManager) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource())) // Habilita e configura o CORS
            .csrf(csrf -> csrf.disable()) // Desabilita CSRF para APIs stateless
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/login", "/foment/**").permitAll() // Permite acesso público ao login e a todas as rotas de fomento
                .anyRequest().authenticated() // Exige autenticação para todas as outras rotas
            ); // Adiciona nosso filtro de autenticação JSON personalizado
        http.addFilterAt(jsonUsernamePasswordAuthenticationFilter(authenticationManager), UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    // Cria o nosso filtro personalizado
    private JsonUsernamePasswordAuthenticationFilter jsonUsernamePasswordAuthenticationFilter(AuthenticationManager authenticationManager) {
        JsonUsernamePasswordAuthenticationFilter filter = new JsonUsernamePasswordAuthenticationFilter(new ObjectMapper());
        filter.setAuthenticationManager(authenticationManager);
        filter.setRequiresAuthenticationRequestMatcher(new AntPathRequestMatcher("/login", "POST"));
        filter.setAuthenticationSuccessHandler((request, response, authentication) -> {
            response.setStatus(HttpServletResponse.SC_OK); // 200
        });
        filter.setAuthenticationFailureHandler((request, response, exception) -> {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED); // 401
        });
        return filter;
    }

    // Classe interna para o filtro
    private static class JsonUsernamePasswordAuthenticationFilter extends UsernamePasswordAuthenticationFilter {
        private final ObjectMapper objectMapper;

        public JsonUsernamePasswordAuthenticationFilter(ObjectMapper objectMapper) {
            this.objectMapper = objectMapper;
        }

        @Override
        public org.springframework.security.core.Authentication attemptAuthentication(HttpServletRequest request, HttpServletResponse response) {
            try {
                LoginRequest loginRequest = objectMapper.readValue(request.getInputStream(), LoginRequest.class);
                UsernamePasswordAuthenticationToken token = new UsernamePasswordAuthenticationToken(loginRequest.getEmail(), loginRequest.getSenha());
                setDetails(request, token);
                return this.getAuthenticationManager().authenticate(token);
            } catch (java.io.IOException e) {
                throw new IllegalArgumentException(e.getMessage());
            }
        }
    }

    // Classe interna para mapear o corpo da requisição de login JSON
    private static class LoginRequest {
        private String email;
        private String senha;

        // Getters e Setters são necessários para o Jackson (JSON para Objeto)
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getSenha() { return senha; }
        public void setSenha(String senha) { this.senha = senha; }
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList("http://localhost:5173"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "TRACE", "CONNECT"));
        configuration.setAllowedHeaders(Arrays.asList("Authorization", "Content-Type", "X-Requested-With", "Accept"));
        configuration.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
