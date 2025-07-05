import { useState } from "react";
import { MoreDotIcon } from "../../icons";
import { Dropdown } from "../ui/dropdown/Dropdown";
import { DropdownItem } from "../ui/dropdown/DropdownItem";

export default function DemographicCard() {
  const [isOpen, setIsOpen] = useState(false);

  function toggleDropdown() {
    setIsOpen(!isOpen);
  }

  function closeDropdown() {
    setIsOpen(false);
  }
  return (
    <div className='rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] sm:p-6'>
      <div className='flex justify-between'>
        <div>
          <h3 className='text-lg font-semibold text-gray-800 dark:text-white/90'>
            Knowledge Categories
          </h3>
          <p className='mt-1 text-gray-500 text-theme-sm dark:text-gray-400'>
            Distribution of documents by category
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
              View More
            </DropdownItem>
            <DropdownItem
              onItemClick={closeDropdown}
              className='flex w-full font-normal text-left text-gray-500 rounded-lg hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300'
            >
              Delete
            </DropdownItem>
          </Dropdown>
        </div>
      </div>

      <div className='mt-6 space-y-4'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center'>
            <div className='w-3 h-3 bg-blue-500 rounded-full mr-3'></div>
            <span className='text-sm text-gray-600 dark:text-gray-400'>
              Technical Documentation
            </span>
          </div>
          <span className='text-sm font-medium text-gray-800 dark:text-white/90'>
            724 docs
          </span>
        </div>
        <div className='flex items-center justify-between'>
          <div className='flex items-center'>
            <div className='w-3 h-3 bg-green-500 rounded-full mr-3'></div>
            <span className='text-sm text-gray-600 dark:text-gray-400'>
              Training Materials
            </span>
          </div>
          <span className='text-sm font-medium text-gray-800 dark:text-white/90'>
            589 docs
          </span>
        </div>
        <div className='flex items-center justify-between'>
          <div className='flex items-center'>
            <div className='w-3 h-3 bg-purple-500 rounded-full mr-3'></div>
            <span className='text-sm text-gray-600 dark:text-gray-400'>
              Policies & Procedures
            </span>
          </div>
          <span className='text-sm font-medium text-gray-800 dark:text-white/90'>
            412 docs
          </span>
        </div>
        <div className='flex items-center justify-between'>
          <div className='flex items-center'>
            <div className='w-3 h-3 bg-orange-500 rounded-full mr-3'></div>
            <span className='text-sm text-gray-600 dark:text-gray-400'>
              Research Reports
            </span>
          </div>
          <span className='text-sm font-medium text-gray-800 dark:text-white/90'>
            298 docs
          </span>
        </div>
        <div className='flex items-center justify-between'>
          <div className='flex items-center'>
            <div className='w-3 h-3 bg-red-500 rounded-full mr-3'></div>
            <span className='text-sm text-gray-600 dark:text-gray-400'>
              Meeting Notes
            </span>
          </div>
          <span className='text-sm font-medium text-gray-800 dark:text-white/90'>
            824 docs
          </span>
        </div>
      </div>
    </div>
  );
}
