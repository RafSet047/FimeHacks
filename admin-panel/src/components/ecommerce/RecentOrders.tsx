import Badge from "../ui/badge/Badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "../ui/table";

// Define the TypeScript interface for the table rows
interface Query {
  id: number; // Unique identifier for each query
  text: string; // Query text
  type: string; // Type of query (e.g., "Technical", "Policy", "Training")
  category: string; // Category of the query
  timestamp: string; // When the query was made
  status: "Answered" | "Pending" | "In Progress"; // Status of the query
  user: string; // User who made the query
}

// Define the table data using the interface
const tableData: Query[] = [
  {
    id: 1,
    text: "How to implement OAuth authentication?",
    type: "Technical Documentation",
    category: "Security",
    timestamp: "2 hours ago",
    status: "Answered",
    user: "John Doe",
  },
  {
    id: 2,
    text: "What is the company's remote work policy?",
    type: "Policy & Procedures",
    category: "HR",
    timestamp: "4 hours ago",
    status: "Pending",
    user: "Jane Smith",
  },
  {
    id: 3,
    text: "Steps for onboarding new team members",
    type: "Training Materials",
    category: "HR",
    timestamp: "1 day ago",
    status: "Answered",
    user: "Mike Johnson",
  },
  {
    id: 4,
    text: "Database performance optimization techniques",
    type: "Technical Documentation",
    category: "Database",
    timestamp: "2 days ago",
    status: "In Progress",
    user: "Sarah Wilson",
  },
  {
    id: 5,
    text: "Emergency contact procedures",
    type: "Policy & Procedures",
    category: "Safety",
    timestamp: "3 days ago",
    status: "Answered",
    user: "David Lee",
  },
];

export default function RecentOrders() {
  return (
    <div className='overflow-hidden rounded-2xl border border-gray-200 bg-white px-4 pb-3 pt-4 dark:border-gray-800 dark:bg-white/[0.03] sm:px-6'>
      <div className='flex flex-col gap-2 mb-4 sm:flex-row sm:items-center sm:justify-between'>
        <div>
          <h3 className='text-lg font-semibold text-gray-800 dark:text-white/90'>
            Recent Queries
          </h3>
        </div>

        <div className='flex items-center gap-3'>
          <button className='inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-theme-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 hover:text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/[0.03] dark:hover:text-gray-200'>
            <svg
              className='stroke-current fill-white dark:fill-gray-800'
              width='20'
              height='20'
              viewBox='0 0 20 20'
              fill='none'
              xmlns='http://www.w3.org/2000/svg'
            >
              <path
                d='M2.29004 5.90393H17.7067'
                stroke=''
                strokeWidth='1.5'
                strokeLinecap='round'
                strokeLinejoin='round'
              />
              <path
                d='M17.7075 14.0961H2.29085'
                stroke=''
                strokeWidth='1.5'
                strokeLinecap='round'
                strokeLinejoin='round'
              />
              <path
                d='M12.0826 3.33331C13.5024 3.33331 14.6534 4.48431 14.6534 5.90414C14.6534 7.32398 13.5024 8.47498 12.0826 8.47498C10.6627 8.47498 9.51172 7.32398 9.51172 5.90415C9.51172 4.48432 10.6627 3.33331 12.0826 3.33331Z'
                fill=''
                stroke=''
                strokeWidth='1.5'
              />
              <path
                d='M7.91745 11.525C6.49762 11.525 5.34662 12.676 5.34662 14.0959C5.34661 15.5157 6.49762 16.6667 7.91745 16.6667C9.33728 16.6667 10.4883 15.5157 10.4883 14.0959C10.4883 12.676 9.33728 11.525 7.91745 11.525Z'
                fill=''
                stroke=''
                strokeWidth='1.5'
              />
            </svg>
            Filter
          </button>
          <button className='inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-theme-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 hover:text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/[0.03] dark:hover:text-gray-200'>
            See all
          </button>
        </div>
      </div>
      <div className='max-w-full overflow-x-auto'>
        <Table>
          {/* Table Header */}
          <TableHeader className='border-gray-100 dark:border-gray-800 border-y'>
            <TableRow>
              <TableCell
                isHeader
                className='py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400'
              >
                Query
              </TableCell>
              <TableCell
                isHeader
                className='py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400'
              >
                Category
              </TableCell>
              <TableCell
                isHeader
                className='py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400'
              >
                Time
              </TableCell>
              <TableCell
                isHeader
                className='py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400'
              >
                Status
              </TableCell>
            </TableRow>
          </TableHeader>

          {/* Table Body */}

          <TableBody className='divide-y divide-gray-100 dark:divide-gray-800'>
            {tableData.map((query) => (
              <TableRow key={query.id} className=''>
                <TableCell className='py-3'>
                  <div className='flex items-center gap-3'>
                    <div className='h-[40px] w-[40px] overflow-hidden rounded-md bg-gray-100 dark:bg-gray-800 flex items-center justify-center'>
                      <svg
                        className='h-5 w-5 text-gray-500 dark:text-gray-400'
                        fill='none'
                        stroke='currentColor'
                        viewBox='0 0 24 24'
                      >
                        <path
                          strokeLinecap='round'
                          strokeLinejoin='round'
                          strokeWidth={2}
                          d='M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z'
                        />
                      </svg>
                    </div>
                    <div>
                      <p className='font-medium text-gray-800 text-theme-sm dark:text-white/90'>
                        {query.text}
                      </p>
                      <span className='text-gray-500 text-theme-xs dark:text-gray-400'>
                        {query.type}
                      </span>
                    </div>
                  </div>
                </TableCell>
                <TableCell className='py-3 text-gray-500 text-theme-sm dark:text-gray-400'>
                  {query.category}
                </TableCell>
                <TableCell className='py-3 text-gray-500 text-theme-sm dark:text-gray-400'>
                  {query.timestamp}
                </TableCell>
                <TableCell className='py-3 text-gray-500 text-theme-sm dark:text-gray-400'>
                  <Badge
                    size='sm'
                    color={
                      query.status === "Answered"
                        ? "success"
                        : query.status === "Pending"
                        ? "warning"
                        : "info"
                    }
                  >
                    {query.status}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
