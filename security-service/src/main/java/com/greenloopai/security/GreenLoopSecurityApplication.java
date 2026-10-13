package com.greenloopai.security;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

/**
 * GreenLoopAI Spring Boot Security Gateway Application
 * 
 * Provides OAuth2 / JWT validation, role-based authorization, rate limiting,
 * security headers, and secure internal forwarding to the FastAPI AI processing engine.
 * Zero database dependencies.
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class GreenLoopSecurityApplication {

    public static void main(String[] args) {
        SpringApplication.run(GreenLoopSecurityApplication.class, args);
    }
}
