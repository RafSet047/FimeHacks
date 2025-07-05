import {
  AlertIcon,
  ArrowUpIcon,
  BoltIcon,
  CheckCircleIcon,
  PlugInIcon,
  TaskIcon,
  TimeIcon,
} from "../../icons";
import Badge from "../ui/badge/Badge";

export default function BusinessImpactMetrics() {
  return (
    <div className='grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 md:gap-4'>
      {/* <!-- Bottlenecks Resolved --> */}
      <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5 min-h-[140px] flex flex-col justify-between'>
        <div className='flex items-center justify-center w-10 h-10 bg-red-100 rounded-xl dark:bg-red-800/20'>
          <TaskIcon className='text-red-600 size-5 dark:text-red-400' />
        </div>
        <div className='flex items-end justify-between mt-4'>
          <div>
            <span className='text-sm text-gray-500 dark:text-gray-400'>
              Bottlenecks Resolved
            </span>
            <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
              142
            </h4>
            <span className='text-xs text-gray-400 dark:text-gray-500'>
              this month
            </span>
          </div>
          <Badge color='success'>
            <ArrowUpIcon />
            18%
          </Badge>
        </div>
        <p className='text-xs text-gray-500 dark:text-gray-400 mt-2'>
          142 tasks auto-closed • View log
        </p>
      </div>

      {/* <!-- Hours Saved for Staff --> */}
      <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5 min-h-[140px] flex flex-col justify-between'>
        <div className='flex items-center justify-center w-10 h-10 bg-blue-100 rounded-xl dark:bg-blue-800/20'>
          <TimeIcon className='text-blue-600 size-5 dark:text-blue-400' />
        </div>
        <div className='flex items-end justify-between mt-4'>
          <div>
            <span className='text-sm text-gray-500 dark:text-gray-400'>
              Hours Saved for Staff
            </span>
            <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
              513h
            </h4>
            <span className='text-xs text-gray-400 dark:text-gray-500'>
              auto-logged
            </span>
          </div>
          <Badge color='success'>
            <ArrowUpIcon />
            12%
          </Badge>
        </div>
        <p className='text-xs text-gray-500 dark:text-gray-400 mt-2'>
          513 h = one full staff year this quarter
        </p>
      </div>

      {/* <!-- High-Risk Events Averted --> */}
      <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5 min-h-[140px] flex flex-col justify-between'>
        <div className='flex items-center justify-center w-10 h-10 bg-yellow-100 rounded-xl dark:bg-yellow-800/20'>
          <AlertIcon className='text-yellow-600 size-5 dark:text-yellow-400' />
        </div>
        <div className='flex items-end justify-between mt-4'>
          <div>
            <span className='text-sm text-gray-500 dark:text-gray-400'>
              High-Risk Events Averted
            </span>
            <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
              7
            </h4>
            <span className='text-xs text-gray-400 dark:text-gray-500'>
              critical alerts
            </span>
          </div>
          <Badge color='success'>
            <ArrowUpIcon />
            40%
          </Badge>
        </div>
        <p className='text-xs text-gray-500 dark:text-gray-400 mt-2'>
          Handled before SLA breach
        </p>
      </div>

      {/* <!-- Answer Accuracy --> */}
      <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5 min-h-[140px] flex flex-col justify-between'>
        <div className='flex items-center justify-center w-10 h-10 bg-purple-100 rounded-xl dark:bg-purple-800/20'>
          <CheckCircleIcon className='text-purple-600 size-5 dark:text-purple-400' />
        </div>
        <div className='flex items-end justify-between mt-4'>
          <div>
            <span className='text-sm text-gray-500 dark:text-gray-400'>
              Answer Accuracy
            </span>
            <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
              92%
            </h4>
            <span className='text-xs text-gray-400 dark:text-gray-500'>
              confirmed helpful
            </span>
          </div>
          <Badge color='success'>
            <ArrowUpIcon />
            4%
          </Badge>
        </div>
        <p className='text-xs text-gray-500 dark:text-gray-400 mt-2'>
          Thumb-ups ÷ total responses
        </p>
      </div>

      {/* <!-- Data Freshness --> */}
      <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5 min-h-[140px] flex flex-col justify-between'>
        <div className='flex items-center justify-center w-10 h-10 bg-indigo-100 rounded-xl dark:bg-indigo-800/20'>
          <BoltIcon className='text-indigo-600 size-5 dark:text-indigo-400' />
        </div>
        <div className='flex items-end justify-between mt-4'>
          <div>
            <span className='text-sm text-gray-500 dark:text-gray-400'>
              Data Freshness
            </span>
            <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
              97%
            </h4>
            <span className='text-xs text-gray-400 dark:text-gray-500'>
              sources synced
            </span>
          </div>
          <Badge color='success'>
            <ArrowUpIcon />
            2%
          </Badge>
        </div>
        <p className='text-xs text-gray-500 dark:text-gray-400 mt-2'>
          &lt;15 min ago real-time sync
        </p>
      </div>

      {/* <!-- Coverage Growth --> */}
      <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5 min-h-[140px] flex flex-col justify-between'>
        <div className='flex items-center justify-center w-10 h-10 bg-cyan-100 rounded-xl dark:bg-cyan-800/20'>
          <PlugInIcon className='text-cyan-600 size-5 dark:text-cyan-400' />
        </div>
        <div className='flex items-end justify-between mt-4'>
          <div>
            <span className='text-sm text-gray-500 dark:text-gray-400'>
              Coverage Growth
            </span>
            <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
              12
            </h4>
            <span className='text-xs text-gray-400 dark:text-gray-500'>
              live connectors
            </span>
          </div>
          <Badge color='success'>
            <ArrowUpIcon />3 new
          </Badge>
        </div>
        <p className='text-xs text-gray-500 dark:text-gray-400 mt-2'>
          ↑3 this quarter, expanding coverage
        </p>
      </div>
    </div>
  );
}
