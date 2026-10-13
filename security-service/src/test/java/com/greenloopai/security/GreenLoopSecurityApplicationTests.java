package com.greenloopai.security;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(classes = GreenLoopSecurityApplication.class)
class GreenLoopSecurityApplicationTests {

    @Test
    void contextLoads() {
        // Verifies the Spring Security application context loads with zero database dependencies
    }
}
