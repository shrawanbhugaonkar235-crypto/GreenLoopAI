package com.greenloopai.security.controller;

import com.greenloopai.security.filter.RequestIdFilter;
import com.greenloopai.security.service.FastApiProxyService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/verification")
public class VerificationProxyController {

    private final FastApiProxyService proxyService;

    public VerificationProxyController(FastApiProxyService proxyService) {
        this.proxyService = proxyService;
    }

    @PostMapping(value = "/verify", consumes = MediaType.MULTIPART_FORM_DATA_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> verify(
            @RequestParam("image") MultipartFile imageFile,
            HttpServletRequest request) {

        String requestId = (String) request.getAttribute(RequestIdFilter.REQUEST_ID_HEADER);
        String responseJson = proxyService.proxyVerification(imageFile, requestId);
        return ResponseEntity.ok(responseJson);
    }
}
