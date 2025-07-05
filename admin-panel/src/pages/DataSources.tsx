import ComponentCard from "../components/common/ComponentCard";
import PageBreadcrumb from "../components/common/PageBreadCrumb";
import PageMeta from "../components/common/PageMeta";
import Badge from "../components/ui/badge/Badge";
import {
  AlertIcon,
  AudioIcon,
  BoltIcon,
  BoxCubeIcon,
  CalenderIcon,
  ChatIcon,
  CheckCircleIcon,
  DocsIcon,
  EnvelopeIcon,
  FileIcon,
  GroupIcon,
  InfoIcon,
  PlugInIcon,
  TableIcon,
  TimeIcon,
  VideoIcon,
} from "../icons";

export default function DataSources() {
  return (
    <>
      <PageMeta
        title='Data Sources Dashboard | Cerebryx - Admin Dashboard'
        description='Manage and monitor various data sources and connectors for your knowledge management system'
      />
      <PageBreadcrumb pageTitle='Data Sources' />

      <div className='space-y-6'>
        {/* Overview Stats */}
        <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4'>
          <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
            <div className='flex items-center justify-between'>
              <div>
                <span className='text-sm text-gray-500 dark:text-gray-400'>
                  Active Sources
                </span>
                <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
                  24
                </h4>
              </div>
              <div className='flex items-center justify-center w-10 h-10 bg-green-100 rounded-xl dark:bg-green-800/20'>
                <CheckCircleIcon className='text-green-600 size-5 dark:text-green-400' />
              </div>
            </div>
          </div>

          <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
            <div className='flex items-center justify-between'>
              <div>
                <span className='text-sm text-gray-500 dark:text-gray-400'>
                  Data Ingested
                </span>
                <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
                  2.4TB
                </h4>
              </div>
              <div className='flex items-center justify-center w-10 h-10 bg-blue-100 rounded-xl dark:bg-blue-800/20'>
                <BoxCubeIcon className='text-blue-600 size-5 dark:text-blue-400' />
              </div>
            </div>
          </div>

          <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
            <div className='flex items-center justify-between'>
              <div>
                <span className='text-sm text-gray-500 dark:text-gray-400'>
                  Real-time Streams
                </span>
                <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
                  8
                </h4>
              </div>
              <div className='flex items-center justify-center w-10 h-10 bg-purple-100 rounded-xl dark:bg-purple-800/20'>
                <BoltIcon className='text-purple-600 size-5 dark:text-purple-400' />
              </div>
            </div>
          </div>

          <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
            <div className='flex items-center justify-between'>
              <div>
                <span className='text-sm text-gray-500 dark:text-gray-400'>
                  Sync Status
                </span>
                <h4 className='mt-1 font-bold text-gray-800 text-title-sm dark:text-white/90'>
                  98%
                </h4>
              </div>
              <div className='flex items-center justify-center w-10 h-10 bg-cyan-100 rounded-xl dark:bg-cyan-800/20'>
                <TimeIcon className='text-cyan-600 size-5 dark:text-cyan-400' />
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Data Sources */}
        <ComponentCard title='Real-time Data Sources'>
          <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3'>
            {/* Camera Streams */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-red-100 rounded-xl dark:bg-red-800/20'>
                  <VideoIcon className='text-red-600 size-5 dark:text-red-400' />
                </div>
                <Badge color='success'>Live</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Camera Streams
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Real-time video analysis from security cameras and surveillance
                systems
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>6 active streams</span>
                <span className='flex items-center'>
                  <div className='w-2 h-2 bg-green-500 rounded-full mr-1'></div>
                  Streaming
                </span>
              </div>
            </div>

            {/* Audio Streams */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-orange-100 rounded-xl dark:bg-orange-800/20'>
                  <AudioIcon className='text-orange-600 size-5 dark:text-orange-400' />
                </div>
                <Badge color='success'>Live</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Audio Monitoring
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Voice-to-text transcription from call centers and meeting rooms
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>12 audio feeds</span>
                <span className='flex items-center'>
                  <div className='w-2 h-2 bg-green-500 rounded-full mr-1'></div>
                  Processing
                </span>
              </div>
            </div>

            {/* IoT Sensors */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-green-100 rounded-xl dark:bg-green-800/20'>
                  <BoltIcon className='text-green-600 size-5 dark:text-green-400' />
                </div>
                <Badge color='success'>Live</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                IoT Sensors
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Environmental and operational data from connected devices
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>247 sensors</span>
                <span className='flex items-center'>
                  <div className='w-2 h-2 bg-green-500 rounded-full mr-1'></div>
                  Active
                </span>
              </div>
            </div>
          </div>
        </ComponentCard>

        {/* Communication Channels */}
        <ComponentCard title='Communication Channels'>
          <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3'>
            {/* Email Integration */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-blue-100 rounded-xl dark:bg-blue-800/20'>
                  <EnvelopeIcon className='text-blue-600 size-5 dark:text-blue-400' />
                </div>
                <Badge color='success'>Synced</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Email Integration
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Meeting minutes, project updates, and important communications
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>3 mailboxes</span>
                <span>Last sync: 2 min ago</span>
              </div>
            </div>

            {/* Chat Platforms */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-purple-100 rounded-xl dark:bg-purple-800/20'>
                  <ChatIcon className='text-purple-600 size-5 dark:text-purple-400' />
                </div>
                <Badge color='success'>Connected</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Chat Platforms
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Slack, Teams, Discord conversations and shared knowledge
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>15 channels</span>
                <span>Real-time sync</span>
              </div>
            </div>

            {/* Bot Networks */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-cyan-100 rounded-xl dark:bg-cyan-800/20'>
                  <GroupIcon className='text-cyan-600 size-5 dark:text-cyan-400' />
                </div>
                <Badge color='success'>Active</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Bot Networks
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                AI agents, chatbots, and automated note-taking systems
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>8 bots active</span>
                <span>24/7 monitoring</span>
              </div>
            </div>
          </div>
        </ComponentCard>

        {/* Document & File Sources */}
        <ComponentCard title='Document & File Sources'>
          <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3'>
            {/* Cloud Storage */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-indigo-100 rounded-xl dark:bg-indigo-800/20'>
                  <FileIcon className='text-indigo-600 size-5 dark:text-indigo-400' />
                </div>
                <Badge color='success'>Synced</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Cloud Storage
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Google Drive, Dropbox, OneDrive document repositories
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>12.5K files</span>
                <span>Auto-sync enabled</span>
              </div>
            </div>

            {/* Document Management */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-yellow-100 rounded-xl dark:bg-yellow-800/20'>
                  <DocsIcon className='text-yellow-600 size-5 dark:text-yellow-400' />
                </div>
                <Badge color='success'>Connected</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Document Management
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                SharePoint, Confluence, Notion knowledge bases
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>5 systems</span>
                <span>Incremental sync</span>
              </div>
            </div>

            {/* Version Control */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-gray-100 rounded-xl dark:bg-gray-800/20'>
                  <BoxCubeIcon className='text-gray-600 size-5 dark:text-gray-400' />
                </div>
                <Badge color='success'>Connected</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Version Control
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Git repositories, code documentation, and technical wikis
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>23 repositories</span>
                <span>Webhook sync</span>
              </div>
            </div>
          </div>
        </ComponentCard>

        {/* Database & API Sources */}
        <ComponentCard title='Database & API Sources'>
          <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3'>
            {/* Database Systems */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-emerald-100 rounded-xl dark:bg-emerald-800/20'>
                  <TableIcon className='text-emerald-600 size-5 dark:text-emerald-400' />
                </div>
                <Badge color='success'>Connected</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Database Systems
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                PostgreSQL, MySQL, MongoDB operational data
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>4 databases</span>
                <span>Real-time CDC</span>
              </div>
            </div>

            {/* API Integrations */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-rose-100 rounded-xl dark:bg-rose-800/20'>
                  <PlugInIcon className='text-rose-600 size-5 dark:text-rose-400' />
                </div>
                <Badge color='success'>Active</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                API Integrations
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                REST APIs, GraphQL, microservices data feeds
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>18 endpoints</span>
                <span>Rate limited</span>
              </div>
            </div>

            {/* Event Streams */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-violet-100 rounded-xl dark:bg-violet-800/20'>
                  <CalenderIcon className='text-violet-600 size-5 dark:text-violet-400' />
                </div>
                <Badge color='success'>Streaming</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Event Streams
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Kafka, RabbitMQ, and other message queue systems
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>7 streams</span>
                <span>High throughput</span>
              </div>
            </div>
          </div>
        </ComponentCard>

        {/* Social Media & External Sources */}
        <ComponentCard title='Social Media & External Sources'>
          <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3'>
            {/* Social Media */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-pink-100 rounded-xl dark:bg-pink-800/20'>
                  <GroupIcon className='text-pink-600 size-5 dark:text-pink-400' />
                </div>
                <Badge color='warning'>Limited</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Social Media
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                Twitter, LinkedIn, Reddit mentions and discussions
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>3 platforms</span>
                <span>API rate limits</span>
              </div>
            </div>

            {/* Web Scraping */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-teal-100 rounded-xl dark:bg-teal-800/20'>
                  <InfoIcon className='text-teal-600 size-5 dark:text-teal-400' />
                </div>
                <Badge color='success'>Scheduled</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Web Scraping
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                News sites, blogs, and industry publications
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>25 sources</span>
                <span>Daily crawl</span>
              </div>
            </div>

            {/* Third-party Services */}
            <div className='rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03] md:p-5'>
              <div className='flex items-center justify-between mb-4'>
                <div className='flex items-center justify-center w-10 h-10 bg-amber-100 rounded-xl dark:bg-amber-800/20'>
                  <PlugInIcon className='text-amber-600 size-5 dark:text-amber-400' />
                </div>
                <Badge color='success'>Connected</Badge>
              </div>
              <h4 className='font-semibold text-gray-800 dark:text-white/90 mb-2'>
                Third-party Services
              </h4>
              <p className='text-sm text-gray-500 dark:text-gray-400 mb-3'>
                CRM systems, analytics platforms, and business tools
              </p>
              <div className='flex items-center justify-between text-xs text-gray-500 dark:text-gray-400'>
                <span>11 services</span>
                <span>OAuth secured</span>
              </div>
            </div>
          </div>
        </ComponentCard>

        {/* Quick Actions */}
        <ComponentCard title='Quick Actions'>
          <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4'>
            <button className='flex items-center justify-center p-4 rounded-2xl border border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-800 dark:bg-white/[0.03] dark:hover:bg-white/[0.05] transition-colors'>
              <div className='text-center'>
                <div className='flex items-center justify-center w-12 h-12 bg-blue-100 rounded-xl dark:bg-blue-800/20 mx-auto mb-3'>
                  <PlugInIcon className='text-blue-600 size-6 dark:text-blue-400' />
                </div>
                <h5 className='font-medium text-gray-800 dark:text-white/90'>
                  Add New Source
                </h5>
                <p className='text-sm text-gray-500 dark:text-gray-400 mt-1'>
                  Connect new data source
                </p>
              </div>
            </button>

            <button className='flex items-center justify-center p-4 rounded-2xl border border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-800 dark:bg-white/[0.03] dark:hover:bg-white/[0.05] transition-colors'>
              <div className='text-center'>
                <div className='flex items-center justify-center w-12 h-12 bg-green-100 rounded-xl dark:bg-green-800/20 mx-auto mb-3'>
                  <CheckCircleIcon className='text-green-600 size-6 dark:text-green-400' />
                </div>
                <h5 className='font-medium text-gray-800 dark:text-white/90'>
                  Health Check
                </h5>
                <p className='text-sm text-gray-500 dark:text-gray-400 mt-1'>
                  Monitor all sources
                </p>
              </div>
            </button>

            <button className='flex items-center justify-center p-4 rounded-2xl border border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-800 dark:bg-white/[0.03] dark:hover:bg-white/[0.05] transition-colors'>
              <div className='text-center'>
                <div className='flex items-center justify-center w-12 h-12 bg-purple-100 rounded-xl dark:bg-purple-800/20 mx-auto mb-3'>
                  <BoltIcon className='text-purple-600 size-6 dark:text-purple-400' />
                </div>
                <h5 className='font-medium text-gray-800 dark:text-white/90'>
                  Force Sync
                </h5>
                <p className='text-sm text-gray-500 dark:text-gray-400 mt-1'>
                  Trigger manual sync
                </p>
              </div>
            </button>

            <button className='flex items-center justify-center p-4 rounded-2xl border border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-800 dark:bg-white/[0.03] dark:hover:bg-white/[0.05] transition-colors'>
              <div className='text-center'>
                <div className='flex items-center justify-center w-12 h-12 bg-orange-100 rounded-xl dark:bg-orange-800/20 mx-auto mb-3'>
                  <AlertIcon className='text-orange-600 size-6 dark:text-orange-400' />
                </div>
                <h5 className='font-medium text-gray-800 dark:text-white/90'>
                  View Alerts
                </h5>
                <p className='text-sm text-gray-500 dark:text-gray-400 mt-1'>
                  Check sync issues
                </p>
              </div>
            </button>
          </div>
        </ComponentCard>
      </div>
    </>
  );
}
