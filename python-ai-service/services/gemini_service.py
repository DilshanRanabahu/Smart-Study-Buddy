import google.generativeai as genai
import os
from typing import List, Dict
import json
import re

class GeminiService:
    
    def __init__(self):
        # Initialize Google AI Studio
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY is not set. Please add it to your environment variables.")
            
        genai.configure(api_key=api_key)
        
        # Use exact model from previous project
        model_name = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
        
        # If they still passed the vertex naming format, clean it up
        if "exp" in model_name or "gemini-2.0" in model_name:
             model_name = "gemini-flash-lite-latest"
             
        self.model = genai.GenerativeModel(model_name)

    def generate_summary(self, text: str) -> str:
        """Generate a friendly, student-oriented summary"""
        prompt = f"""You are a friendly study buddy helping a student understand this document. 
        Create a clear, conversational summary that:
        - Uses simple, everyday language (avoid overly formal/academic tone)
        - Highlights the main points and key takeaways
        - Explains concepts in a way that's easy to understand
        - Uses bullet points or short paragraphs for readability
        
        Document to summarize:
        {text[:10000]}
        
        Remember: Be helpful, friendly, and clear - like explaining to a friend!"""
        
        response = self.model.generate_content(prompt)
        return response.text

    def answer_question(self, text: str, question: str, chat_history: list = None) -> str:
        """Answer questions in a friendly, helpful way with conversation context"""
        
        # Build conversation context from chat history
        conversation_context = ""
        if chat_history and len(chat_history) > 0:
            conversation_context = "\n\nPrevious conversation:\n"
            for i, chat in enumerate(chat_history[-5:], 1):  # Include last 5 exchanges to keep context manageable
                conversation_context += f"\nQ{i}: {chat.get('question', '')}\n"
                conversation_context += f"A{i}: {chat.get('answer', '')}\n"
            conversation_context += "\n---\n"
        
        prompt = f"""You are a friendly study buddy helping a student understand their study material.
        {conversation_context}
        Current Question: {question}
        
        Document context (use this as reference, but feel free to expand with your knowledge):
        {text[:10000]}
        
        Provide a clear, helpful answer that:
        - References previous conversation if relevant (e.g., "As we discussed earlier...")
        - Uses the document as primary context when relevant
        - Supplements with your broader knowledge to give a complete, useful answer
        - Explains concepts clearly even if they're not fully covered in the document
        - Uses examples, analogies, or additional context when helpful
        - Sounds like a knowledgeable friend explaining, not just reading from the document
        - Is educational and thorough, not just a brief excerpt
        
        If the question is completely unrelated to the document, politely acknowledge that and still provide a helpful answer based on your knowledge."""
        
        response = self.model.generate_content(prompt)
        return response.text
        
    def generate_flashcards(self, text: str) -> List[Dict[str, str]]:
        """Generate student-friendly flashcards"""
        prompt = f"""You are creating study flashcards for a student. Generate 10 flashcards from this document.
        
        Guidelines:
        - Questions should be clear and specific
        - Answers should be concise (1-3 sentences max)
        - Focus on key concepts, definitions, and important facts
        - Use simple, student-friendly language
        - Make questions that actually help with studying
        
        Document:
        {text[:10000]}
        
        Return ONLY a JSON array in this exact format (no other text):
        [
            {{"question": "What is...", "answer": "..."}},
            {{"question": "How does...", "answer": "..."}}
        ]"""
        
        response = self.model.generate_content(prompt)
        
        # Clean response and parse JSON
        text_response = response.text.strip()
        
        # Remove markdown code blocks if present
        text_response = re.sub(r'```json\s*', '', text_response)
        text_response = re.sub(r'```\s*', '', text_response)
        text_response = text_response.strip()
        
        try:
            flashcards = json.loads(text_response)
            return flashcards
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {text_response}")
            # Return a default flashcard if parsing fails
            return [{"question": "Error generating flashcards", "answer": "Please try again"}]
    
    def generate_quiz(self, text: str) -> list:
        """Generate multiple-choice quiz questions"""
        prompt = f"""You are creating a quiz for a student. Generate 10 multiple-choice questions from this document.
        
        Guidelines:
        - Each question should have 4 options (A, B, C, D)
        - Only ONE option should be correct
        - Questions should test understanding, not just memorization
        - Include a brief explanation for the correct answer
        - Use clear, student-friendly language
        - Mix difficulty levels (easy, medium, hard)
        
        Document:
        {text[:10000]}
        
        Return ONLY a JSON array in this exact format (no other text):
        [
            {{
                "question": "What is the main purpose of...",
                "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
                "correctAnswer": 0,
                "explanation": "Brief explanation why option A is correct"
            }}
        ]
        
        Note: correctAnswer is the index (0-3) of the correct option in the options array."""
        
        response = self.model.generate_content(prompt)
        
        # Clean response and parse JSON
        text_response = response.text.strip()
        
        # Remove markdown code blocks if present
        text_response = re.sub(r'```json\s*', '', text_response)
        text_response = re.sub(r'```\s*', '', text_response)
        text_response = text_response.strip()
        
        try:
            quiz = json.loads(text_response)
            return quiz
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {text_response}")
            # Return a default question if parsing fails
            return [{
                "question": "Error generating quiz",
                "options": ["Please try again", "Error occurred", "Unable to generate", "Try later"],
                "correctAnswer": 0,
                "explanation": "There was an error generating the quiz. Please try again."
            }]
