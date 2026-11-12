package com.starfall.config;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ServiceConfigTest {

    @Mock
    private RestTemplateBuilder builder;

    @Mock
    private RestTemplate restTemplate;

    @Test
    void appliesConfiguredConnectionAndReadTimeouts() {
        Duration connectTimeout = Duration.ofSeconds(2);
        Duration readTimeout = Duration.ofSeconds(30);
        when(builder.setConnectTimeout(connectTimeout)).thenReturn(builder);
        when(builder.setReadTimeout(readTimeout)).thenReturn(builder);
        when(builder.build()).thenReturn(restTemplate);

        RestTemplate result = new ServiceConfig().restTemplate(builder, connectTimeout, readTimeout);

        assertSame(restTemplate, result);
        verify(builder).setConnectTimeout(connectTimeout);
        verify(builder).setReadTimeout(readTimeout);
        verify(builder).build();
    }
}
