import pytest
import os
import io
import time
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from typing import Dict, Any, List

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.external_apis.google_service import GoogleService


class TestGoogleServiceInitialization:
    """Test Google service initialization and configuration"""
    
    def test_init_with_api_key_parameter(self):
        """Test initialization with API key parameter"""
        service = GoogleService(api_key="test_key_param")
        assert service.api_key == "test_key_param"
    
    
    @patch('src.services.external_apis.google_service.settings')
    def test_init_with_settings_fallback(self, mock_settings):
        """Test initialization with settings fallback"""
        mock_settings.google_api_key = "settings_key"
        service = GoogleService()
        assert service.api_key == "settings_key"
    
    @patch('src.services.external_apis.google_service.GOOGLE_APIs_AVAILABLE', True)
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.speech')
    def test_successful_initialization(self, mock_speech, mock_genai):
        """Test successful service initialization"""
        mock_speech_client = Mock()
        mock_speech.SpeechClient.return_value = mock_speech_client
        
        service = GoogleService(api_key="test_key")
        
        assert service.genai_configured == True
        assert service.speech_client == mock_speech_client
        mock_genai.configure.assert_called_once_with(api_key="test_key")
    
    @patch('src.services.external_apis.google_service.GOOGLE_APIs_AVAILABLE', False)
    def test_initialization_without_apis(self):
        """Test initialization when Google APIs not available"""
        service = GoogleService(api_key="test_key")
        
        assert service.genai_configured == False
        assert service.speech_client is None
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.services.external_apis.google_service.settings') as mock_settings:
                mock_settings.google_api_key = None
                service = GoogleService()
                
                assert service.api_key is None
                assert service.genai_configured == False


class TestTextEmbeddingGeneration:
    """Test text embedding generation functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.service = GoogleService(api_key="test_key")
        self.service.genai_configured = True
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_generate_text_embeddings_single_chunk(self, mock_settings, mock_genai):
        """Test embedding generation for single chunk"""
        mock_settings.text_chunk_size = 1000
        mock_settings.text_embedding_dimension = 1536
        
        # Mock API response
        mock_genai.embed_content.return_value = {
            'embedding': [0.1, 0.2, 0.3] * 512  # 1536 dimensions
        }
        
        result = self.service.generate_text_embeddings("Short text")
        
        assert len(result) == 1
        assert len(result[0]) == 1536
        mock_genai.embed_content.assert_called_once_with(
            model=mock_settings.google_embedding_model,
            content="Short text",
            task_type="retrieval_document"
        )
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_generate_text_embeddings_multiple_chunks(self, mock_settings, mock_genai):
        """Test embedding generation for multiple chunks"""
        mock_settings.text_chunk_size = 10
        mock_settings.text_embedding_dimension = 1536
        
        # Mock API response
        mock_genai.embed_content.return_value = {
            'embedding': [0.1] * 1536
        }
        
        long_text = "This is a very long text that will be split into multiple chunks"
        result = self.service.generate_text_embeddings(long_text)
        
        # Should have multiple chunks
        assert len(result) > 1
        assert all(len(embedding) == 1536 for embedding in result)
        assert mock_genai.embed_content.call_count > 1
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_generate_text_embeddings_dimension_padding(self, mock_settings, mock_genai):
        """Test embedding dimension padding"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        
        # Mock API response with fewer dimensions
        mock_genai.embed_content.return_value = {
            'embedding': [0.1, 0.2, 0.3]  # Only 3 dimensions
        }
        
        result = self.service.generate_text_embeddings("Test text")
        
        assert len(result) == 1
        assert len(result[0]) == 1536
        assert result[0][:3] == [0.1, 0.2, 0.3]
        assert all(x == 0.0 for x in result[0][3:])  # Rest should be zeros
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_generate_text_embeddings_dimension_truncation(self, mock_settings, mock_genai):
        """Test embedding dimension truncation"""
        mock_settings.text_embedding_dimension = 100
        mock_settings.text_chunk_size = 1000
        
        # Mock API response with more dimensions
        mock_genai.embed_content.return_value = {
            'embedding': [0.1] * 2000  # 2000 dimensions
        }
        
        result = self.service.generate_text_embeddings("Test text")
        
        assert len(result) == 1
        assert len(result[0]) == 100
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_generate_text_embeddings_api_error(self, mock_settings, mock_genai):
        """Test handling of API errors in embedding generation"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        mock_genai.embed_content.side_effect = Exception("API Error")
        
        result = self.service.generate_text_embeddings("Test text")
        
        # Should return zero embedding as fallback
        assert len(result) == 1
        assert len(result[0]) == 1536
        assert all(x == 0.0 for x in result[0])
    
    def test_generate_text_embeddings_not_configured(self):
        """Test embedding generation when service not configured"""
        service = GoogleService(api_key="test_key")
        service.genai_configured = False
        
        with pytest.raises(RuntimeError, match="Google Generative AI not configured"):
            service.generate_text_embeddings("Test text")
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_generate_text_embeddings_custom_chunk_size(self, mock_settings, mock_genai):
        """Test embedding generation with custom chunk size"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        mock_genai.embed_content.return_value = {'embedding': [0.1] * 1536}
        
        result = self.service.generate_text_embeddings("Test text", chunk_size=5)
        
        # Should use custom chunk size
        assert len(result) >= 1


