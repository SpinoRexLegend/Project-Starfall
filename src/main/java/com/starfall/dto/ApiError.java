package com.starfall.dto;

public record ApiError(String status, String code, String message) {
    public static ApiError of(String code, String message) {
        return new ApiError("error", code, message);
    }
}
