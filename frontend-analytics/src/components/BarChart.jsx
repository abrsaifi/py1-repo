// Bar chart component
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

export const BarChart = ({ title, labels, datasets, options = {} }) => {
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
      backgroundColor: ds.backgroundColor || '#3b82f6',
      borderColor: ds.borderColor || '#1e40af',
      borderWidth: 1,
    })),
  }

  return <Bar data={data} options={{ ...defaultOptions, ...options }} />
}

export default BarChart
