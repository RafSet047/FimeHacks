import BarChartOne from "../../components/charts/bar/BarChartOne";
import ComponentCard from "../../components/common/ComponentCard";
import PageBreadcrumb from "../../components/common/PageBreadCrumb";
import PageMeta from "../../components/common/PageMeta";

export default function BarChart() {
  return (
    <div>
      <PageMeta
        title='React.js Chart Dashboard | Cerebryx - React.js Admin Dashboard'
        description='This is React.js Chart Dashboard page for Cerebryx - React.js Admin Dashboard'
      />
      <PageBreadcrumb pageTitle='Bar Chart' />
      <div className='space-y-6'>
        <ComponentCard title='Bar Chart 1'>
          <BarChartOne />
        </ComponentCard>
      </div>
    </div>
  );
}
