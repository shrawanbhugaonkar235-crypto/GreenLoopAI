package com.greenloopai.security.dto;

import jakarta.validation.constraints.Size;
import java.util.List;
import java.util.Map;

public class ChatRequestDto {

    @Size(max = 2000, message = "Message exceeds maximum permitted length of 2000 characters.")
    private String message;

    private List<ChatMessageDto> messages;

    private Map<String, Object> context;

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public List<ChatMessageDto> getMessages() {
        return messages;
    }

    public void setMessages(List<ChatMessageDto> messages) {
        this.messages = messages;
    }

    public Map<String, Object> getContext() {
        return context;
    }

    public void setContext(Map<String, Object> context) {
        this.context = context;
    }

    public static class ChatMessageDto {
        private String role;
        
        @Size(max = 2000, message = "Message content exceeds maximum permitted length.")
        private String content;

        public String getRole() {
            return role;
        }

        public void setRole(String role) {
            this.role = role;
        }

        public String getContent() {
            return content;
        }

        public void setContent(String content) {
            this.content = content;
        }
    }
}
