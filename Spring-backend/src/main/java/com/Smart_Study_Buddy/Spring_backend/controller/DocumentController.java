package com.Smart_Study_Buddy.Spring_backend.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.Smart_Study_Buddy.Spring_backend.service.FirestoreService;
import com.Smart_Study_Buddy.Spring_backend.service.StorageService;

@RestController
@RequestMapping("/api/documents")
@CrossOrigin(origins = {"http://localhost:5173", "http://44.204.96.20"})
public class DocumentController {

    private final StorageService storageService;
    private final FirestoreService firestoreService;

    public DocumentController(StorageService storageService, FirestoreService firestoreService) {
        this.storageService = storageService;
        this.firestoreService = firestoreService;
    }

    @PostMapping("/upload")
    public ResponseEntity<?> uploadDocument(
            @RequestParam("file") MultipartFile file,
            @RequestParam("userId") String userId) {
        try {
            if (file.isEmpty()) {
                return ResponseEntity.badRequest().body("File is empty");
            }

            String filename = file.getOriginalFilename();
            String storagePath = "users/" + userId + "/documents/" + java.util.UUID.randomUUID() + "_" + filename;

            String downloadUrl = storageService.uploadFile(file, storagePath);

            String documentId = firestoreService.saveDocument(userId, filename, storagePath, downloadUrl);

            Map<String, String> response = new HashMap<>();
            response.put("documentId", documentId);
            response.put("filename", filename);
            response.put("downloadUrl", downloadUrl);

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    @GetMapping
    public ResponseEntity<?> getUserDocuments(@RequestParam String userId) {
        try {
            List<Map<String, Object>> documents = firestoreService.getUserDocuments(userId);
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    @GetMapping("/{documentId}/content")
    public ResponseEntity<?> getDocumentContent(
            @PathVariable String documentId,
            @RequestParam String userId) {
        try {
            Map<String, Object> doc = firestoreService.getDocument(documentId);

            if (doc == null) {
                return ResponseEntity.notFound().build();
            }

            String storagePath = (String) doc.get("storagePath");
            String freshDownloadUrl;

            // Fallback for old documents without storagePath
            if (storagePath == null || storagePath.isEmpty()) {
                // For old documents, just use the stored URL (may be expired)
                freshDownloadUrl = (String) doc.get("downloadUrl");
                System.out.println("Warning: Old document without storagePath, using stored URL");
            } else {
                // Generate fresh URL for new documents
                freshDownloadUrl = storageService.getDownloadUrl(storagePath);
            }

            Map<String, Object> response = new HashMap<>();
            response.put("documentId", documentId);
            response.put("filename", doc.get("filename"));
            response.put("downloadUrl", freshDownloadUrl);
            response.put("storagePath", storagePath);

            // Include cached extracted text if available
            String extractedText = (String) doc.get("extractedText");
            if (extractedText != null && !extractedText.isEmpty()) {
                response.put("extractedText", extractedText);
                response.put("textCached", true);
            } else {
                response.put("textCached", false);
            }

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    @DeleteMapping("/{documentId}")
    public ResponseEntity<?> deleteDocument(
            @PathVariable String documentId,
            @RequestParam String userId) {
        try {
            Map<String, Object> doc = firestoreService.getDocument(documentId);

            if (doc == null) {
                return ResponseEntity.notFound().build();
            }

            // Verify user owns the document
            if (!userId.equals(doc.get("userId"))) {
                return ResponseEntity.status(403).body("Unauthorized");
            }

            // Delete from Firestore
            firestoreService.deleteDocument(documentId);

            return ResponseEntity.ok(Map.of("message", "Document deleted successfully"));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    @PostMapping("/{documentId}/chat-history")
    public ResponseEntity<?> saveChatHistory(
            @PathVariable String documentId,
            @RequestParam String userId,
            @RequestBody List<Map<String, String>> chatHistory) {
        try {
            firestoreService.saveChatHistory(documentId, userId, chatHistory);
            return ResponseEntity.ok(Map.of("message", "Chat history saved"));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    @GetMapping("/{documentId}/chat-history")
    public ResponseEntity<?> getChatHistory(
            @PathVariable String documentId,
            @RequestParam String userId) {
        try {
            List<Map<String, String>> chatHistory = firestoreService.getChatHistory(documentId, userId);
            return ResponseEntity.ok(Map.of("chatHistory", chatHistory));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }
}
