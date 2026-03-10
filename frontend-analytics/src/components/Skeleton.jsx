// Skeleton loader components
import '../styles/skeleton.css'

export const Skeleton = ({ width = '100%', height = '20px', borderRadius = '4px', count = 1 }) => {
  return (
    <>
      {Array(count).fill(0).map((_, i) => (
        <div 
          key={`skeleton-${i}`}
          className="skeleton"
          style={{ width, height, borderRadius }}
        ></div>
      ))}
    </>
  )
}

export const CardSkeleton = () => {
  return (
    <div className="card skeleton-card">
      <Skeleton width="80%" height="20px" count={3} />
      <Skeleton width="100%" height="40px" borderRadius="8px" />
    </div>
  )
}

export const TableSkeleton = ({ rows = 5 }) => {
  return (
    <table className="skeleton-table">
      <thead>
        <tr>
          <th><Skeleton width="100%" height="20px" /></th>
          <th><Skeleton width="100%" height="20px" /></th>
          <th><Skeleton width="100%" height="20px" /></th>
          <th><Skeleton width="100%" height="20px" /></th>
        </tr>
      </thead>
      <tbody>
        {Array(rows).fill(0).map((_, i) => (
          <tr key={`row-${i}`}>
            <td><Skeleton width="100%" height="20px" /></td>
            <td><Skeleton width="100%" height="20px" /></td>
            <td><Skeleton width="100%" height="20px" /></td>
            <td><Skeleton width="100%" height="20px" /></td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default Skeleton
