package com.greenloopai.security.service;

import com.greenloopai.security.config.AppProperties;
import com.greenloopai.security.dto.ChatRequestDto;
import com.greenloopai.security.exception.ApiException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.io.IOException;
import java.util.Map;

@Service
public class FastApiProxyService {

    private static final Logger log = LoggerFactory.getLogger(FastApiProxyService.class);
    private final WebClient fastApiWebClient;
    private final AppProperties appProperties;

    public FastApiProxyService(WebClient fastApiWebClient, AppProperties appProperties) {
        this.fastApiWebClient = fastApiWebClient;
        this.appProperties = appProperties;
    }

    public String proxyAssistantChat(ChatRequestDto requestDto, String requestId) {
        String serviceToken = appProperties.getFastapi().getServiceToken();

        try {
            return fastApiWebClient.post()
                    .uri("/api/v1/assistant/chat")
                    .header("X-Request-Id", requestId)
                    .header("X-Service-Token", serviceToken)
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(requestDto)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
        } catch (WebClientResponseException e) {
            log.error("FastAPI Chat Error: status={} reqId={}", e.getStatusCode(), requestId);
            throw e;
        } catch (Exception e) {
            log.error("FastAPI Assistant Connection Failure: reqId={} msg={}", requestId, e.getMessage());
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "SERVICE_UNAVAILABLE", "AI processing service unavailable.");
        }
    }

    public String proxyVerification(MultipartFile imageFile, String requestId) {
        String serviceToken = appProperties.getFastapi().getServiceToken();

        try {
            MultipartBodyBuilder builder = new MultipartBodyBuilder();
            ByteArrayResource fileResource = new ByteArrayResource(imageFile.getBytes()) {
                @Override
                public String getFilename() {
                    return imageFile.getOriginalFilename() != null ? imageFile.getOriginalFilename() : "upload.jpg";
                }
            };
            builder.part("image", fileResource, MediaType.parseMediaType(
                    imageFile.getContentType() != null ? imageFile.getContentType() : MediaType.IMAGE_JPEG_VALUE
            ));

            return fastApiWebClient.post()
                    .uri("/api/v1/verification/verify")
                    .header("X-Request-Id", requestId)
                    .header("X-Service-Token", serviceToken)
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(builder.build()))
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
        } catch (WebClientResponseException e) {
            log.error("FastAPI Verification Error: status={} reqId={}", e.getStatusCode(), requestId);
            throw e;
        } catch (IOException e) {
            log.error("Failed to read uploaded image bytes: reqId={}", requestId);
            throw new ApiException(HttpStatus.BAD_REQUEST, "INVALID_PAYLOAD", "Unable to read uploaded image content.");
        } catch (Exception e) {
            log.error("FastAPI Verification Connection Failure: reqId={} msg={}", requestId, e.getMessage());
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "SERVICE_UNAVAILABLE", "AI processing service unavailable.");
        }
    }

    public String proxyEprProcessing(Map<String, Object> eprRequest, String requestId) {
        String serviceToken = appProperties.getFastapi().getServiceToken();

        try {
            return fastApiWebClient.post()
                    .uri("/api/v1/epr/process")
                    .header("X-Request-Id", requestId)
                    .header("X-Service-Token", serviceToken)
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(eprRequest)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
        } catch (WebClientResponseException e) {
            log.error("FastAPI EPR Error: status={} reqId={}", e.getStatusCode(), requestId);
            throw e;
        } catch (Exception e) {
            log.error("FastAPI EPR Connection Failure: reqId={} msg={}", requestId, e.getMessage());
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "SERVICE_UNAVAILABLE", "AI processing service unavailable.");
        }
    }

    public Map<String, Object> checkFastApiHealth() {
        try {
            return fastApiWebClient.get()
                    .uri("/health")
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            log.warn("FastAPI health check failed: {}", e.getMessage());
            return Map.of("status", "DOWN", "error", "Cannot connect to AI service");
        }
    }
}
