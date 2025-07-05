# File Upload API Examples

## Basic Upload
```bash
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_file.txt" \
  -F 'metadata={"department": "demo", "description": "Test upload"}'
```

## Valid Enum Values

### Document Types
- `"procedure"` - Medical procedures
- `"protocol"` - Standard protocols
- `"research"` - Research documents
- `"lecture"` - Educational lectures
- `"meeting"` - Meeting notes
- `"report"` - Reports
- `"policy"` - Policy documents
- `"training"` - Training materials
- `"patient_record"` - Patient records
- `"lab_result"` - Laboratory results
- `"imaging"` - Medical imaging
- `"presentation"` - Presentations
- `"manual"` - Manuals
- `"other"` - Other documents

### Content Categories
- `"clinical"` - Clinical content
- `"academic"` - Academic content
- `"administrative"` - Administrative content
- `"research"` - Research content
- `"training"` - Training content
- `"operational"` - Operational content
- `"financial"` - Financial content
- `"legal"` - Legal content
- `"technical"` - Technical content
- `"other"` - Other content

### Priority Levels
- `"low"` - Low priority
- `"medium"` - Medium priority
- `"high"` - High priority
- `"urgent"` - Urgent priority
- `"critical"` - Critical priority

### Access Levels
- `"public"` - Public access
- `"internal"` - Internal access
- `"restricted"` - Restricted access
- `"confidential"` - Confidential access
- `"classified"` - Classified access

### Employee Roles
- `"doctor"` - Doctor
- `"nurse"` - Nurse
- `"technician"` - Technician
- `"administrator"` - Administrator
- `"researcher"` - Researcher
- `"faculty"` - Faculty
- `"student"` - Student
- `"staff"` - Staff
- `"manager"` - Manager
- `"director"` - Director
- `"other"` - Other roles

## Example Upload Commands

### Research Document
```bash
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@research_paper.pdf" \
  -F 'metadata={"department": "research", "description": "Research paper on AI", "document_type": "research", "content_category": "research", "priority_level": "high", "access_level": "internal", "employee_role": "researcher", "uploaded_by": "john.doe", "tags": ["AI", "research", "paper"]}'
```

### Training Manual
```bash
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@training_manual.docx" \
  -F 'metadata={"department": "training", "description": "Employee training manual", "document_type": "training", "content_category": "training", "priority_level": "medium", "access_level": "internal", "employee_role": "administrator", "uploaded_by": "hr.team"}'
```

### Clinical Report
```bash
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@clinical_report.pdf" \
  -F 'metadata={"department": "medical", "description": "Patient clinical report", "document_type": "patient_record", "content_category": "clinical", "priority_level": "high", "access_level": "confidential", "employee_role": "doctor", "uploaded_by": "dr.smith"}'
```

### Meeting Notes
```bash
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@meeting_notes.txt" \
  -F 'metadata={"department": "management", "description": "Weekly team meeting notes", "document_type": "meeting", "content_category": "administrative", "priority_level": "medium", "access_level": "internal", "employee_role": "manager", "uploaded_by": "team.lead"}'
```

### Technical Manual
```bash
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@technical_manual.pdf" \
  -F 'metadata={"department": "engineering", "description": "Technical system manual", "document_type": "manual", "content_category": "technical", "priority_level": "high", "access_level": "internal", "employee_role": "technician", "uploaded_by": "engineering.team"}'
```

## Quick Test
```bash
./test_upload.sh
```

## Expected Response
```json
{
  "success": true,
  "message": "File uploaded and processed: X chunks with AI analysis, stored X documents",
  "document_ids": ["doc1", "doc2", "doc3"],
  "chunks_processed": 3,
  "embeddings_generated": 3,
  "ai_tags": ["technical", "documentation"],
  "analysis_time": 1.25,
  "file_id": "uuid-here",
  "filename": "test_document.txt",
  "file_size": 1024,
  "file_type": "txt",
  "database_id": 1,
  "department": "demo",
  "project": "hackathon"
}
``` 