import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.cloud.aiplatform.initializer")

from fastapi import FastAPI, UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.pdf_service import extract_text_from_pdf
from services.gemini_service import GeminiService
from services.youtube_service import YouTubeService
from models.schemas import SummarizeRequest,QuestionRequest
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Smart Study Buddy AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_service = GeminiService()

@app.get("/health")
async def health_check():
    return {"status" : "healthy"}

@app.post("/api/ai/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """Extract text from uploaded PDF"""
    try:
        content = await file.read()
        text = extract_text_from_pdf(content)
        return {"text": text, "length": len(text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/summarize")
async def summarize_document(request: SummarizeRequest):
    """Generate summary from document text"""
    try:
        summary = gemini_service.generate_summary(request.text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/ask")
async def ask_question(request: QuestionRequest):
        """Answer question about document"""

        try:
            answer = gemini_service.answer_question(
                request.text,
                request.question,
                request.chat_history
            )
            return {"answer": answer, "question": request.question}
        except Exception as e:
            raise HTTPException(status_code=500,detail=str(e))

@app.post("/api/ai/flashcards")
async def generate_flashcards(request: SummarizeRequest):
    """Generate flashcards from document"""

    try:
        flashcards = gemini_service.generate_flashcards(request.text)
        return {"flashcards": flashcards, "count": len(flashcards)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/generate-quiz")
async def generate_quiz(request: SummarizeRequest):
    """Generate quiz questions from document"""
    try:
        quiz = gemini_service.generate_quiz(request.text)
        return {"quiz": quiz, "count": len(quiz)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# YouTube Integration Endpoints

class YouTubeRequest(BaseModel):
    url: str

class YouTubeTranscriptRequest(BaseModel):
    video_id: str
    languages: list[str] = ['en']

@app.post("/api/youtube/extract")
async def extract_youtube_transcript(request: YouTubeRequest):
    """Extract transcript from YouTube video URL"""
    try:
        print(f"📹 Received YouTube extract request: {request.url}")
        
        # Extract video ID from URL
        video_id = YouTubeService.extract_video_id(request.url)
        print(f"  Video ID extracted: {video_id}")
        
        if not video_id:
            raise HTTPException(
                status_code=400, 
                detail="Invalid YouTube URL. Please provide a valid YouTube video URL."
            )
        
        # Get transcript
        print(f"  Getting transcript for video ID: {video_id}")
        transcript_data = YouTubeService.get_transcript(video_id)
        print(f"  Transcript success: {transcript_data.get('success')}")
        
        if not transcript_data['success']:
            print(f"  ❌ Transcript error: {transcript_data.get('error')}")
            raise HTTPException(
                status_code=400,
                detail=transcript_data['error']
            )
        
        # Get video metadata
        print(f"  Getting metadata...")
        metadata = YouTubeService.get_video_metadata(video_id)
        
        result = {
            "success": True,
            "video_id": video_id,
            "title": metadata.get('title', 'Unknown Title'),
            "channel": metadata.get('author_name', 'Unknown Channel'),
            "thumbnail_url": metadata.get('thumbnail_url', ''),
            "transcript": transcript_data['transcript'],
            "full_text": transcript_data['full_text'],
            "language": transcript_data['language'],
            "is_generated": transcript_data['is_generated'],
            "duration": transcript_data['total_duration']
        }
        
        print(f"  ✅ Success! Title: {result['title']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting transcript: {str(e)}")

@app.get("/api/youtube/metadata/{video_id}")
async def get_youtube_metadata(video_id: str):
    """Get YouTube video metadata"""
    try:
        metadata = YouTubeService.get_video_metadata(video_id)
        
        if not metadata['success']:
            raise HTTPException(
                status_code=404,
                detail=metadata.get('error', 'Video not found')
            )
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata: {str(e)}")