class TestAudioTranscription:
    """Test audio transcription functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.service = GoogleService(api_key="test_key")
        self.service.speech_client = Mock()
    
    @patch('src.services.external_apis.google_service.settings')
    @patch('src.services.external_apis.google_service.PYDUB_AVAILABLE', True)
    @patch('src.services.external_apis.google_service.AudioSegment')
    def test_transcribe_audio_success(self, mock_audio_segment, mock_settings):
        """Test successful audio transcription"""
        # Mock settings
        mock_settings.google_speech_language = "en-US"
        mock_settings.google_speech_model = "latest_long"
        mock_settings.enable_speaker_diarization = True
        mock_settings.max_speakers = 6
        
        # Mock audio processing
        mock_audio = Mock()
        mock_audio.set_channels.return_value = mock_audio
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.set_sample_width.return_value = mock_audio
        
        mock_buffer = Mock()
        mock_buffer.getvalue.return_value = b"audio_data"
        
        with patch('io.BytesIO', return_value=mock_buffer):
            mock_audio_segment.from_file.return_value = mock_audio
            
            # Mock speech recognition response
            mock_word1 = Mock()
            mock_word1.word = "Hello"
            mock_word1.start_time.total_seconds.return_value = 0.0
            mock_word1.end_time.total_seconds.return_value = 0.5
            mock_word1.confidence = 0.95
            mock_word1.speaker_tag = 1
            
            mock_word2 = Mock()
            mock_word2.word = "world"
            mock_word2.start_time.total_seconds.return_value = 0.6
            mock_word2.end_time.total_seconds.return_value = 1.0
            mock_word2.confidence = 0.90
            mock_word2.speaker_tag = 1
            
            mock_alternative = Mock()
            mock_alternative.transcript = "Hello world"
            mock_alternative.confidence = 0.92
            mock_alternative.words = [mock_word1, mock_word2]
            
            mock_result = Mock()
            mock_result.alternatives = [mock_alternative]
            
            mock_response = Mock()
            mock_response.results = [mock_result]
            
            self.service.speech_client.recognize.return_value = mock_response
            
            result = self.service.transcribe_audio("test_audio.mp3")
            
            assert result["transcript"] == "Hello world"
            assert result["confidence"] == 0.92
            assert "Speaker 1" in result["speakers"]
            assert len(result["word_details"]) == 2
            assert result["word_count"] == 2
    
    @patch('src.services.external_apis.google_service.PYDUB_AVAILABLE', False)
    def test_transcribe_audio_without_pydub(self):
        """Test audio transcription fallback without pydub"""
        mock_response = Mock()
        mock_response.results = []
        self.service.speech_client.recognize.return_value = mock_response
        
        with patch('builtins.open', mock_open(read_data=b"raw_audio_data")):
            result = self.service.transcribe_audio("test_audio.mp3")
            
            assert result["transcript"] == ""
            assert result["confidence"] == 0.0
            assert "No transcription results" in result["error"]
    
    def test_transcribe_audio_no_speech_client(self):
        """Test transcription when speech client not available"""
        service = GoogleService(api_key="test_key")
        service.speech_client = None
        
        with pytest.raises(RuntimeError, match="Google Speech client not initialized"):
            service.transcribe_audio("test_audio.mp3")
    
    @patch('src.services.external_apis.google_service.settings')
    def test_transcribe_audio_api_error(self, mock_settings):
        """Test handling of API errors in transcription"""
        mock_settings.google_speech_language = "en-US"
        mock_settings.google_speech_model = "latest_long"
        mock_settings.enable_speaker_diarization = True
        mock_settings.max_speakers = 6
        
        self.service.speech_client.recognize.side_effect = Exception("API Error")
        
        with patch.object(self.service, '_prepare_audio_file', return_value=b"audio_data"):
            with pytest.raises(Exception, match="API Error"):
                self.service.transcribe_audio("test_audio.mp3")
    
    def test_process_transcription_response_empty(self):
        """Test processing empty transcription response"""
        mock_response = Mock()
        mock_response.results = []
        
        result = self.service._process_transcription_response(mock_response)
        
        assert result["transcript"] == ""
        assert result["confidence"] == 0.0
        assert result["speakers"] == []
        assert result["word_details"] == []
        assert "No transcription results" in result["error"]


class TestAsyncOperations:
    """Test async versions of operations"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.service = GoogleService(api_key="test_key")
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_async(self):
        """Test async audio transcription"""
        mock_result = {"transcript": "async test", "confidence": 0.95}
        
        with patch.object(self.service, 'transcribe_audio', return_value=mock_result):
            result = await self.service.transcribe_audio_async("test_audio.mp3")
            
            assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_generate_text_embeddings_async(self):
        """Test async text embedding generation"""
        mock_result = [[0.1, 0.2, 0.3]]
        
        with patch.object(self.service, 'generate_text_embeddings', return_value=mock_result):
            result = await self.service.generate_text_embeddings_async("test text")
            
            assert result == mock_result


