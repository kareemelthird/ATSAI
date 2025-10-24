import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { jobApi } from '@/lib/api'

const JobDetail = () => {
  const { id } = useParams<{ id: string }>()
  const { data: job, isLoading } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobApi.getById(id!),
  })

  if (isLoading) return <div>Loading...</div>

  const jobData = job?.data

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">{jobData?.title}</h1>
      <div className="card">
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">Description</h3>
            <p className="text-gray-700 dark:text-gray-300">{jobData?.description}</p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">Requirements</h3>
            <p className="text-gray-700 dark:text-gray-300">{jobData?.requirements}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default JobDetail
