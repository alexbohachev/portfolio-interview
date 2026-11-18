package ua.agrichain.work03.api;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import ua.agrichain.work03.service.IdempotencyConflictException;

@RestControllerAdvice
public class RestExceptionHandler {

    @ExceptionHandler(IdempotencyConflictException.class)
    public ResponseEntity<String> conflict(IdempotencyConflictException ex) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(ex.getMessage());
    }
}