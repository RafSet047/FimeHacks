import PageMeta from "../../components/common/PageMeta";
import BusinessImpactMetrics from "../../components/ecommerce/BusinessImpactMetrics";
import DemographicCard from "../../components/ecommerce/DemographicCard";
import DocumentUpload from "../../components/ecommerce/DocumentUpload";
import MonthlySalesChart from "../../components/ecommerce/MonthlySalesChart";
import RecentOrders from "../../components/ecommerce/RecentOrders";
import StatisticsChart from "../../components/ecommerce/StatisticsChart";

export default function Home() {
  return (
    <>
      <PageMeta
        title='Knowledge Management Dashboard | Cerebryx - Admin Dashboard'
        description='This is the Knowledge Management Dashboard page for Cerebryx Admin Panel'
      />
      <div className='space-y-4 md:space-y-6'>
        {/* First Row: Business Impact Cards + Upload Card */}
        <div className='grid grid-cols-12 gap-4 md:gap-6 items-start'>
          <div className='col-span-12 xl:col-span-8'>
            <BusinessImpactMetrics />
          </div>
          <div className='col-span-12 xl:col-span-4'>
            <DocumentUpload />
          </div>
        </div>

        {/* Second Row: Charts and Other Components */}
        <div className='grid grid-cols-12 gap-4 md:gap-6'>
          <div className='col-span-12 space-y-6 xl:col-span-7'>
            <MonthlySalesChart />
          </div>

          <div className='col-span-12 xl:col-span-5'>
            <DemographicCard />
          </div>

          <div className='col-span-12'>
            <StatisticsChart />
          </div>

          <div className='col-span-12'>
            <RecentOrders />
          </div>
        </div>
      </div>
    </>
  );
}
