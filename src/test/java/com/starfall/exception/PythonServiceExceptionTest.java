package com.starfall.exception;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;

class PythonServiceExceptionTest {

    @Test
    void retainsOperationMessageAndCause() {
        RuntimeException cause = new RuntimeException("offline");

        PythonServiceException exception = new PythonServiceException(
                "agent-decisions", "Agent request failed", cause);

        assertEquals("agent-decisions", exception.getOperation());
        assertEquals("Agent request failed", exception.getMessage());
        assertSame(cause, exception.getCause());
    }
}
