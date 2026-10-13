package com.greenloopai.security.controller;

import com.greenloopai.security.dto.ChatRequestDto;
import com.greenloopai.security.filter.RequestIdFilter;
import com.greenloopai.security.service.FastApiProxyService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/assistant")
public class AssistantProxyController {

    private final FastApiProxyService proxyService;

    public AssistantProxyController(FastApiProxyService proxyService) {
        this.proxyService = proxyService;
    }

    @PostMapping(value = "/chat", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> chat(
            @Valid @RequestBody ChatRequestDto requestDto,
            HttpServletRequest request) {

        String requestId = (String) request.getAttribute(RequestIdFilter.REQUEST_ID_HEADER);
        String responseJson = proxyService.proxyAssistantChat(requestDto, requestId);
        return ResponseEntity.ok(responseJson);
    }
}
