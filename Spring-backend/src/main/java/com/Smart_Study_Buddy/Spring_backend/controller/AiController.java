package com.Smart_Study_Buddy.Spring_backend.controller;

import java.util.Map;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/api/ai")
@CrossOrigin(origins = {"http://localhost:5173", "http://44.204.96.20"})
public class AiController {

    private final RestTemplate restTemplate = new RestTemplate();
    
    @org.springframework.beans.factory.annotation.Value("${AI_SERVICE_URL:http://localhost:8000/api/ai}")
    private String AI_SERVICE_URL;

    @PostMapping("/summarize")
    public ResponseEntity<?> summarize(@RequestBody Map<String, String> request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

        return restTemplate.postForEntity(
                AI_SERVICE_URL + "/summarize",
                entity,
                String.class);
    }

    @PostMapping("/ask")
    public ResponseEntity<?> askQuestion(@RequestBody Map<String, Object> request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

        return restTemplate.postForEntity(
                AI_SERVICE_URL + "/ask",
                entity,
                String.class);
    }

    @PostMapping("/flashcards")
    public ResponseEntity<?> generateFlashcards(@RequestBody Map<String, String> request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

        return restTemplate.postForEntity(
                AI_SERVICE_URL + "/flashcards",
                entity,
                String.class);
    }

    @PostMapping("/generate-quiz")
    public ResponseEntity<?> generateQuiz(@RequestBody Map<String, String> request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);

        return restTemplate.postForEntity(
                AI_SERVICE_URL + "/generate-quiz",
                entity,
                String.class);
    }

}
