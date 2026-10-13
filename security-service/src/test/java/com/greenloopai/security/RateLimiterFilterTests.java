package com.greenloopai.security;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(properties = {
    "greenloopai.security.rate-limit.requests-per-minute=2",
    "greenloopai.security.rate-limit.burst-capacity=2"
})
@AutoConfigureMockMvc
class RateLimiterFilterTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testRateLimiterEnforcesBurstLimit() throws Exception {
        // Request 1: Allowed
        mockMvc.perform(get("/")).andExpect(status().isOk());

        // Request 2: Allowed
        mockMvc.perform(get("/")).andExpect(status().isOk());

        // Request 3: Exceeds burst capacity -> 429 Too Many Requests
        mockMvc.perform(get("/"))
                .andExpect(status().isTooManyRequests())
                .andExpect(jsonPath("$.error").value("TOO_MANY_REQUESTS"));
    }
}
