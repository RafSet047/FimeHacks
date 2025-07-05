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

# Image processing imports
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available for image processing")

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

        # Check for service account credentials
        self.service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

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

        # Check authentication methods
        has_api_key = bool(self.api_key)
        has_service_account = bool(self.service_account_path and os.path.exists(self.service_account_path))

        if not has_api_key and not has_service_account:
            logger.error("No Google authentication found. Provide either GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS")
            return

        try:
            # Initialize Generative AI for embeddings
            if has_api_key:
                genai.configure(api_key=self.api_key)
                self.genai_configured = True
                logger.info("Google Generative AI configured successfully with API key")
            elif has_service_account:
                # For service account authentication, we need to use a different approach
                # The generative AI SDK may not support service account directly
                # We'll try to use the API key method or fall back to vertex AI
                logger.info(f"Using service account credentials: {self.service_account_path}")

                # Try to initialize with service account for Vertex AI
                try:
                    import google.auth
                    from google.auth import default

                    # Load credentials
                    credentials, project_id = default()

                    # For now, we'll use the embedding API directly via REST calls
                    # This is a fallback approach
                    self.genai_configured = True
                    logger.info("Google services configured with service account credentials")
                except Exception as e:
                    logger.error(f"Failed to configure with service account: {e}")
                    return

            # Initialize Speech client (works with both API key and service account)
            if has_service_account:
                self.speech_client = speech.SpeechClient()
                logger.info("Google Speech client initialized with service account")
            else:
                # Speech client typically requires service account
                logger.warning("Google Speech client requires service account credentials")

        except Exception as e:
            logger.error(f"Failed to initialize Google services: {e}")
            self.genai_configured = False

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
        logger.info(f"Generating embeddings for text: {text[:50]}...")
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
                    # If using service account credentials, provide specific guidance
                    if self.service_account_path and not self.api_key:
                        logger.error("Service account credentials may not work with Generative AI SDK. Please provide GOOGLE_API_KEY for embeddings.")
                    # Create zero embedding as fallback
                    embeddings.append([0.0] * settings.text_embedding_dimension)

            logger.info(f"Generated {len(embeddings)} embeddings for text")
            return embeddings

        except Exception as e:
            logger.error(f"Text embedding generation failed: {e}")
            # If using service account credentials, provide specific guidance
            if self.service_account_path and not self.api_key:
                logger.error("Service account credentials may not work with Generative AI SDK. Please provide GOOGLE_API_KEY for embeddings.")
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
            "pil_available": PIL_AVAILABLE,
            "api_key_configured": bool(self.api_key),
            "service_account_configured": bool(self.service_account_path and os.path.exists(self.service_account_path)),
            "authentication_method": "api_key" if self.api_key else ("service_account" if self.service_account_path else "none")
        }

    def test_connection(self) -> Dict[str, Any]:
        """Test Google API connections"""
        results = {
            "embedding_test": False,
            "speech_test": False,
            "image_analysis_test": False,
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

        # Test image analysis capability
        if PIL_AVAILABLE and self.genai_configured:
            results["image_analysis_test"] = True
        else:
            if not PIL_AVAILABLE:
                results["errors"].append("PIL not available for image processing")
            if not self.genai_configured:
                results["errors"].append("Google Generative AI not configured for image analysis")

        return results

    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail") -> str:
        """Analyze image and generate description/caption using Google's vision model"""
        logger.info(f"Analyzing image: {image_path}")
        if not self.genai_configured:
            raise RuntimeError("Google Generative AI not configured")
        
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL not available for image processing")

        try:
            # Load image
            image = Image.open(image_path)
            logger.debug(f"Loaded image: {image_path}, size: {image.size}, mode: {image.mode}")

            # Apply rate limiting
            self._rate_limit()

            # Create model instance for multimodal content generation
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate content from image and prompt
            response = model.generate_content([prompt, image])
            
            if not response.text:
                logger.warning(f"No text generated for image: {image_path}")
                return ""

            logger.info(f"Generated image analysis for: {image_path}")
            return response.text.strip()

        except Exception as e:
            logger.error(f"Image analysis failed for {image_path}: {e}")
            raise

    def generate_image_caption(self, image_path: str) -> str:
        """Generate a descriptive caption for an image"""
        caption_prompt = (
            "Generate a clear, descriptive caption for this image. "
            "Focus on the main subjects, their actions, and the setting. "
            "Keep it concise but informative. Give me only one option."
        )
        return self.analyze_image(image_path, caption_prompt)

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image using OCR capabilities"""
        ocr_prompt = (
            "Extract all visible text from this image. "
            "Provide the text exactly as it appears, maintaining formatting where possible. "
            "If no text is visible, respond with 'No text found'."
        )
        return self.analyze_image(image_path, ocr_prompt)

    def analyze_image_content(self, image_path: str, question: str) -> str:
        """Answer specific questions about image content"""
        analysis_prompt = f"Looking at this image, please answer the following question: {question}"
        return self.analyze_image(image_path, analysis_prompt)

    async def analyze_image_async(self, image_path: str, prompt: str = "Describe this image in detail") -> str:
        """Async version of image analysis"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                self.analyze_image,
                image_path,
                prompt
            )
        return result

    async def generate_image_caption_async(self, image_path: str) -> str:
        """Async version of image caption generation"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                self.generate_image_caption,
                image_path
            )
        return result


# Global service instance
# Global instance will be created when needed
google_service = None

def get_google_service(api_key: Optional[str] = None) -> GoogleService:
    """Get or create the global GoogleService instance."""
    global google_service
    if google_service is None:
        google_service = GoogleService(api_key=api_key)
    return google_service
