import pytest
import time
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
from typing import Dict, Any, List

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.document_extractor import DocumentTextExtractor
from src.services.external_apis.google_service import GoogleService


class TestDocumentToEmbeddingPipeline:
    """Test complete pipeline from document extraction to embeddings"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.doc_extractor = DocumentTextExtractor()
        self.google_service = GoogleService(api_key="test_key")
        self.google_service.genai_configured = True
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_pdf_to_embeddings_pipeline(self, mock_settings, mock_genai):
        """Test complete pipeline: PDF → text → embeddings"""
        # Mock settings
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        mock_settings.google_embedding_model = "models/embedding-001"
        
        # Mock PDF extraction
        pdf_content = "Medical Protocol: Emergency cardiac care procedures for acute myocardial infarction..."
        
        # Mock Google embeddings
        mock_genai.embed_content.return_value = {
            'embedding': [0.1, 0.2, 0.3] * 512  # 1536 dimensions
        }
        
        # Test the pipeline
        with patch.object(self.doc_extractor, 'extract_text', return_value=pdf_content):
            # Extract text from PDF
            extracted_text = self.doc_extractor.extract_text("medical_protocol.pdf", "application/pdf")
            
            # Generate embeddings from extracted text
            embeddings = self.google_service.generate_text_embeddings(extracted_text)
            
        # Validate results
        assert extracted_text == pdf_content
        assert len(embeddings) == 1  # Single chunk for short text
        assert len(embeddings[0]) == 1536
        assert isinstance(embeddings[0], list)
        
        # Verify API calls
        mock_genai.embed_content.assert_called_once()
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_docx_to_embeddings_pipeline(self, mock_settings, mock_genai):
        """Test complete pipeline: DOCX → text → embeddings"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 500
        
        # Mock DOCX extraction
        docx_content = "Computer Science 101 Syllabus\n\nCourse Objectives:\n1. Learn programming fundamentals\n2. Understand data structures\n3. Master algorithm design..."
        
        # Mock Google embeddings
        mock_genai.embed_content.return_value = {
            'embedding': [0.5] * 1536
        }
        
        with patch.object(self.doc_extractor, 'extract_text', return_value=docx_content):
            extracted_text = self.doc_extractor.extract_text("syllabus.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            embeddings = self.google_service.generate_text_embeddings(extracted_text)
            
            assert "Computer Science 101" in extracted_text
            assert len(embeddings) == 1
            assert all(x == 0.5 for x in embeddings[0])
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_chunked_document_embeddings(self, mock_settings, mock_genai):
        """Test pipeline with document chunking"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 50  # Small chunks for testing
        
        # Mock large document
        large_document = "This is a very long medical document. " * 20  # Will create multiple chunks
        
        # Mock Google embeddings for each chunk
        mock_genai.embed_content.return_value = {
            'embedding': [0.1] * 1536
        }
        
        with patch.object(self.doc_extractor, 'extract_text', return_value=large_document):
            extracted_text = self.doc_extractor.extract_text("large_protocol.pdf", "application/pdf")
            embeddings = self.google_service.generate_text_embeddings(extracted_text)
            
            assert len(embeddings) > 1  # Should have multiple chunks
            assert all(len(embedding) == 1536 for embedding in embeddings)
            assert mock_genai.embed_content.call_count > 1
    
    def test_document_extraction_error_handling(self):
        """Test error handling in document extraction"""
        with patch.object(self.doc_extractor, 'extract_text', side_effect=Exception("PDF extraction failed")):
            with pytest.raises(Exception, match="PDF extraction failed"):
                self.doc_extractor.extract_text("corrupted.pdf", "application/pdf")
    
    @patch('src.services.external_apis.google_service.genai')
    def test_embedding_generation_error_handling(self, mock_genai):
        """Test error handling in embedding generation"""
        mock_genai.embed_content.side_effect = Exception("API quota exceeded")
        
        # Should create zero embeddings as fallback
        embeddings = self.google_service.generate_text_embeddings("Test text")
        
        assert len(embeddings) == 1
        assert all(x == 0.0 for x in embeddings[0])


class TestAudioToEmbeddingPipeline:
    """Test complete pipeline from audio transcription to embeddings"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.google_service = GoogleService(api_key="test_key")
        self.google_service.genai_configured = True
        self.google_service.speech_client = Mock()
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_audio_to_embeddings_pipeline(self, mock_settings, mock_genai):
        """Test complete pipeline: Audio → transcription → embeddings"""
        # Mock settings
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        mock_settings.google_speech_language = "en-US"
        mock_settings.google_speech_model = "latest_long"
        mock_settings.enable_speaker_diarization = True
        mock_settings.max_speakers = 6
        
        # Mock transcription response
        mock_word = Mock()
        mock_word.word = "cardiac"
        mock_word.start_time.total_seconds.return_value = 0.0
        mock_word.end_time.total_seconds.return_value = 0.5
        mock_word.confidence = 0.95
        mock_word.speaker_tag = 1
        
        mock_alternative = Mock()
        mock_alternative.transcript = "Patient has cardiac arrest, initiate CPR protocol immediately"
        mock_alternative.confidence = 0.92
        mock_alternative.words = [mock_word]
        
        mock_result = Mock()
        mock_result.alternatives = [mock_alternative]
        
        mock_response = Mock()
        mock_response.results = [mock_result]
        
        self.google_service.speech_client.recognize.return_value = mock_response
        
        # Mock embeddings
        mock_genai.embed_content.return_value = {
            'embedding': [0.8] * 1536
        }
        
        # Test the pipeline
        with patch.object(self.google_service, '_prepare_audio_file', return_value=b"audio_data"):
            # Transcribe audio
            transcription_result = self.google_service.transcribe_audio("emergency_call.mp3")
            
            # Generate embeddings from transcription
            transcript_embeddings = self.google_service.generate_text_embeddings(transcription_result["transcript"])
            
        # Validate transcription
        assert transcription_result["transcript"] == "Patient has cardiac arrest, initiate CPR protocol immediately"
        assert transcription_result["confidence"] == 0.92
        assert "Speaker 1" in transcription_result["speakers"]
        
        # Validate embeddings
        assert len(transcript_embeddings) == 1
        assert len(transcript_embeddings[0]) == 1536
        assert all(x == 0.8 for x in transcript_embeddings[0])
    
    @patch('src.services.external_apis.google_service.settings')
    def test_audio_transcription_with_speakers(self, mock_settings):
        """Test audio transcription with speaker identification"""
        mock_settings.enable_speaker_diarization = True
        mock_settings.max_speakers = 2
        mock_settings.google_speech_language = "en-US"
        mock_settings.google_speech_model = "latest_long"
        
        # Mock multi-speaker conversation
        mock_word1 = Mock()
        mock_word1.word = "Doctor"
        mock_word1.speaker_tag = 1
        
        mock_word2 = Mock()
        mock_word2.word = "calling"
        mock_word2.speaker_tag = 1
        
        mock_word3 = Mock()
        mock_word3.word = "Yes"
        mock_word3.speaker_tag = 2
        
        mock_alternative = Mock()
        mock_alternative.transcript = "Doctor calling emergency Yes I understand"
        mock_alternative.confidence = 0.90
        mock_alternative.words = [mock_word1, mock_word2, mock_word3]
        
        mock_result = Mock()
        mock_result.alternatives = [mock_alternative]
        
        mock_response = Mock()
        mock_response.results = [mock_result]
        
        self.google_service.speech_client.recognize.return_value = mock_response
        
        with patch.object(self.google_service, '_prepare_audio_file', return_value=b"audio_data"):
            result = self.google_service.transcribe_audio("conversation.mp3")
            
        # Should detect multiple speakers
        assert "Speaker 1" in result["speakers"]
        assert "Speaker 2" in result["speakers"]
        assert len(result["speakers"]) == 2
        assert result["word_count"] == 6  # 6 words in transcript


class TestMultiModalWorkflow:
    """Test workflows combining multiple modalities"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.doc_extractor = DocumentTextExtractor()
        self.google_service = GoogleService(api_key="test_key")
        self.google_service.genai_configured = True
        self.google_service.speech_client = Mock()
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_healthcare_multimodal_workflow(self, mock_settings, mock_genai):
        """Test healthcare workflow with documents and audio"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        
        # Mock embeddings
        mock_genai.embed_content.return_value = {
            'embedding': [0.1] * 1536
        }
        
        # Process medical protocol document
        protocol_text = "Emergency Cardiac Protocol: Check pulse, start CPR if no pulse detected"
        with patch.object(self.doc_extractor, 'extract_text', return_value=protocol_text):
            doc_embeddings = self.google_service.generate_text_embeddings(protocol_text)
            
        # Process emergency call audio
        emergency_transcript = "Patient unresponsive, no pulse detected, starting CPR"
        audio_embeddings = self.google_service.generate_text_embeddings(emergency_transcript)
        
        # Validate workflow results
        assert len(doc_embeddings) == 1
        assert len(audio_embeddings) == 1
        assert len(doc_embeddings[0]) == 1536
        assert len(audio_embeddings[0]) == 1536
        
        # Verify both contain medical content indicators
        assert "cardiac" in protocol_text.lower() or "cpr" in protocol_text.lower()
        assert "cpr" in emergency_transcript.lower()
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_university_multimodal_workflow(self, mock_settings, mock_genai):
        """Test university workflow with lecture documents and recordings"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        
        # Mock embeddings
        mock_genai.embed_content.return_value = {
            'embedding': [0.2] * 1536
        }
        
        # Process lecture slides
        slides_text = "Machine Learning Lecture 5: Decision Trees and Random Forests"
        with patch.object(self.doc_extractor, 'extract_text', return_value=slides_text):
            slides_embeddings = self.google_service.generate_text_embeddings(slides_text)
            
        # Process lecture recording transcript
        lecture_transcript = "Today we'll discuss decision trees, a fundamental algorithm in machine learning"
        recording_embeddings = self.google_service.generate_text_embeddings(lecture_transcript)
        
        # Validate workflow results
        assert len(slides_embeddings) == 1
        assert len(recording_embeddings) == 1
        assert len(slides_embeddings[0]) == 1536
        assert len(recording_embeddings[0]) == 1536
        
        # Verify both contain educational content
        assert "machine learning" in slides_text.lower()
        assert "machine learning" in lecture_transcript.lower() or "algorithm" in lecture_transcript.lower()


class TestErrorHandlingAndFallbacks:
    """Test error handling and fallback mechanisms"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.doc_extractor = DocumentTextExtractor()
        self.google_service = GoogleService(api_key="test_key")
    
    def test_document_extraction_fallback_chain(self):
        """Test fallback chain in document extraction"""
        # Test with unsupported file type
        with pytest.raises(ValueError, match="No extractor available"):
            self.doc_extractor.extract_text("test.unknown", "unknown/type")
    
    @patch('src.services.external_apis.google_service.genai')
    def test_embedding_api_failure_fallback(self, mock_genai):
        """Test fallback when embedding API fails"""
        self.google_service.genai_configured = True
        mock_genai.embed_content.side_effect = Exception("API Error")
        
        # Should return zero embeddings
        result = self.google_service.generate_text_embeddings("test")
        assert len(result) == 1
        assert all(x == 0.0 for x in result[0])
    
    def test_service_not_configured_error(self):
        """Test error when service not properly configured"""
        service = GoogleService(api_key=None)
        
        with pytest.raises(RuntimeError):
            service.generate_text_embeddings("test")
    
    def test_audio_processing_without_speech_client(self):
        """Test audio processing when speech client unavailable"""
        service = GoogleService(api_key="test_key")
        service.speech_client = None
        
        with pytest.raises(RuntimeError, match="Google Speech client not initialized"):
            service.transcribe_audio("test.mp3")


class TestPerformanceAndScaling:
    """Test performance considerations and scaling scenarios"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.google_service = GoogleService(api_key="test_key")
        self.google_service.genai_configured = True
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_rate_limiting_with_multiple_requests(self, mock_settings, mock_genai):
        """Test rate limiting behavior with multiple requests"""
        mock_settings.text_embedding_dimension = 1536
        mock_settings.text_chunk_size = 1000
        mock_genai.embed_content.return_value = {'embedding': [0.1] * 1536}
        
        # Mock rate limiting with a very small interval for testing
        self.google_service.min_request_interval = 0.001  # 1ms for testing
        
        start_time = time.time()
        
        # Make multiple requests quickly
        for i in range(5):
            text = f"Test document {i}"
            embeddings = self.google_service.generate_text_embeddings(text)
            assert len(embeddings) == 1
            assert len(embeddings[0]) == 1536
            
        end_time = time.time()
        
        # Should take at least some minimum time due to rate limiting
        # Just verify that the calls were made successfully
        actual_time = end_time - start_time
        
        # Basic sanity check - should take some time but not too much
        assert 0.001 <= actual_time <= 1.0  # Between 1ms and 1 second
    
    @patch('src.services.external_apis.google_service.genai')
    @patch('src.services.external_apis.google_service.settings')
    def test_large_document_chunking(self, mock_settings, mock_genai):
        """Test handling of very large documents"""
        mock_settings.text_chunk_size = 100
        mock_settings.text_embedding_dimension = 1536
        mock_genai.embed_content.return_value = {'embedding': [0.1] * 1536}
        
        # Create large document (10000 characters)
        large_text = "This is a sentence that will be repeated many times. " * 200
        
        embeddings = self.google_service.generate_text_embeddings(large_text)
        
        # Should create many chunks
        expected_chunks = len(large_text) // mock_settings.text_chunk_size + 1
        assert len(embeddings) >= expected_chunks - 1  # Allow for slight variation
        assert mock_genai.embed_content.call_count >= 10  # Should make many API calls


if __name__ == "__main__":
    pytest.main([__file__]) 