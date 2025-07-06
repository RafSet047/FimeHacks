import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { MoreDotIcon } from "../../icons";
import { Dropdown } from "../ui/dropdown/Dropdown";
import { DropdownItem } from "../ui/dropdown/DropdownItem";

// Types for API responses
interface ProcessResponse {
  success: boolean;
  message: string;
  document_ids: string[];
  chunks_processed: number;
  embeddings_generated: number;
  ai_tags?: string[];
  analysis_time?: number;
}

interface UploadedFile {
  file: File;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  result?: ProcessResponse;
  error?: string;
  uploadTime?: number;
}

export default function DocumentUpload() {
  const [isOpen, setIsOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

      const uploadFileToAPI = async (file: File): Promise<ProcessResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    // Add metadata
    const metadata = {
      department: 'admin-panel',
      description: `Document uploaded via admin panel: ${file.name}`,
      project: 'knowledge-base',
      tags: ['admin-upload']
    };
    formData.append('metadata', JSON.stringify(metadata));

    // Determine the correct API URL based on environment
    const isDevelopment = window.location.port === '3001';
    const apiUrl = isDevelopment ? '/process' : '/process';

    console.log('Making API request to:', apiUrl);
    console.log('Environment:', isDevelopment ? 'development' : 'production');
    console.log('Current URL:', window.location.href);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });

      // Get response text first
      const responseText = await response.text();

      if (!response.ok) {
        // Try to parse error as JSON, fallback to text
        let errorMessage = `Upload failed: ${response.status} ${response.statusText}`;

        try {
          const errorData = JSON.parse(responseText);
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // If JSON parsing fails, use the text response or a default message
          errorMessage = responseText || errorMessage;
        }

        throw new Error(errorMessage);
      }

      // Try to parse success response as JSON
      try {
        return JSON.parse(responseText);
      } catch (parseError) {
        throw new Error(`Invalid response format: ${responseText.substring(0, 100)}...`);
      }

    } catch (error) {
      // Handle network errors and other exceptions
      if (error instanceof Error) {
        throw error;
      }
      throw new Error(`Network error: ${String(error)}`);
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    if (isUploading) return;

    setIsUploading(true);

    // Add files to state with initial status
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      file,
      status: 'uploading',
      progress: 0,
      uploadTime: Date.now()
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Process files one by one
    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];
      const fileIndex = uploadedFiles.length + i;

      try {
        // Update status to processing
        setUploadedFiles(prev =>
          prev.map((f, idx) =>
            idx === fileIndex
              ? { ...f, status: 'processing', progress: 50 }
              : f
          )
        );

        // Upload file
        const result = await uploadFileToAPI(file);

        // Update with success
        setUploadedFiles(prev =>
          prev.map((f, idx) =>
            idx === fileIndex
              ? { ...f, status: 'completed', progress: 100, result }
              : f
          )
        );

        console.log(`File ${file.name} processed successfully:`, result);

      } catch (error) {
        console.error(`Error processing ${file.name}:`, error);

        // Update with error
        setUploadedFiles(prev =>
          prev.map((f, idx) =>
            idx === fileIndex
              ? {
                  ...f,
                  status: 'error',
                  progress: 0,
                  error: error instanceof Error ? error.message : 'Upload failed'
                }
              : f
          )
        );
      }
    }

    setIsUploading(false);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [],
      "application/msword": [],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [],
      "text/plain": [],
      "text/csv": [],
      "application/vnd.ms-excel": [],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [],
      "text/markdown": [],
      "application/json": [],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "audio/wav": [".wav"],
      "audio/mpeg": [".mp3"],
    },
    disabled: isUploading,
  });

  function toggleDropdown() {
    setIsOpen(!isOpen);
  }

  function closeDropdown() {
    setIsOpen(false);
  }

  const clearFiles = () => {
    setUploadedFiles([]);
    closeDropdown();
  };

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading': return 'text-blue-600 dark:text-blue-400';
      case 'processing': return 'text-yellow-600 dark:text-yellow-400';
      case 'completed': return 'text-green-600 dark:text-green-400';
      case 'error': return 'text-red-600 dark:text-red-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return (
          <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      case 'completed':
        return (
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'error':
        return (
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className='rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-5 sm:p-6 h-full flex flex-col'>
      <div className='flex justify-between mb-6'>
        <div>
          <h3 className='text-lg font-semibold text-gray-800 dark:text-white/90'>
            Upload Documents
          </h3>
          <p className='mt-1 text-gray-500 text-theme-sm dark:text-gray-400'>
            Add new documents to your knowledge base
          </p>
        </div>
        <div className='relative inline-block'>
          <button className='dropdown-toggle' onClick={toggleDropdown}>
            <MoreDotIcon className='text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 size-6' />
          </button>
          <Dropdown
            isOpen={isOpen}
            onClose={closeDropdown}
            className='w-40 p-2'
          >
            <DropdownItem
              onItemClick={clearFiles}
              className='flex w-full font-normal text-left text-gray-500 rounded-lg hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300'
            >
              Clear All
            </DropdownItem>
            <DropdownItem
              onItemClick={closeDropdown}
              className='flex w-full font-normal text-left text-gray-500 rounded-lg hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300'
            >
              Settings
            </DropdownItem>
          </Dropdown>
        </div>
      </div>

      <div className='flex-1 flex flex-col'>
        <div
          {...getRootProps()}
          className={`transition border-2 border-dashed cursor-pointer rounded-xl p-12 text-center flex-1 flex flex-col justify-center min-h-[300px] ${
            isDragActive
              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
              : isUploading
              ? "border-gray-300 bg-gray-100 dark:border-gray-600 dark:bg-gray-800/50 cursor-not-allowed"
              : "border-gray-300 bg-gray-50 dark:border-gray-700 dark:bg-gray-900/50"
          }`}
        >
          <input {...getInputProps()} />

          <div className='flex flex-col items-center justify-center'>
            <div className='mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gray-200 text-gray-700 dark:bg-gray-800 dark:text-gray-400'>
              {isUploading ? (
                <svg className="animate-spin h-8 w-8" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <svg
                  className='h-8 w-8'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M12 6v6m0 0v6m0-6h6m-6 0H6'
                  />
                </svg>
              )}
            </div>

            <h4 className='mb-3 text-xl font-semibold text-gray-800 dark:text-white/90'>
              {isUploading
                ? "Processing files..."
                : isDragActive
                ? "Drop files here"
                : "Drag & drop files"
              }
            </h4>

            <p className='text-base text-gray-500 dark:text-gray-400 mb-6 max-w-sm'>
              PDF, DOC, DOCX, TXT, CSV, XLS, XLSX, MD, JSON, JPG, PNG, WAV, MP3 files supported
            </p>

            <span className={`text-base font-medium px-4 py-2 rounded-lg ${
              isUploading
                ? 'text-gray-500 bg-gray-200 dark:bg-gray-700 dark:text-gray-400'
                : 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30'
            }`}>
              {isUploading ? 'Processing...' : 'or browse files'}
            </span>
          </div>
        </div>

        {uploadedFiles.length > 0 && (
          <div className='mt-6 flex-shrink-0'>
            <h4 className='text-sm font-medium text-gray-800 dark:text-white/90 mb-3'>
              Upload Status ({uploadedFiles.length} files)
            </h4>
            <div className='space-y-3 max-h-64 overflow-y-auto'>
              {uploadedFiles.slice().reverse().map((uploadedFile, index) => (
                <div
                  key={index}
                  className='p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700'
                >
                  <div className='flex items-center justify-between mb-2'>
                    <div className='flex items-center'>
                      <div className={`h-8 w-8 rounded flex items-center justify-center mr-3 ${getStatusColor(uploadedFile.status)}`}>
                        {getStatusIcon(uploadedFile.status)}
                      </div>
                      <span className='text-sm font-medium text-gray-800 dark:text-white/90 truncate'>
                        {uploadedFile.file.name}
                      </span>
                    </div>
                    <span className='text-xs text-gray-500 dark:text-gray-400'>
                      {(uploadedFile.file.size / 1024).toFixed(1)} KB
                    </span>
                  </div>

                  {uploadedFile.status === 'error' && uploadedFile.error && (
                    <div className='mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded'>
                      <p className='text-sm text-red-600 dark:text-red-400'>{uploadedFile.error}</p>
                    </div>
                  )}

                  {uploadedFile.status === 'completed' && uploadedFile.result && (
                    <div className='mt-2 p-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded'>
                      <p className='text-sm text-green-600 dark:text-green-400 mb-1'>
                        ✓ Processed {uploadedFile.result.chunks_processed} chunks, {uploadedFile.result.embeddings_generated} embeddings
                      </p>
                      {uploadedFile.result.ai_tags && uploadedFile.result.ai_tags.length > 0 && (
                        <div className='flex flex-wrap gap-1 mt-2'>
                          {uploadedFile.result.ai_tags.map((tag, tagIndex) => (
                            <span
                              key={tagIndex}
                              className='px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs rounded'
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {(uploadedFile.status === 'uploading' || uploadedFile.status === 'processing') && (
                    <div className='mt-2'>
                      <div className='flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1'>
                        <span>{uploadedFile.status === 'uploading' ? 'Uploading...' : 'Processing...'}</span>
                        <span>{uploadedFile.progress}%</span>
                      </div>
                      <div className='w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2'>
                        <div
                          className='bg-blue-600 dark:bg-blue-400 h-2 rounded-full transition-all duration-300'
                          style={{ width: `${uploadedFile.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
