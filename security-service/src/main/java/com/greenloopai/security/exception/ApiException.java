package com.greenloopai.security.exception;

import org.springframework.http.HttpStatus;

public class ApiException extends RuntimeException {
    private final HttpStatus status;
    private final String errorCategory;

    public ApiException(HttpStatus status, String errorCategory, String message) {
        super(message);
        this.status = status;
        this.errorCategory = errorCategory;
    }

    public HttpStatus getStatus() {
        return status;
    }

    public String getErrorCategory() {
        return errorCategory;
    }
}
