import os
from typing import List, Dict, Any
from pathlib import Path

# LangChain imports
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Audio processing imports
import speech_recognition as sr
from pydub import AudioSegment
import tempfile


class FileType:
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    XLSX = "xlsx"
    PPTX = "pptx"
    MP3 = "mp3"
    WAV = "wav"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"

PROCESSOR_MAP = {
    FileType.PDF: "pdf_processor",
    FileType.DOCX: "docx_processor",
    FileType.TXT: "txt_processor",
    FileType.CSV: "csv_processor",
    FileType.XLSX: "xlsx_processor",
    FileType.PPTX: "pptx_processor",
    FileType.MP3: "audio_processor",
    FileType.WAV: "audio_processor",
    FileType.M4A: "audio_processor",
    FileType.FLAC: "audio_processor",
    FileType.OGG: "audio_processor"
}

class Processor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.recognizer = sr.Recognizer()
    
    def process_input(self, file_path: str) -> List[Document]:
        """
        Process input file and return list of LangChain Documents
        """
        file_type = self.get_file_type(file_path)
        
        if file_type == FileType.PDF:
            return self.process_pdf(file_path)
        elif file_type == FileType.CSV:
            return self.process_csv(file_path)
        elif file_type == FileType.TXT:
            return self.process_text(file_path)
        elif file_type == FileType.DOCX:
            return self.process_docx(file_path)
        elif file_type == FileType.XLSX:
            return self.process_xlsx(file_path)
        elif file_type == FileType.PPTX:
            return self.process_pptx(file_path)
        elif file_type in [FileType.MP3, FileType.WAV, FileType.M4A, FileType.FLAC, FileType.OGG]:
            return self.process_audio(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def get_file_type(self, file_path: str) -> str:
        """
        Determine file type based on file extension
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return FileType.PDF
        elif file_extension == '.csv':
            return FileType.CSV
        elif file_extension == '.txt':
            return FileType.TXT
        elif file_extension == '.docx':
            return FileType.DOCX
        elif file_extension == '.xlsx':
            return FileType.XLSX
        elif file_extension == '.pptx':
            return FileType.PPTX
        elif file_extension == '.mp3':
            return FileType.MP3
        elif file_extension == '.wav':
            return FileType.WAV
        elif file_extension == '.m4a':
            return FileType.M4A
        elif file_extension == '.flac':
            return FileType.FLAC
        elif file_extension == '.ogg':
            return FileType.OGG
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """
        Process PDF file using LangChain PyPDFLoader
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            raise Exception(f"Error processing PDF file {file_path}: {str(e)}")
    
    def process_csv(self, file_path: str) -> List[Document]:
        """
        Process CSV file using LangChain CSVLoader
        """
        try:
            loader = CSVLoader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            raise Exception(f"Error processing CSV file {file_path}: {str(e)}")
    
    def process_text(self, file_path: str) -> List[Document]:
        """
        Process text file using LangChain TextLoader
        """
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            raise Exception(f"Error processing text file {file_path}: {str(e)}")
    
    def process_docx(self, file_path: str) -> List[Document]:
        """
        Process DOCX file using LangChain Docx2txtLoader
        """
        try:
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            raise Exception(f"Error processing DOCX file {file_path}: {str(e)}")
    
    def process_xlsx(self, file_path: str) -> List[Document]:
        """
        Process XLSX file by converting to CSV first
        """
        try:
            import pandas as pd
            # Read Excel file and convert to CSV format
            df = pd.read_excel(file_path)
            csv_content = df.to_csv(index=False)
            
            # Create a document from the CSV content
            document = Document(
                page_content=csv_content,
                metadata={"source": file_path, "file_type": "xlsx"}
            )
            return self.text_splitter.split_documents([document])
        except Exception as e:
            raise Exception(f"Error processing XLSX file {file_path}: {str(e)}")
    
    def process_pptx(self, file_path: str) -> List[Document]:
        """
        Process PPTX file using LangChain UnstructuredPowerPointLoader
        """
        try:
            loader = UnstructuredPowerPointLoader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            raise Exception(f"Error processing PPTX file {file_path}: {str(e)}")
    
    def process_audio(self, file_path: str) -> List[Document]:
        """
        Process audio file by converting to text using speech recognition
        """
        try:
            # Convert audio to WAV format if needed
            audio_path = self._convert_audio_to_wav(file_path)
            
            # Perform speech recognition
            transcription = self._transcribe_audio(audio_path)
            
            # Clean up temporary file if it was created
            if audio_path != file_path:
                os.remove(audio_path)
            
            # Create document from transcription
            document = Document(
                page_content=transcription,
                metadata={"source": file_path, "file_type": "audio", "transcription": True}
            )
            
            return self.text_splitter.split_documents([document])
            
        except Exception as e:
            raise Exception(f"Error processing audio file {file_path}: {str(e)}")
    
    def _convert_audio_to_wav(self, file_path: str) -> str:
        """
        Convert audio file to WAV format for speech recognition
        """
        file_extension = Path(file_path).suffix.lower()
        
        # If already WAV, return as is
        if file_extension == '.wav':
            return file_path
        
        try:
            # Load audio file
            if file_extension == '.mp3':
                audio = AudioSegment.from_mp3(file_path)
            elif file_extension == '.m4a':
                audio = AudioSegment.from_file(file_path, format="m4a")
            elif file_extension == '.flac':
                audio = AudioSegment.from_file(file_path, format="flac")
            elif file_extension == '.ogg':
                audio = AudioSegment.from_file(file_path, format="ogg")
            else:
                raise ValueError(f"Unsupported audio format: {file_extension}")
            
            # Create temporary WAV file
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio.export(temp_wav.name, format="wav")
            
            return temp_wav.name
            
        except Exception as e:
            raise Exception(f"Error converting audio to WAV: {str(e)}")
    
    def _transcribe_audio(self, wav_file_path: str) -> str:
        """
        Transcribe WAV audio file to text using speech recognition
        """
        try:
            with sr.AudioFile(wav_file_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                
                # Record audio
                audio = self.recognizer.record(source)
                
                # Perform speech recognition
                transcription = self.recognizer.recognize_google(audio)
                
                return transcription
                
        except sr.UnknownValueError:
            raise Exception("Speech recognition could not understand the audio")
        except sr.RequestError as e:
            raise Exception(f"Could not request results from speech recognition service: {str(e)}")
        except Exception as e:
            raise Exception(f"Error during transcription: {str(e)}")
    
    def get_document_metadata(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Extract metadata from processed documents
        """
        if not documents:
            return {}
        
        total_chunks = len(documents)
        total_characters = sum(len(doc.page_content) for doc in documents)
        
        # Get unique sources
        sources = list(set(doc.metadata.get('source', 'unknown') for doc in documents))
        
        return {
            'total_chunks': total_chunks,
            'total_characters': total_characters,
            'sources': sources,
            'average_chunk_size': total_characters / total_chunks if total_chunks > 0 else 0
        }
