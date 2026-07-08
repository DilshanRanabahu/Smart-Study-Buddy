package com.Smart_Study_Buddy.Spring_backend.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.Smart_Study_Buddy.Spring_backend.dto.YouTubeUploadRequest;
import com.Smart_Study_Buddy.Spring_backend.dto.YouTubeResponse;
import com.Smart_Study_Buddy.Spring_backend.service.FirestoreService;

@RestController
@RequestMapping("/api/youtube")
public class YouTubeController {

    @Autowired
    private FirestoreService firestoreService;

    private final RestTemplate restTemplate = new RestTemplate();
    
    @org.springframework.beans.factory.annotation.Value("${PYTHON_SERVICE_URL:http://python-backend:8000}")
    private String PYTHON_SERVICE_URL;

    @PostMapping("/upload")
    public ResponseEntity<?> uploadYouTubeVideo(@RequestBody YouTubeUploadRequest request) {
        try {
            System.out.println("📹 YouTube upload request received");
            System.out.println("  URL: " + request.getUrl());
            System.out.println("  User ID: " + request.getUserId());

            // Validate input
            if (request.getUrl() == null || request.getUrl().trim().isEmpty()) {
                return ResponseEntity.badRequest()
                        .body(Map.of("error", "YouTube URL is required"));
            }

            if (request.getUserId() == null || request.getUserId().trim().isEmpty()) {
                return ResponseEntity.badRequest()
                        .body(Map.of("error", "User ID is required"));
            }

            // Call Python AI service to extract transcript
            String extractUrl = PYTHON_SERVICE_URL + "/api/youtube/extract";
            Map<String, String> aiRequest = new HashMap<>();
            aiRequest.put("url", request.getUrl());

            System.out.println("🔄 Calling AI service: " + extractUrl);

            try {
                ResponseEntity<YouTubeResponse> aiResponse = restTemplate.postForEntity(
                        extractUrl,
                        aiRequest,
                        YouTubeResponse.class);

                if (aiResponse.getBody() == null || !aiResponse.getBody().isSuccess()) {
                    String error = aiResponse.getBody() != null ? aiResponse.getBody().getError()
                            : "Failed to extract transcript";
                    System.err.println("❌ AI service error: " + error);
                    return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                            .body(Map.of("error", error));
                }

                YouTubeResponse youtubeData = aiResponse.getBody();
                System.out.println("✅ Transcript extracted successfully");
                System.out.println("  Video ID: " + youtubeData.getVideoId());
                System.out.println("  Title: " + youtubeData.getTitle());
                System.out.println("  Duration: " + youtubeData.getDuration() + "s");
                System.out.println("  Transcript length: " + youtubeData.getFullText().length() + " characters");

                // Save to Firestore
                String documentId = firestoreService.saveYouTubeVideo(
                        request.getUserId(),
                        youtubeData.getVideoId(),
                        youtubeData.getTitle(),
                        youtubeData.getChannel(),
                        youtubeData.getThumbnailUrl(),
                        youtubeData.getFullText(),
                        youtubeData.getTranscript(),
                        youtubeData.getDuration());

                System.out.println("💾 Saved to Firestore with ID: " + documentId);

                // Return response
                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("documentId", documentId);
                response.put("videoId", youtubeData.getVideoId());
                response.put("title", youtubeData.getTitle());
                response.put("channel", youtubeData.getChannel());
                response.put("thumbnailUrl", youtubeData.getThumbnailUrl());
                response.put("duration", youtubeData.getDuration());
                response.put("message", "YouTube video added successfully");

                return ResponseEntity.ok(response);

            } catch (org.springframework.web.client.HttpClientErrorException e) {
                // Handle 400 Bad Request from Python service (e.g., no transcript available)
                System.err.println("❌ Python service returned error: " + e.getStatusCode());
                System.err.println("   Response body: " + e.getResponseBodyAsString());

                // Try to extract error message from response
                String errorMessage = "This video doesn't have captions/subtitles available. Please try a different video.";
                try {
                    if (e.getResponseBodyAsString().contains("no element found")) {
                        errorMessage = "No transcript found for this video. The video may not have captions enabled.";
                    } else if (e.getResponseBodyAsString().contains("detail")) {
                        // Extract error from JSON response
                        String body = e.getResponseBodyAsString();
                        int start = body.indexOf("\"detail\":\"") + 10;
                        int end = body.indexOf("\"", start);
                        if (start > 9 && end > start) {
                            errorMessage = body.substring(start, end);
                        }
                    }
                } catch (Exception parseError) {
                    // Use default message if parsing fails
                }

                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(Map.of("error", errorMessage));
            }

        } catch (Exception e) {
            System.err.println("❌ Error uploading YouTube video: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to upload YouTube video: " + e.getMessage()));
        }
    }
}
