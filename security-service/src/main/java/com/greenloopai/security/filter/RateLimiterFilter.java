package com.greenloopai.security.filter;

import com.greenloopai.security.config.AppProperties;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

@Component
public class RateLimiterFilter extends OncePerRequestFilter {

    private final AppProperties appProperties;
    private final Map<String, TokenBucket> clientBuckets = new ConcurrentHashMap<>();

    public RateLimiterFilter(AppProperties appProperties) {
        this.appProperties = appProperties;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        AppProperties.Security.RateLimit rateLimitProps = appProperties.getSecurity().getRateLimit();

        if (!rateLimitProps.isEnabled()) {
            filterChain.doFilter(request, response);
            return;
        }

        // Identify client by IP (or user identifier when available)
        String clientIp = getClientIp(request);
        TokenBucket bucket = clientBuckets.computeIfAbsent(clientIp, k -> new TokenBucket(
                rateLimitProps.getRequestsPerMinute(),
                rateLimitProps.getBurstCapacity()
        ));

        if (!bucket.tryConsume()) {
            String requestId = (String) request.getAttribute(RequestIdFilter.REQUEST_ID_HEADER);
            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.getWriter().write(String.format(
                    "{\"error\":\"TOO_MANY_REQUESTS\",\"message\":\"The assistant is temporarily busy. Please try again.\",\"request_id\":\"%s\"}",
                    requestId != null ? requestId : "unknown"
            ));
            return;
        }

        filterChain.doFilter(request, response);
    }

    private String getClientIp(HttpServletRequest request) {
        String xfHeader = request.getHeader("X-Forwarded-For");
        if (xfHeader == null || xfHeader.isEmpty() || !xfHeader.contains(",")) {
            return request.getRemoteAddr();
        }
        return xfHeader.split(",")[0].trim();
    }

    private static class TokenBucket {
        private final int refillRatePerMinute;
        private final int capacity;
        private final AtomicInteger tokens;
        private final AtomicLong lastRefillTimestamp;

        public TokenBucket(int refillRatePerMinute, int capacity) {
            this.refillRatePerMinute = refillRatePerMinute;
            this.capacity = capacity;
            this.tokens = new AtomicInteger(capacity);
            this.lastRefillTimestamp = new AtomicLong(System.currentTimeMillis());
        }

        public synchronized boolean tryConsume() {
            refill();
            if (tokens.get() > 0) {
                tokens.decrementAndGet();
                return true;
            }
            return false;
        }

        private void refill() {
            long now = System.currentTimeMillis();
            long elapsed = now - lastRefillTimestamp.get();
            if (elapsed > 1000) {
                int tokensToAdd = (int) ((elapsed / 60000.0) * refillRatePerMinute);
                if (tokensToAdd > 0) {
                    tokens.updateAndGet(current -> Math.min(capacity, current + tokensToAdd));
                    lastRefillTimestamp.set(now);
                }
            }
        }
    }
}
