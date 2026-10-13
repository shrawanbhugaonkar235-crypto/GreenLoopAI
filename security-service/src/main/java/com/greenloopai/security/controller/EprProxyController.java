package com.greenloopai.security.controller;

import com.greenloopai.security.filter.RequestIdFilter;
import com.greenloopai.security.service.FastApiProxyService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/epr")
public class EprProxyController {

    private final FastApiProxyService proxyService;

    public EprProxyController(FastApiProxyService proxyService) {
        this.proxyService = proxyService;
    }

    @PostMapping(value = "/process", consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> processEpr(
            @RequestBody Map<String, Object> eprRequest,
            HttpServletRequest request) {

        String requestId = (String) request.getAttribute(RequestIdFilter.REQUEST_ID_HEADER);
        String responseJson = proxyService.proxyEprProcessing(eprRequest, requestId);
        return ResponseEntity.ok(responseJson);
    }
}
