import axios from "axios";

const API_URL = "http://44.204.96.20:8080/api";

// Create axios instance
const apiClient = axios.create({
    baseURL: API_URL
});

// Add request interceptor to attach authentication token
apiClient.interceptors.request.use(
    (config) => {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const token = user.customToken; // Backend returns 'customToken', not 'token'

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export const registerUser = (username, email, password) => {
    return axios.post(`${API_URL}/auth/register`, {
        username,
        email,
        password
    });
};

export const loginUser = (email, password) => {
    return axios.post(`${API_URL}/auth/login`, {
        email,
        password
    });
};

export const uploadFile = (file, userId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('userId', userId);

    return apiClient.post('/documents/upload', formData, {
        headers: {
            "Content-Type": "multipart/form-data"
        }
    });
};

export const getUserDocuments = (userId) => {
    return apiClient.get('/documents', {
        params: { userId }
    });
};

// AI Features
export const extractPdfTextFromStoragePath = (storagePath, documentId) => {
    return apiClient.post('/pdf/extract-from-storage-path', {
        storagePath,
        documentId
    });
};

export const extractPdfText = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post('http://44.204.96.20:8000/api/ai/extract-text', formData);
};

export const summarizeDocument = (text, documentId) => {
    return apiClient.post('/ai/summarize', {
        text,
        document_id: documentId
    });
};

export const askQuestion = (text, question, documentId, chatHistory = []) => {
    return apiClient.post('/ai/ask', {
        text,
        question,
        document_id: documentId,
        chat_history: chatHistory
    });
};

export const generateFlashcards = (text, documentId) => {
    return apiClient.post('/ai/flashcards', {
        text,
        document_id: documentId
    });
};

export const generateQuiz = (text, documentId) => {
    return apiClient.post('/ai/generate-quiz', {
        text,
        document_id: documentId
    });
};

export const getDocumentContent = (documentId, userId) => {
    return apiClient.get(`/documents/${documentId}/content`, {
        params: { userId }
    });
};

export const deleteDocument = (documentId, userId) => {
    return apiClient.delete(`/documents/${documentId}`, {
        params: { userId }
    });
};

export const saveChatHistory = (documentId, userId, chatHistory) => {
    return apiClient.post(`/documents/${documentId}/chat-history`, chatHistory, {
        params: { userId }
    });
};

export const getChatHistory = (documentId, userId) => {
    return apiClient.get(`/documents/${documentId}/chat-history`, {
        params: { userId }
    });
};

// YouTube Integration
export const uploadYouTubeVideo = (url, userId) => {
    return apiClient.post('/youtube/upload', {
        url,
        userId
    });
};