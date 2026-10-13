package com.greenloopai.security.exception;

import com.greenloopai.security.dto.ErrorResponseDto;
import com.greenloopai.security.filter.RequestIdFilter;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponseDto> handleValidationExceptions(
            MethodArgumentNotValidException ex, HttpServletRequest request) {
        String requestId = getRequestId(request);
        String details = ex.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));

        log.warn("Validation error on {}: reqId={} details={}", request.getRequestURI(), requestId, details);

        ErrorResponseDto errorDto = new ErrorResponseDto(
                "VALIDATION_ERROR",
                details.isBlank() ? "Invalid request payload." : details,
                HttpStatus.BAD_REQUEST.value(),
                requestId
        );
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorDto);
    }

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<ErrorResponseDto> handleMaxSizeException(
            MaxUploadSizeExceededException ex, HttpServletRequest request) {
        String requestId = getRequestId(request);
        log.warn("Payload too large on {}: reqId={}", request.getRequestURI(), requestId);

        ErrorResponseDto errorDto = new ErrorResponseDto(
                "PAYLOAD_TOO_LARGE",
                "Uploaded image exceeds the maximum permitted file size.",
                HttpStatus.PAYLOAD_TOO_LARGE.value(),
                requestId
        );
        return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE).body(errorDto);
    }

    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<ErrorResponseDto> handleAuthenticationException(
            AuthenticationException ex, HttpServletRequest request) {
        String requestId = getRequestId(request);
        log.warn("Authentication failed on {}: reqId={}", request.getRequestURI(), requestId);

        ErrorResponseDto errorDto = new ErrorResponseDto(
                "UNAUTHORIZED",
                "Authentication required. Valid JWT bearer token missing or expired.",
                HttpStatus.UNAUTHORIZED.value(),
                requestId
        );
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(errorDto);
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponseDto> handleAccessDeniedException(
            AccessDeniedException ex, HttpServletRequest request) {
        String requestId = getRequestId(request);
        log.warn("Access denied on {}: reqId={}", request.getRequestURI(), requestId);

        ErrorResponseDto errorDto = new ErrorResponseDto(
                "FORBIDDEN",
                "You don't have permission to use this feature.",
                HttpStatus.FORBIDDEN.value(),
                requestId
        );
        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(errorDto);
    }

    @ExceptionHandler(WebClientResponseException.class)
    public ResponseEntity<ErrorResponseDto> handleWebClientException(
            WebClientResponseException ex, HttpServletRequest request) {
        String requestId = getRequestId(request);
        log.error("Upstream FastAPI service returned status {}: reqId={}", ex.getStatusCode(), requestId);

        String message = switch (ex.getStatusCode().value()) {
            case 503 -> "AI Assistant is temporarily unavailable.";
            case 429 -> "The assistant is temporarily busy. Please try again.";
            case 413 -> "Uploaded image is too large for processing.";
            case 400 -> "Invalid request data sent to processing engine.";
            default -> "AI processing service unavailable.";
        };

        ErrorResponseDto errorDto = new ErrorResponseDto(
                "UPSTREAM_SERVICE_ERROR",
                message,
                ex.getStatusCode().value(),
                requestId
        );
        return ResponseEntity.status(ex.getStatusCode()).body(errorDto);
    }

    @ExceptionHandler(ApiException.class)
    public ResponseEntity<ErrorResponseDto> handleApiException(
            ApiException ex, HttpServletRequest request) {
        String requestId = getRequestId(request);
        log.error("API Exception on {}: reqId={} msg={}", request.getRequestURI(), requestId, ex.getMessage());

        ErrorResponseDto errorDto = new ErrorResponseDto(
                ex.getErrorCategory(),
                ex.getMessage(),
                ex.getStatus().value(),
                requestId
        );
        return ResponseEntity.status(ex.getStatus()).body(errorDto);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponseDto> handleGenericException(
            Exception ex, HttpServletRequest request) {
        String requestId = getRequestId(request);
        log.error("Unhandled server error on {}: reqId={} ex={}", request.getRequestURI(), requestId, ex.getClass().getSimpleName());

        ErrorResponseDto errorDto = new ErrorResponseDto(
                "INTERNAL_SERVER_ERROR",
                "An unexpected internal error occurred.",
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                requestId
        );
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorDto);
    }

    private String getRequestId(HttpServletRequest request) {
        String requestId = (String) request.getAttribute(RequestIdFilter.REQUEST_ID_HEADER);
        return requestId != null ? requestId : "unknown";
    }
}
