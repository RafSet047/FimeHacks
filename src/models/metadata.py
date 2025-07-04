from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, field_validator, Field, ConfigDict
import json


class DocumentType(str, Enum):
    PROCEDURE = "procedure"
    PROTOCOL = "protocol"
    RESEARCH = "research"
    LECTURE = "lecture"
    MEETING = "meeting"
    REPORT = "report"
    POLICY = "policy"
    TRAINING = "training"
    PATIENT_RECORD = "patient_record"
    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    PRESENTATION = "presentation"
    MANUAL = "manual"
    OTHER = "other"


class ContentCategory(str, Enum):
    CLINICAL = "clinical"
    ACADEMIC = "academic"
    ADMINISTRATIVE = "administrative"
    RESEARCH = "research"
    TRAINING = "training"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    LEGAL = "legal"
    TECHNICAL = "technical"
    OTHER = "other"


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class AccessLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    CLASSIFIED = "classified"


class EmployeeRole(str, Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    ADMINISTRATOR = "administrator"
    RESEARCHER = "researcher"
    FACULTY = "faculty"
    STUDENT = "student"
    STAFF = "staff"
    MANAGER = "manager"
    DIRECTOR = "director"
    OTHER = "other"


class HealthcareMetadata(BaseModel):
    """Healthcare-specific metadata"""
    model_config = ConfigDict(use_enum_values=True)
    
    specialty: Optional[str] = None
    patient_id: Optional[str] = None
    physician_id: Optional[str] = None
    hospital_unit: Optional[str] = None
    procedure_code: Optional[str] = None
    diagnosis_code: Optional[str] = None
    treatment_date: Optional[datetime] = None
    urgency_level: Optional[str] = None


class UniversityMetadata(BaseModel):
    """University-specific metadata"""
    model_config = ConfigDict(use_enum_values=True)
    
    course_code: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    faculty_id: Optional[str] = None
    student_id: Optional[str] = None
    research_group: Optional[str] = None
    grant_number: Optional[str] = None
    publication_type: Optional[str] = None


class ProcessingMetadata(BaseModel):
    """Metadata related to file processing"""
    model_config = ConfigDict(use_enum_values=True)
    
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_duration_seconds: Optional[float] = None
    processing_steps: List[str] = Field(default_factory=list)
    apis_used: List[str] = Field(default_factory=list)
    content_extracted: bool = False
    embeddings_generated: bool = False
    error_occurred: bool = False
    error_message: Optional[str] = None


class SearchMetadata(BaseModel):
    """Metadata for search and indexing"""
    model_config = ConfigDict(use_enum_values=True)
    
    indexed_at: Optional[datetime] = None
    search_terms: List[str] = Field(default_factory=list)
    content_summary: Optional[str] = None
    key_phrases: List[str] = Field(default_factory=list)
    entities_extracted: List[str] = Field(default_factory=list)
    search_priority: int = 1


class FileMetadata(BaseModel):
    """
    Comprehensive metadata structure for files
    """
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )
    
    # Core organizational metadata
    department: str
    organization_unit: Optional[str] = None
    uploaded_by: str
    employee_role: EmployeeRole
    employee_id: Optional[str] = None
    
    # File classification
    document_type: DocumentType
    content_category: ContentCategory
    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    access_level: AccessLevel = AccessLevel.INTERNAL
    
    # Project and context
    project_name: Optional[str] = None
    project_id: Optional[str] = None
    case_id: Optional[str] = None
    reference_id: Optional[str] = None
    
    # Content descriptors
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    notes: Optional[str] = None
    
    # Domain-specific metadata
    domain_type: Optional[str] = None  # "healthcare", "university", etc.
    healthcare_metadata: Optional[HealthcareMetadata] = None
    university_metadata: Optional[UniversityMetadata] = None
    
    # Processing metadata
    processing_metadata: Optional[ProcessingMetadata] = None
    search_metadata: Optional[SearchMetadata] = None
    
    # Timestamps and versioning
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"
    
    # Custom fields for extensibility
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        return [tag.strip().lower() for tag in v if tag.strip()]
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        return [keyword.strip().lower() for keyword in v if keyword.strip()]
    
    @field_validator('healthcare_metadata')
    @classmethod
    def validate_healthcare_metadata(cls, v, info):
        if info.data.get('domain_type') == 'healthcare' and v is None:
            raise ValueError('Healthcare metadata is required when domain_type is healthcare')
        return v
    
    @field_validator('university_metadata')
    @classmethod
    def validate_university_metadata(cls, v, info):
        if info.data.get('domain_type') == 'university' and v is None:
            raise ValueError('University metadata is required when domain_type is university')
        return v

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = self.model_dump(exclude_none=True)
        
        # Convert datetime objects to ISO format strings and handle nested objects
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, BaseModel):
                # Handle nested BaseModel objects
                data[key] = value.model_dump(exclude_none=True)
            elif isinstance(value, dict):
                # Handle nested dictionaries
                data[key] = self._serialize_dict(value)
        
        return data
    
    def _serialize_dict(self, obj):
        """Recursively serialize dictionary objects"""
        if isinstance(obj, dict):
            return {k: self._serialize_dict(v) for k, v in obj.items()}
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, BaseModel):
            return obj.model_dump(exclude_none=True)
        else:
            return obj
    
    def to_json_string(self) -> str:
        return self.model_dump_json(exclude_none=True) 