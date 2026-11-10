package com.starfall.exception;

public class PythonServiceException extends RuntimeException {

    private final String operation;

    public PythonServiceException(String operation, String message) {
        super(message);
        this.operation = operation;
    }

    public PythonServiceException(String operation, String message, Throwable cause) {
        super(message, cause);
        this.operation = operation;
    }

    public String getOperation() {
        return operation;
    }
}
