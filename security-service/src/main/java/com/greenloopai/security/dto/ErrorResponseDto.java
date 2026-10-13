package com.greenloopai.security.dto;

import java.time.Instant;

public class ErrorResponseDto {
    private String error;
    private String message;
    private int status;
    private String requestId;
    private Instant timestamp;

    public ErrorResponseDto() {
        this.timestamp = Instant.now();
    }

    public ErrorResponseDto(String error, String message, int status, String requestId) {
        this.error = error;
        this.message = message;
        this.status = status;
        this.requestId = requestId;
        this.timestamp = Instant.now();
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Instant timestamp) {
        this.timestamp = timestamp;
    }
}
