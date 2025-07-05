import { useState } from "react";
import PageBreadcrumb from "../components/common/PageBreadCrumb";
import PageMeta from "../components/common/PageMeta";
import DocumentUpload from "../components/ecommerce/DocumentUpload";
import { DocsIcon, FolderIcon } from "../icons";

// Custom icons as inline SVG components
const SearchIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill='none'
    stroke='currentColor'
    viewBox='0 0 24 24'
  >
    <path
      strokeLinecap='round'
      strokeLinejoin='round'
      strokeWidth={2}
      d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
    />
  </svg>
);

const TagIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill='none'
    stroke='currentColor'
    viewBox='0 0 24 24'
  >
    <path
      strokeLinecap='round'
      strokeLinejoin='round'
      strokeWidth={2}
      d='M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z'
    />
  </svg>
);

interface Document {
  id: string;
  title: string;
  type: string;
  category: string;
  lastModified: string;
  size: string;
  tags: string[];
}

interface Category {
  name: string;
  count: number;
  icon: React.ReactNode;
  color: string;
}

export default function KnowledgeBase() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  // Mock data - in a real app, this would come from an API
  const recentDocuments: Document[] = [
    {
      id: "1",
      title: "Company Policy Manual",
      type: "PDF",
      category: "Policies",
      lastModified: "2024-01-15",
      size: "2.5 MB",
      tags: ["policy", "manual", "hr"],
    },
    {
      id: "2",
      title: "Technical Documentation",
      type: "DOCX",
      category: "Technical",
      lastModified: "2024-01-14",
      size: "1.8 MB",
      tags: ["technical", "documentation", "api"],
    },
    {
      id: "3",
      title: "Financial Report Q4 2023",
      type: "XLSX",
      category: "Finance",
      lastModified: "2024-01-13",
      size: "3.2 MB",
      tags: ["finance", "report", "quarterly"],
    },
    {
      id: "4",
      title: "Marketing Strategy 2024",
      type: "PDF",
      category: "Marketing",
      lastModified: "2024-01-12",
      size: "4.1 MB",
      tags: ["marketing", "strategy", "2024"],
    },
    {
      id: "5",
      title: "Employee Handbook",
      type: "PDF",
      category: "HR",
      lastModified: "2024-01-11",
      size: "1.9 MB",
      tags: ["handbook", "employee", "hr"],
    },
  ];

  const categories: Category[] = [
    {
      name: "All Documents",
      count: 247,
      icon: <DocsIcon className='w-5 h-5' />,
      color: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
    },
    {
      name: "Policies",
      count: 42,
      icon: <FolderIcon className='w-5 h-5' />,
      color:
        "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400",
    },
    {
      name: "Technical",
      count: 89,
      icon: <FolderIcon className='w-5 h-5' />,
      color:
        "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400",
    },
    {
      name: "Finance",
      count: 56,
      icon: <FolderIcon className='w-5 h-5' />,
      color:
        "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400",
    },
    {
      name: "Marketing",
      count: 34,
      icon: <FolderIcon className='w-5 h-5' />,
      color: "bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400",
    },
    {
      name: "HR",
      count: 26,
      icon: <FolderIcon className='w-5 h-5' />,
      color:
        "bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400",
    },
  ];

  const stats = [
    {
      label: "Total Documents",
      value: "247",
      change: "+12%",
      isPositive: true,
    },
    { label: "Storage Used", value: "2.4 GB", change: "+5%", isPositive: true },
    {
      label: "Searches This Month",
      value: "1,249",
      change: "+23%",
      isPositive: true,
    },
    { label: "Downloads", value: "456", change: "-2%", isPositive: false },
  ];

  const filteredDocuments = recentDocuments.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.tags.some((tag) =>
        tag.toLowerCase().includes(searchQuery.toLowerCase()),
      );
    const matchesCategory =
      selectedCategory === "all" ||
      doc.category.toLowerCase() === selectedCategory.toLowerCase();
    return matchesSearch && matchesCategory;
  });

  const getFileTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf":
        return "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400";
      case "docx":
      case "doc":
        return "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400";
      case "xlsx":
      case "xls":
        return "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400";
      case "txt":
        return "bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400";
      default:
        return "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400";
    }
  };

  return (
    <>
      <PageMeta
        title='Knowledge Base | Cerebryx - Admin Dashboard'
        description="Manage and access your organization's knowledge base documents"
      />
      <PageBreadcrumb pageTitle='Knowledge Base' />

      <div className='space-y-4 md:space-y-6'>
        {/* Statistics Cards */}
        <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6'>
          {stats.map((stat, index) => (
            <div
              key={index}
              className='rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-6'
            >
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm text-gray-500 dark:text-gray-400'>
                    {stat.label}
                  </p>
                  <p className='text-2xl font-semibold text-gray-800 dark:text-white/90 mt-1'>
                    {stat.value}
                  </p>
                  <p
                    className={`text-sm mt-1 ${
                      stat.isPositive
                        ? "text-green-600 dark:text-green-400"
                        : "text-red-600 dark:text-red-400"
                    }`}
                  >
                    {stat.change} from last month
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Search and Upload Section */}
        <div className='grid grid-cols-12 gap-4 md:gap-6'>
          <div className='col-span-12 xl:col-span-8'>
            <div className='rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-6'>
              <div className='flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-6'>
                <div>
                  <h3 className='text-lg font-semibold text-gray-800 dark:text-white/90'>
                    Search Knowledge Base
                  </h3>
                  <p className='text-sm text-gray-500 dark:text-gray-400 mt-1'>
                    Find documents, policies, and resources
                  </p>
                </div>
              </div>

              {/* Search Bar */}
              <div className='relative mb-6'>
                <SearchIcon className='absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5' />
                <input
                  type='text'
                  placeholder='Search documents, tags, or content...'
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className='w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500'
                />
              </div>

              {/* Category Filter */}
              <div className='flex flex-wrap gap-2 mb-6'>
                {categories.map((category) => (
                  <button
                    key={category.name}
                    onClick={() =>
                      setSelectedCategory(
                        category.name === "All Documents"
                          ? "all"
                          : category.name,
                      )
                    }
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                      (selectedCategory === "all" &&
                        category.name === "All Documents") ||
                      selectedCategory.toLowerCase() ===
                        category.name.toLowerCase()
                        ? category.color
                        : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
                    }`}
                  >
                    {category.icon}
                    <span className='text-sm font-medium'>{category.name}</span>
                    <span className='text-xs opacity-75'>
                      ({category.count})
                    </span>
                  </button>
                ))}
              </div>

              {/* Recent Documents */}
              <div>
                <h4 className='text-md font-semibold text-gray-800 dark:text-white/90 mb-4'>
                  Recent Documents ({filteredDocuments.length})
                </h4>
                <div className='space-y-3'>
                  {filteredDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className='flex items-center justify-between p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer'
                    >
                      <div className='flex items-center gap-4'>
                        <div
                          className={`px-2 py-1 rounded text-xs font-medium ${getFileTypeColor(
                            doc.type,
                          )}`}
                        >
                          {doc.type}
                        </div>
                        <div>
                          <h5 className='font-medium text-gray-800 dark:text-white/90'>
                            {doc.title}
                          </h5>
                          <p className='text-sm text-gray-500 dark:text-gray-400'>
                            {doc.category} • {doc.lastModified} • {doc.size}
                          </p>
                          <div className='flex flex-wrap gap-1 mt-2'>
                            {doc.tags.map((tag, index) => (
                              <span
                                key={index}
                                className='inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs rounded'
                              >
                                <TagIcon className='w-3 h-3' />
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <button className='text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'>
                        <svg
                          className='w-5 h-5'
                          fill='none'
                          stroke='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path
                            strokeLinecap='round'
                            strokeLinejoin='round'
                            strokeWidth={2}
                            d='M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z'
                          />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className='col-span-12 xl:col-span-4'>
            <DocumentUpload />
          </div>
        </div>

        {/* Quick Actions */}
        <div className='rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] p-6'>
          <h3 className='text-lg font-semibold text-gray-800 dark:text-white/90 mb-4'>
            Quick Actions
          </h3>
          <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4'>
            <button className='flex items-center gap-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors'>
              <div className='w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center'>
                <SearchIcon className='w-5 h-5 text-blue-600 dark:text-blue-400' />
              </div>
              <div className='text-left'>
                <p className='font-medium text-gray-800 dark:text-white/90'>
                  Advanced Search
                </p>
                <p className='text-sm text-gray-500 dark:text-gray-400'>
                  Search with filters
                </p>
              </div>
            </button>

            <button className='flex items-center gap-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors'>
              <div className='w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center'>
                <FolderIcon className='w-5 h-5 text-green-600 dark:text-green-400' />
              </div>
              <div className='text-left'>
                <p className='font-medium text-gray-800 dark:text-white/90'>
                  Browse Categories
                </p>
                <p className='text-sm text-gray-500 dark:text-gray-400'>
                  View by category
                </p>
              </div>
            </button>

            <button className='flex items-center gap-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors'>
              <div className='w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center'>
                <TagIcon className='w-5 h-5 text-purple-600 dark:text-purple-400' />
              </div>
              <div className='text-left'>
                <p className='font-medium text-gray-800 dark:text-white/90'>
                  Manage Tags
                </p>
                <p className='text-sm text-gray-500 dark:text-gray-400'>
                  Organize content
                </p>
              </div>
            </button>

            <button className='flex items-center gap-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors'>
              <div className='w-10 h-10 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center'>
                <DocsIcon className='w-5 h-5 text-yellow-600 dark:text-yellow-400' />
              </div>
              <div className='text-left'>
                <p className='font-medium text-gray-800 dark:text-white/90'>
                  Recent Activity
                </p>
                <p className='text-sm text-gray-500 dark:text-gray-400'>
                  View recent changes
                </p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
