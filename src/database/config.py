from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class OrganizationTypeEnum(str, Enum):
    HEALTHCARE = "healthcare"
    UNIVERSITY = "university"
    CORPORATE = "corporate"

class ContentTypeEnum(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    STRUCTURED_DATA = "structured_data"

class SecurityLevelEnum(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class OrganizationalMetadata(BaseModel):
    """Generic organizational metadata for any institution type"""
    department: str = Field(..., description="Department/Unit name")
    role: str = Field(..., description="User role (doctor, professor, student, staff, etc.)")
    organization_type: OrganizationTypeEnum = Field(default=OrganizationTypeEnum.HEALTHCARE)
    project_id: Optional[str] = Field(None, description="Project or study identifier")
    team_id: Optional[str] = Field(None, description="Team or group identifier")
    security_level: SecurityLevelEnum = Field(default=SecurityLevelEnum.INTERNAL)
    access_groups: List[str] = Field(default_factory=list, description="Access control groups")

class ContentMetadata(BaseModel):
    """Generic content metadata"""
    title: str = Field(..., description="Document/Content title")
    author: str = Field(..., description="Content creator")
    content_type: ContentTypeEnum = Field(..., description="Type of content")
    format: str = Field(..., description="File format (pdf, jpg, mp4, etc.)")
    creation_date: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0", description="Content version")
    language: str = Field(default="en", description="Content language")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    keywords: List[str] = Field(default_factory=list, description="Search keywords")

class ProcessingMetadata(BaseModel):
    """Metadata about AI processing"""
    api_used: str = Field(..., description="API service used for processing")
    processing_timestamp: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(ge=0.0, le=1.0, description="Processing confidence")
    model_version: Optional[str] = Field(None, description="AI model version")
    processing_duration: Optional[float] = Field(None, description="Processing time in seconds")
    error_log: Optional[str] = Field(None, description="Any processing errors")

class DomainSpecificMetadata(BaseModel):
    """Flexible domain-specific metadata"""
    specialty: Optional[str] = Field(None, description="Medical specialty, academic field, etc.")
    subject_area: Optional[str] = Field(None, description="Subject or topic area")
    priority: Optional[str] = Field(None, description="Priority level")
    status: Optional[str] = Field(None, description="Document status")
    related_entities: List[str] = Field(default_factory=list, description="Related people/cases/studies")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom domain fields")

class ComplianceMetadata(BaseModel):
    """Compliance and governance metadata"""
    compliance_frameworks: List[str] = Field(default_factory=list, description="HIPAA, FERPA, etc.")
    retention_date: Optional[datetime] = Field(None, description="Data retention until")
    approved_by: Optional[str] = Field(None, description="Approval authority")
    review_date: Optional[datetime] = Field(None, description="Next review date")
    access_log: List[str] = Field(default_factory=list, description="Access history")
    anonymized: bool = Field(default=False, description="Whether data is anonymized")

class DocumentMetadata(BaseModel):
    """Complete document metadata structure"""
    organizational: OrganizationalMetadata
    content: ContentMetadata
    processing: ProcessingMetadata
    domain_specific: DomainSpecificMetadata
    compliance: ComplianceMetadata
    relationships: Dict[str, List[str]] = Field(default_factory=dict, description="Related documents")

class AgenticDescription(BaseModel):
    """AI-readable collection description"""
    purpose: str = Field(..., description="What this collection stores")
    best_for: str = Field(..., description="Best use cases")
    typical_queries: List[str] = Field(..., description="Example queries")
    search_hints: List[str] = Field(default_factory=list, description="Search optimization hints")
    combine_with: List[str] = Field(default_factory=list, description="Other collections to combine")
    authority_level: str = Field(default="medium", description="Content authority level")

class CollectionConfig(BaseModel):
    """Configuration for a single collection"""
    name: str = Field(..., description="Collection name")
    description: str = Field(..., description="Human-readable description")
    vector_dim: int = Field(..., description="Vector embedding dimensions")
    content_types: List[ContentTypeEnum] = Field(..., description="Supported content types")
    organization_types: List[OrganizationTypeEnum] = Field(..., description="Target organizations")
    agentic_description: AgenticDescription
    enabled: bool = Field(default=True, description="Whether collection is active")
    max_entities: Optional[int] = Field(None, description="Maximum entities limit")
    index_config: Dict[str, Any] = Field(default_factory=dict, description="Index configuration")

class DatabaseConfig(BaseModel):
    """Complete database configuration"""
    host: str = Field(default="localhost", description="Milvus host")
    port: int = Field(default=19530, description="Milvus port")
    collections: Dict[str, CollectionConfig] = Field(..., description="Collection configurations")
    organization_type: OrganizationTypeEnum = Field(default=OrganizationTypeEnum.HEALTHCARE)
    default_security_level: SecurityLevelEnum = Field(default=SecurityLevelEnum.INTERNAL)
    enable_audit_logging: bool = Field(default=True, description="Enable audit trails")
    max_vector_dim: int = Field(default=2048, description="Maximum vector dimensions")

def get_default_collections_config() -> Dict[str, CollectionConfig]:
    """Get default collection configurations"""
    return {
        "documents": CollectionConfig(
            name="documents",
            description="Text documents, reports, protocols, research papers",
            vector_dim=1536,
            content_types=[ContentTypeEnum.DOCUMENT],
            organization_types=[OrganizationTypeEnum.HEALTHCARE, OrganizationTypeEnum.UNIVERSITY],
            agentic_description=AgenticDescription(
                purpose="Stores textual content including protocols, research papers, reports, and documentation",
                best_for="Procedural questions, policy lookups, research queries, documentation search",
                typical_queries=[
                    "What is the protocol for X?",
                    "How do we handle Y situation?",
                    "What are the guidelines for Z?",
                    "Find research about topic A"
                ],
                search_hints=["Use for policy and procedure queries", "Good for research literature"],
                combine_with=["images", "audio_recordings"],
                authority_level="high"
            ),
            index_config={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
        ),
        "images": CollectionConfig(
            name="images",
            description="Images, medical scans, diagrams, charts, visual content",
            vector_dim=512,
            content_types=[ContentTypeEnum.IMAGE],
            organization_types=[OrganizationTypeEnum.HEALTHCARE, OrganizationTypeEnum.UNIVERSITY],
            agentic_description=AgenticDescription(
                purpose="Stores visual content including medical images, diagrams, charts, and educational materials",
                best_for="Visual references, diagnostic support, educational content, case studies",
                typical_queries=[
                    "Show me similar images",
                    "What does condition X look like?",
                    "Find reference images for Y",
                    "Visual examples of Z"
                ],
                search_hints=["Use for visual similarity", "Good for diagnostic references"],
                combine_with=["documents", "video_content"],
                authority_level="medium"
            ),
            index_config={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 64}
            }
        ),
        "audio_recordings": CollectionConfig(
            name="audio_recordings",
            description="Audio recordings, transcripts, meetings, lectures, consultations",
            vector_dim=768,
            content_types=[ContentTypeEnum.AUDIO],
            organization_types=[OrganizationTypeEnum.HEALTHCARE, OrganizationTypeEnum.UNIVERSITY],
            agentic_description=AgenticDescription(
                purpose="Stores audio content including meeting transcripts, lectures, and consultation recordings",
                best_for="Historical context, meeting records, educational content, decision tracking",
                typical_queries=[
                    "What was decided about X?",
                    "Who mentioned Y in meetings?",
                    "Find discussions about Z",
                    "What training covered topic A?"
                ],
                search_hints=["Use for historical context", "Good for decision tracking"],
                combine_with=["documents", "video_content"],
                authority_level="medium"
            ),
            index_config={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
        ),
        "video_content": CollectionConfig(
            name="video_content",
            description="Video content, training materials, procedures, lectures",
            vector_dim=1024,
            content_types=[ContentTypeEnum.VIDEO],
            organization_types=[OrganizationTypeEnum.HEALTHCARE, OrganizationTypeEnum.UNIVERSITY],
            agentic_description=AgenticDescription(
                purpose="Stores video content including training materials, procedure demonstrations, and lectures",
                best_for="Training materials, procedure guidance, educational content, demonstrations",
                typical_queries=[
                    "Show me how to perform X",
                    "Training videos about Y",
                    "Procedure demonstrations for Z",
                    "Educational content on topic A"
                ],
                search_hints=["Use for training content", "Good for procedure guidance"],
                combine_with=["documents", "images", "audio_recordings"],
                authority_level="high"
            ),
            index_config={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
        )
    }

def get_default_database_config() -> DatabaseConfig:
    """Get default database configuration"""
    return DatabaseConfig(
        collections=get_default_collections_config(),
        organization_type=OrganizationTypeEnum.HEALTHCARE,
        default_security_level=SecurityLevelEnum.INTERNAL,
        enable_audit_logging=True
    )

def load_config_from_dict(config_dict: Dict[str, Any]) -> DatabaseConfig:
    """Load configuration from dictionary (for UI integration)"""
    return DatabaseConfig(**config_dict)

def save_config_to_dict(config: DatabaseConfig) -> Dict[str, Any]:
    """Save configuration to dictionary (for UI integration)"""
    return config.model_dump() 