class TestServiceStatus:
    """Test service status and health checks"""
    
    def test_get_service_status(self):
        """Test getting service status"""
        service = GoogleService(api_key="test_key")
        service.genai_configured = True
        service.speech_client = Mock()
        
        status = service.get_service_status()
        
        assert "google_apis_available" in status
        assert "genai_configured" in status
        assert "speech_client_available" in status
        assert "pydub_available" in status
        assert "api_key_configured" in status
        assert status["genai_configured"] == True
        assert status["speech_client_available"] == True
        assert status["api_key_configured"] == True
    
    def test_test_connection_success(self):
        """Test connection testing with success"""
        service = GoogleService(api_key="test_key")
        service.speech_client = Mock()
        
        mock_embeddings = [[0.1, 0.2, 0.3]]
        with patch.object(service, 'generate_text_embeddings', return_value=mock_embeddings):
            result = service.test_connection()
            
            assert result["embedding_test"] == True
            assert result["speech_test"] == True
            assert len(result["errors"]) == 0
    
    def test_test_connection_embedding_failure(self):
        """Test connection testing with embedding failure"""
        service = GoogleService(api_key="test_key")
        service.speech_client = Mock()
        
        with patch.object(service, 'generate_text_embeddings', side_effect=Exception("Embedding error")):
            result = service.test_connection()
            
            assert result["embedding_test"] == False
            assert result["speech_test"] == True
            assert "Embedding test failed" in result["errors"][0]
    
    def test_test_connection_no_speech_client(self):
        """Test connection testing without speech client"""
        service = GoogleService(api_key="test_key")
        service.speech_client = None
        
        mock_embeddings = [[0.1, 0.2, 0.3]]
        with patch.object(service, 'generate_text_embeddings', return_value=mock_embeddings):
            result = service.test_connection()
            
            assert result["embedding_test"] == True
            assert result["speech_test"] == False
            assert "Speech client not available" in result["errors"]


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting(self):
        """Test rate limiting mechanism"""
        service = GoogleService(api_key="test_key")
        service.min_request_interval = 0.1
        
        start_time = time.time()
        
        # First request
        service._rate_limit()
        first_time = time.time()
        
        # Second request immediately
        service._rate_limit()
        second_time = time.time()
        
        # Should have waited at least min_request_interval
        time_diff = second_time - first_time
        assert time_diff >= service.min_request_interval


class TestGlobalInstance:
    """Test global instance functionality"""
    
    def test_global_instance_exists(self):
        """Test that global instance can be created"""
        from src.services.external_apis.google_service import get_google_service
        service = get_google_service(api_key="test_key")
        assert service is not None
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_env_key'})
    def test_global_instance_api_key_from_env(self):
        """Test global instance uses environment variable"""
        # Reset the global instance first
        import src.services.external_apis.google_service as gs
        gs.google_service = None
        
        from src.services.external_apis.google_service import get_google_service
        service = get_google_service()
        assert service.api_key == "test_env_key"


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_healthcare_document_embedding(self, mock_settings, mock_genai):
        """Test embedding healthcare document text"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        mock_settings.google_embedding_model = "text-embedding-3-small"
        
        # Mock API response
        mock_genai.embed_content.return_value = {
            'embedding': [0.1] * 1536
        }
        
        medical_text = "Patient diagnosed with hypertension. Prescribed medication X."
        
        service = GoogleService(api_key="test_key")
        service.genai_configured = True
        
        result = service.generate_text_embeddings(medical_text)
        
        assert len(result) == 1
        assert len(result[0]) == 1536
        mock_genai.embed_content.assert_called_once_with(
            model="text-embedding-3-small",
            content=medical_text,
            task_type="retrieval_document"
        )
    
    @patch('src.services.external_apis.google_service.settings')
    def test_university_lecture_transcription(self, mock_settings):
        """Test transcription of university lecture audio"""
        mock_settings.google_speech_language = "en-US"
        mock_settings.google_speech_model = "latest_long"
        mock_settings.enable_speaker_diarization = True
        mock_settings.max_speakers = 6
        
        service = GoogleService(api_key="test_key")
        service.speech_client = Mock()
        
        # Mock lecture transcription
        mock_alternative = Mock()
        mock_alternative.transcript = "Today we will discuss machine learning algorithms and their applications"
        mock_alternative.confidence = 0.95
        mock_alternative.words = []
        
        mock_result = Mock()
        mock_result.alternatives = [mock_alternative]
        
        mock_response = Mock()
        mock_response.results = [mock_result]
        
        service.speech_client.recognize.return_value = mock_response
        
        with patch.object(service, '_prepare_audio_file', return_value=b"lecture_audio"):
            result = service.transcribe_audio("lecture.mp3")
            
        assert result["transcript"] == "Today we will discuss machine learning algorithms and their applications"
        assert result["confidence"] == 0.95
        assert result["word_count"] == 10  # Number of words in the transcript


if __name__ == "__main__":
    pytest.main([__file__]) 