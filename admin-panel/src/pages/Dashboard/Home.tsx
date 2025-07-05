import PageMeta from "../../components/common/PageMeta";
import DemographicCard from "../../components/ecommerce/DemographicCard";
import DocumentUpload from "../../components/ecommerce/DocumentUpload";
import EcommerceMetrics from "../../components/ecommerce/EcommerceMetrics";
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
      <div className='grid grid-cols-12 gap-4 md:gap-6'>
        <div className='col-span-12 space-y-6 xl:col-span-7'>
          <EcommerceMetrics />

          <MonthlySalesChart />
        </div>

        <div className='col-span-12 xl:col-span-5'>
          <DocumentUpload />
        </div>

        <div className='col-span-12'>
          <StatisticsChart />
        </div>

        <div className='col-span-12 xl:col-span-5'>
          <DemographicCard />
        </div>

        <div className='col-span-12 xl:col-span-7'>
          <RecentOrders />
        </div>
      </div>
    </>
  );
}
