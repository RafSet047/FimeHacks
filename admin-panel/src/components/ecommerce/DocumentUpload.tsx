import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { MoreDotIcon } from "../../icons";
import { Dropdown } from "../ui/dropdown/Dropdown";
import { DropdownItem } from "../ui/dropdown/DropdownItem";

export default function DocumentUpload() {
  const [isOpen, setIsOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  const onDrop = (acceptedFiles: File[]) => {
    setUploadedFiles((prev) => [...prev, ...acceptedFiles]);
    console.log("Files uploaded:", acceptedFiles);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [],
      "application/msword": [],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [],
      "text/plain": [],
      "text/csv": [],
      "application/vnd.ms-excel": [],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [],
    },
  });

  function toggleDropdown() {
    setIsOpen(!isOpen);
  }

  function closeDropdown() {
    setIsOpen(false);
  }

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
              onItemClick={closeDropdown}
              className='flex w-full font-normal text-left text-gray-500 rounded-lg hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300'
            >
              View All
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
              : "border-gray-300 bg-gray-50 dark:border-gray-700 dark:bg-gray-900/50"
          }`}
        >
          <input {...getInputProps()} />

          <div className='flex flex-col items-center justify-center'>
            <div className='mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-gray-200 text-gray-700 dark:bg-gray-800 dark:text-gray-400'>
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
            </div>

            <h4 className='mb-3 text-xl font-semibold text-gray-800 dark:text-white/90'>
              {isDragActive ? "Drop files here" : "Drag & drop files"}
            </h4>

            <p className='text-base text-gray-500 dark:text-gray-400 mb-6 max-w-sm'>
              PDF, DOC, DOCX, TXT, CSV, XLS, XLSX files supported
            </p>

            <span className='text-base font-medium text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30 px-4 py-2 rounded-lg'>
              or browse files
            </span>
          </div>
        </div>

        {uploadedFiles.length > 0 && (
          <div className='mt-6 flex-shrink-0'>
            <h4 className='text-sm font-medium text-gray-800 dark:text-white/90 mb-3'>
              Recent Uploads ({uploadedFiles.length})
            </h4>
            <div className='space-y-2 max-h-32 overflow-y-auto'>
              {uploadedFiles.slice(-3).map((file, index) => (
                <div
                  key={index}
                  className='flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg'
                >
                  <div className='flex items-center'>
                    <div className='h-10 w-10 rounded bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center mr-3'>
                      <svg
                        className='h-5 w-5 text-blue-600 dark:text-blue-400'
                        fill='currentColor'
                        viewBox='0 0 20 20'
                      >
                        <path
                          fillRule='evenodd'
                          d='M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z'
                          clipRule='evenodd'
                        />
                      </svg>
                    </div>
                    <span className='text-sm text-gray-800 dark:text-white/90 truncate'>
                      {file.name}
                    </span>
                  </div>
                  <span className='text-xs text-gray-500 dark:text-gray-400'>
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
