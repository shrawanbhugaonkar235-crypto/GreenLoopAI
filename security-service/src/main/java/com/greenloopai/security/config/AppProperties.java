package com.greenloopai.security.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import java.util.List;

@ConfigurationProperties(prefix = "greenloopai")
public class AppProperties {

    private FastApi fastapi = new FastApi();
    private Security security = new Security();

    public FastApi getFastapi() {
        return fastapi;
    }

    public void setFastapi(FastApi fastapi) {
        this.fastapi = fastapi;
    }

    public Security getSecurity() {
        return security;
    }

    public void setSecurity(Security security) {
        this.security = security;
    }

    public static class FastApi {
        private String baseUrl = "http://localhost:8000";
        private String serviceToken = "dev-internal-secret-token";
        private int connectTimeoutMs = 5000;
        private int readTimeoutMs = 30000;

        public String getBaseUrl() {
            return baseUrl;
        }

        public void setBaseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
        }

        public String getServiceToken() {
            return serviceToken;
        }

        public void setServiceToken(String serviceToken) {
            this.serviceToken = serviceToken;
        }

        public int getConnectTimeoutMs() {
            return connectTimeoutMs;
        }

        public void setConnectTimeoutMs(int connectTimeoutMs) {
            this.connectTimeoutMs = connectTimeoutMs;
        }

        public int getReadTimeoutMs() {
            return readTimeoutMs;
        }

        public void setReadTimeoutMs(int readTimeoutMs) {
            this.readTimeoutMs = readTimeoutMs;
        }
    }

    public static class Security {
        private Cors cors = new Cors();
        private RateLimit rateLimit = new RateLimit();

        public Cors getCors() {
            return cors;
        }

        public void setCors(Cors cors) {
            this.cors = cors;
        }

        public RateLimit getRateLimit() {
            return rateLimit;
        }

        public void setRateLimit(RateLimit rateLimit) {
            this.rateLimit = rateLimit;
        }

        public static class Cors {
            private List<String> allowedOrigins = List.of("http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:5500");
            private List<String> allowedMethods = List.of("GET", "POST", "PUT", "DELETE", "OPTIONS");
            private List<String> allowedHeaders = List.of("Authorization", "Content-Type", "X-Request-Id", "X-Requested-With", "Accept");
            private List<String> exposedHeaders = List.of("X-Request-Id");
            private boolean allowCredentials = true;

            public List<String> getAllowedOrigins() {
                return allowedOrigins;
            }

            public void setAllowedOrigins(List<String> allowedOrigins) {
                this.allowedOrigins = allowedOrigins;
            }

            public List<String> getAllowedMethods() {
                return allowedMethods;
            }

            public void setAllowedMethods(List<String> allowedMethods) {
                this.allowedMethods = allowedMethods;
            }

            public List<String> getAllowedHeaders() {
                return allowedHeaders;
            }

            public void setAllowedHeaders(List<String> allowedHeaders) {
                this.allowedHeaders = allowedHeaders;
            }

            public List<String> getExposedHeaders() {
                return exposedHeaders;
            }

            public void setExposedHeaders(List<String> exposedHeaders) {
                this.exposedHeaders = exposedHeaders;
            }

            public boolean isAllowCredentials() {
                return allowCredentials;
            }

            public void setAllowCredentials(boolean allowCredentials) {
                this.allowCredentials = allowCredentials;
            }
        }

        public static class RateLimit {
            private boolean enabled = true;
            private int requestsPerMinute = 120;
            private int burstCapacity = 30;

            public boolean isEnabled() {
                return enabled;
            }

            public void setEnabled(boolean enabled) {
                this.enabled = enabled;
            }

            public int getRequestsPerMinute() {
                return requestsPerMinute;
            }

            public void setRequestsPerMinute(int requestsPerMinute) {
                this.requestsPerMinute = requestsPerMinute;
            }

            public int getBurstCapacity() {
                return burstCapacity;
            }

            public void setBurstCapacity(int burstCapacity) {
                this.burstCapacity = burstCapacity;
            }
        }
    }
}
