// Line chart component
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export const LineChart = ({ title, labels, datasets, options = {} }) => {
  const defaultOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: title,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  }

  const data = {
    labels,
    datasets: datasets.map(ds => ({
      ...ds,
      borderColor: ds.borderColor || '#3b82f6',
      backgroundColor: ds.backgroundColor || 'rgba(59, 130, 246, 0.1)',
      tension: 0.1,
    })),
  }

  return <Line data={data} options={{ ...defaultOptions, ...options }} />
}

export default LineChart
