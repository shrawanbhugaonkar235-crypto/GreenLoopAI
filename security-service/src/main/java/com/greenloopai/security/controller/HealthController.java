package com.greenloopai.security.controller;

import com.greenloopai.security.dto.HealthResponseDto;
import com.greenloopai.security.service.FastApiProxyService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class HealthController {

    private final FastApiProxyService proxyService;

    public HealthController(FastApiProxyService proxyService) {
        this.proxyService = proxyService;
    }

    @GetMapping("/")
    public ResponseEntity<Map<String, String>> root() {
        return ResponseEntity.ok(Map.of(
                "service", "GreenLoopAI Security Gateway",
                "status", "ONLINE"
        ));
    }

    @GetMapping("/api/health")
    public ResponseEntity<HealthResponseDto> health() {
        Map<String, Object> fastApiHealth = proxyService.checkFastApiHealth();

        HealthResponseDto response = new HealthResponseDto(
                "UP",
                "GreenLoopAI Spring Security Gateway",
                "1.0.0",
                Map.of("fastapi_backend", fastApiHealth)
        );

        return ResponseEntity.ok(response);
    }
}
