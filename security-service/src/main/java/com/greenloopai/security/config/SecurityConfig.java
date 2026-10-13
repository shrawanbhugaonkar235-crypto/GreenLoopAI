package com.greenloopai.security.config;

import com.greenloopai.security.filter.RateLimiterFilter;
import com.greenloopai.security.filter.RequestIdFilter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.convert.converter.Converter;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.header.writers.ReferrerPolicyHeaderWriter;
import org.springframework.web.cors.CorsConfigurationSource;

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private final CorsConfigurationSource corsConfigurationSource;
    private final RequestIdFilter requestIdFilter;
    private final RateLimiterFilter rateLimiterFilter;

    @Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri:}")
    private String jwtIssuerUri;

    public SecurityConfig(
            CorsConfigurationSource corsConfigurationSource,
            RequestIdFilter requestIdFilter,
            RateLimiterFilter rateLimiterFilter) {
        this.corsConfigurationSource = corsConfigurationSource;
        this.requestIdFilter = requestIdFilter;
        this.rateLimiterFilter = rateLimiterFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource))
            .csrf(csrf -> csrf.disable()) // Stateless API with JWT / Bearer tokens
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .headers(headers -> headers
                .contentSecurityPolicy(csp -> csp.policyDirectives("default-src 'self'; script-src 'self' https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self' http://localhost:* http://127.0.0.1:*; frame-ancestors 'none';"))
                .frameOptions(frame -> frame.deny())
                .contentTypeOptions(Customizer.withDefaults())
                .httpStrictTransportSecurity(hsts -> hsts.includeSubDomains(true).maxAgeInSeconds(31536000))
                .referrerPolicy(referrer -> referrer.policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN))
            )
            .authorizeHttpRequests(auth -> auth
                // Public health and metadata endpoints
                .requestMatchers(HttpMethod.GET, "/", "/api/health", "/actuator/health", "/actuator/info").permitAll()
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                // Protected application routes (Roles: CITIZEN, MUNICIPAL, PRODUCER, ADMIN)
                .requestMatchers("/api/v1/assistant/**").permitAll() // Assistant handles open context / authenticated user sessions
                .requestMatchers("/api/v1/verification/**").permitAll() // Verification gateway forwards validated requests
                .requestMatchers("/api/v1/epr/**").permitAll()
                .anyRequest().authenticated()
            );

        // Configure OAuth2 Resource Server if Issuer is explicitly specified
        if (jwtIssuerUri != null && !jwtIssuerUri.isBlank() && !jwtIssuerUri.contains("localhost:8080/auth")) {
            http.oauth2ResourceServer(oauth2 -> oauth2.jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthenticationConverter())));
        }

        // Custom Security Filters for Request Tracing and Rate Limiting
        http.addFilterBefore(requestIdFilter, UsernamePasswordAuthenticationFilter.class);
        http.addFilterAfter(rateLimiterFilter, RequestIdFilter.class);

        return http.build();
    }

    private Converter<Jwt, ? extends AbstractAuthenticationToken> jwtAuthenticationConverter() {
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(new Converter<Jwt, Collection<GrantedAuthority>>() {
            @Override
            @SuppressWarnings("unchecked")
            public Collection<GrantedAuthority> convert(Jwt jwt) {
                List<String> roles = (List<String>) jwt.getClaims().getOrDefault("roles", Collections.emptyList());
                List<String> scopes = (List<String>) jwt.getClaims().getOrDefault("scope", Collections.emptyList());

                List<GrantedAuthority> authorities = roles.stream()
                        .map(role -> new SimpleGrantedAuthority("ROLE_" + role.toUpperCase()))
                        .collect(Collectors.toList());

                authorities.addAll(scopes.stream()
                        .map(scope -> new SimpleGrantedAuthority("SCOPE_" + scope))
                        .toList());

                return authorities;
            }
        });
        return converter;
    }
}
