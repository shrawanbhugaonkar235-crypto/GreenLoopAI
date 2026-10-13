package com.greenloopai.security.dto;

import java.util.Map;

public class HealthResponseDto {
    private String status;
    private String gateway;
    private String version;
    private Map<String, Object> services;

    public HealthResponseDto(String status, String gateway, String version, Map<String, Object> services) {
        this.status = status;
        this.gateway = gateway;
        this.version = version;
        this.services = services;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getGateway() {
        return gateway;
    }

    public void setGateway(String gateway) {
        this.gateway = gateway;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public Map<String, Object> getServices() {
        return services;
    }

    public void setServices(Map<String, Object> services) {
        this.services = services;
    }
}
