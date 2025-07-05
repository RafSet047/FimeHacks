import os
import io
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Google API imports
try:
    import google.generativeai as genai
    from google.cloud import speech
    from google.cloud.speech import RecognitionConfig, RecognitionAudio
    GOOGLE_APIs_AVAILABLE = True
except ImportError:
    GOOGLE_APIs_AVAILABLE = False
    logging.warning("Google AI APIs not available")

# Audio processing imports
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("pydub not available for audio processing")

from src.config.settings import settings

logger = logging.getLogger(__name__)


class GoogleService:
    """Google API service for text embeddings and audio transcription"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Try to get API key from environment variable first, then settings, then parameter
        self.api_key = (
            api_key or
            os.getenv('GOOGLE_API_KEY') or
            os.getenv('GOOGLE_GENERATIVE_AI_API_KEY') or
            settings.google_api_key
        )
        
        self.speech_client = None
        self.genai_configured = False
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second max
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google API services"""
        if not GOOGLE_APIs_AVAILABLE:
            logger.error("Google APIs not available. Install google-generativeai and google-cloud-speech")
            return
        
        if not self.api_key:
            logger.error("Google API key not provided")
            return
        
        try:
            # Initialize Generative AI for embeddings
            genai.configure(api_key=self.api_key)
            self.genai_configured = True
            logger.info("Google Generative AI configured successfully")
            
            # Initialize Speech client (requires service account JSON)
            # For now, we'll use the API key method
            self.speech_client = speech.SpeechClient()
            logger.info("Google Speech client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google services: {e}")
    
    def _rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def generate_text_embeddings(self, text: str, chunk_size: Optional[int] = None) -> List[List[float]]:
        """Generate embeddings for text using Google's embedding model"""
        logger.info(f"Generating embeddings for text: {text}")
        if not self.genai_configured:
            raise RuntimeError("Google Generative AI not configured")
        
        try:
            chunk_size = chunk_size or settings.text_chunk_size
            
            # Split text into chunks
            if len(text) <= chunk_size:
                chunks = [text]
            else:
                chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
            embeddings = []
            for i, chunk in enumerate(chunks):
                self._rate_limit()
                
                try:
                    # Use Google's text embedding model
                    result = genai.embed_content(
                        model=settings.google_embedding_model,
                        content=chunk,
                        task_type="retrieval_document"
                    )
                    
                    embedding = result['embedding']
                    
                    # Ensure embedding has correct dimensions
                    if len(embedding) != settings.text_embedding_dimension:
                        # Pad or truncate to match expected dimensions
                        if len(embedding) < settings.text_embedding_dimension:
                            embedding.extend([0.0] * (settings.text_embedding_dimension - len(embedding)))
                        else:
                            embedding = embedding[:settings.text_embedding_dimension]
                    
                    embeddings.append(embedding)
                    logger.debug(f"Generated embedding for chunk {i+1}/{len(chunks)}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate embedding for chunk {i}: {e}")
                    # Create zero embedding as fallback
                    embeddings.append([0.0] * settings.text_embedding_dimension)
            
            logger.info(f"Generated {len(embeddings)} embeddings for text")
            return embeddings
            
        except Exception as e:
            logger.error(f"Text embedding generation failed: {e}")
            raise
    
    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file to text using Google Speech-to-Text"""
        if not self.speech_client:
            raise RuntimeError("Google Speech client not initialized")
        
        try:
            # Prepare audio file
            audio_data = self._prepare_audio_file(audio_file_path)
            
            # Configure speaker diarization if enabled
            diarization_config = None
            if settings.enable_speaker_diarization:
                from google.cloud.speech_v1.types import SpeakerDiarizationConfig
                diarization_config = SpeakerDiarizationConfig(
                    enable_speaker_diarization=True,
                    min_speaker_count=1,
                    max_speaker_count=settings.max_speakers or 6
                )
            
            # Configure recognition
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=settings.google_speech_language,
                model=settings.google_speech_model,
                diarization_config=diarization_config,
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                enable_word_time_offsets=True
            )
            
            audio = RecognitionAudio(content=audio_data)
            
            # Perform transcription
            self._rate_limit()
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Process results
            transcription_result = self._process_transcription_response(response)
            
            logger.info(f"Transcribed audio file: {audio_file_path}")
            return transcription_result
            
        except Exception as e:
            logger.error(f"Audio transcription failed for {audio_file_path}: {e}")
            raise
    
    def _prepare_audio_file(self, audio_file_path: str) -> bytes:
        """Prepare audio file for transcription"""
        try:
            if PYDUB_AVAILABLE:
                # Convert audio to proper format using pydub
                audio = AudioSegment.from_file(audio_file_path)
                
                # Convert to mono, 16kHz, 16-bit PCM
                audio = audio.set_channels(1)
                audio = audio.set_frame_rate(16000)
                audio = audio.set_sample_width(2)
                
                # Export to bytes
                audio_buffer = io.BytesIO()
                audio.export(audio_buffer, format="wav")
                return audio_buffer.getvalue()
            else:
                # Fallback: read file directly
                with open(audio_file_path, 'rb') as audio_file:
                    return audio_file.read()
                    
        except Exception as e:
            logger.error(f"Audio preparation failed: {e}")
            raise
    
    def _process_transcription_response(self, response) -> Dict[str, Any]:
        """Process Google Speech-to-Text response"""
        try:
            if not response.results:
                return {
                    "transcript": "",
                    "confidence": 0.0,
                    "speakers": [],
                    "word_details": [],
                    "error": "No transcription results"
                }
            
            # Combine all results
            full_transcript = ""
            combined_confidence = 0.0
            speakers = set()
            word_details = []
            
            for result in response.results:
                alternative = result.alternatives[0]
                full_transcript += alternative.transcript
                combined_confidence += alternative.confidence
                
                # Process word details with speaker info
                if hasattr(alternative, 'words') and alternative.words:
                    for word in alternative.words:
                        word_info = {
                            "word": word.word,
                            "start_time": word.start_time.total_seconds(),
                            "end_time": word.end_time.total_seconds(),
                            "confidence": word.confidence
                        }
                        
                        # Add speaker info if available
                        if hasattr(word, 'speaker_tag') and word.speaker_tag:
                            word_info["speaker"] = word.speaker_tag
                            speakers.add(word.speaker_tag)
                        
                        word_details.append(word_info)
            
            # Average confidence
            if response.results:
                combined_confidence /= len(response.results)
            
            # Format speaker list
            speaker_list = [f"Speaker {s}" for s in sorted(speakers)]
            
            # Count words
            word_count = len(full_transcript.split())
            
            return {
                "transcript": full_transcript.strip(),
                "confidence": combined_confidence,
                "speakers": speaker_list,
                "word_details": word_details,
                "word_count": word_count
            }
            
        except Exception as e:
            logger.error(f"Failed to process transcription response: {e}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "speakers": [],
                "word_details": [],
                "error": str(e)
            }
    
    async def transcribe_audio_async(self, audio_file_path: str) -> Dict[str, Any]:
        """Async version of audio transcription"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                self.transcribe_audio, 
                audio_file_path
            )
        return result
    
    async def generate_text_embeddings_async(self, text: str, chunk_size: Optional[int] = None) -> List[List[float]]:
        """Async version of text embedding generation"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                self.generate_text_embeddings, 
                text, 
                chunk_size
            )
        return result
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of Google API services"""
        return {
            "google_apis_available": GOOGLE_APIs_AVAILABLE,
            "genai_configured": self.genai_configured,
            "speech_client_available": self.speech_client is not None,
            "pydub_available": PYDUB_AVAILABLE,
            "api_key_configured": bool(self.api_key)
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Google API connections"""
        results = {
            "embedding_test": False,
            "speech_test": False,
            "errors": []
        }
        
        # Test embedding generation
        try:
            test_embeddings = self.generate_text_embeddings("test text")
            if test_embeddings and len(test_embeddings) > 0:
                results["embedding_test"] = True
            else:
                results["errors"].append("Embedding generation returned empty results")
        except Exception as e:
            results["errors"].append(f"Embedding test failed: {e}")
        
        # Test speech client (skip actual transcription test for now)
        if self.speech_client:
            results["speech_test"] = True
        else:
            results["errors"].append("Speech client not available")
        
        return results


# Global service instance
# Global instance will be created when needed
google_service = None

def get_google_service(api_key: Optional[str] = None) -> GoogleService:
    """Get or create the global GoogleService instance."""
    global google_service
    if google_service is None:
        google_service = GoogleService(api_key=api_key)
    return google_service 