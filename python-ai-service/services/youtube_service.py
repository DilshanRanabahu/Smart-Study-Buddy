import re
import requests
from typing import Dict, List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

class YouTubeService:
    """Service for extracting transcripts and metadata from YouTube videos"""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        """
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already just the video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    @staticmethod
    def get_transcript(video_id: str, languages: List[str] = ['en']) -> Dict:
        """
        Get transcript for a YouTube video using youtube-transcript-api
        This bypasses the strict AWS IP blocks that yt-dlp suffers from.
        """
        try:
            print(f"[INFO] Extracting transcript for video: {video_id}")
            
            # Fetch the transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to find a transcript in the requested languages
            transcript_obj = None
            for lang in languages:
                try:
                    transcript_obj = transcript_list.find_transcript([lang])
                    break
                except:
                    continue
            
            if not transcript_obj:
                # Fallback to the first available transcript if requested languages not found
                # Or try to translate it to English
                try:
                    transcript_obj = transcript_list.find_transcript(['en'])
                except:
                    # Just grab whatever is available
                    for t in transcript_list:
                        transcript_obj = t
                        break
            
            if not transcript_obj:
                return {
                    'success': False,
                    'error': f'No subtitles found for this video. Captions may be disabled.',
                    'error_type': 'no_subtitles'
                }
                
            # Fetch the actual transcript data
            transcript = transcript_obj.fetch()
            language_used = transcript_obj.language_code
            is_generated = transcript_obj.is_generated
            
            # Format the output to match exactly what the frontend expects
            formatted_transcript = []
            for item in transcript:
                formatted_transcript.append({
                    'text': item['text'].replace('\n', ' '),
                    'start': float(item['start']),
                    'duration': float(item['duration'])
                })
                
            # Extract full text
            full_text = ' '.join([entry['text'] for entry in formatted_transcript])
            
            # Calculate total duration
            total_duration = 0
            if formatted_transcript:
                last_entry = formatted_transcript[-1]
                total_duration = last_entry['start'] + last_entry['duration']
            
            print(f"  [OK] Successfully extracted {len(formatted_transcript)} subtitle entries via API")
            
            return {
                'success': True,
                'video_id': video_id,
                'language': language_used,
                'is_generated': is_generated,
                'transcript': formatted_transcript,
                'full_text': full_text,
                'total_duration': total_duration
            }
                
        except Exception as e:
            error_msg = str(e)
            print(f"  [ERROR] {error_msg}")
            
            if 'Subtitles are disabled' in error_msg or 'No transcripts were found' in error_msg:
                return {
                    'success': False,
                    'error': 'No subtitles found for this video. Captions may be disabled.',
                    'error_type': 'no_subtitles'
                }
            
            return {
                'success': False,
                'error': f'Error extracting transcript: {error_msg}',
                'error_type': 'unknown_error'
            }
    
    @staticmethod
    def get_video_metadata(video_id: str) -> Dict:
        """
        Get basic video metadata using YouTube's oEmbed API.
        This does NOT require authentication and bypasses IP blocks.
        """
        try:
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'title': data.get('title', 'Unknown Title'),
                    'author_name': data.get('author_name', 'Unknown Channel'),
                    'thumbnail_url': data.get('thumbnail_url', f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"),
                    'video_id': video_id,
                    'duration': 0 # oEmbed doesn't provide duration, but we'll calculate it from the transcript anyway
                }
            else:
                # Fallback to basic details if oEmbed fails
                return {
                    'success': True,
                    'title': f'YouTube Video ({video_id})',
                    'author_name': 'YouTube',
                    'thumbnail_url': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    'video_id': video_id,
                    'duration': 0
                }
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch metadata for {video_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to fetch video metadata: {str(e)}',
                'video_id': video_id
            }
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Convert seconds to MM:SS or HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
