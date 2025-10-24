import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { candidateApi } from '@/lib/api'
import { 
  Plus, Search, User, Trash2, Filter, Grid3x3, List, 
  Mail, MapPin, Calendar, Briefcase, Star, Download, Eye
} from 'lucide-react'

const Candidates = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [careerLevelFilter, setCareerLevelFilter] = useState('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [sortBy, setSortBy] = useState('recent')
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['candidates', statusFilter],
    queryFn: () =>
      candidateApi.getAll({
        status: statusFilter === 'all' ? undefined : statusFilter,
        limit: 100,
      }),
  })

  const deleteMutation = useMutation({
    mutationFn: (candidateId: string) => candidateApi.delete(candidateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
    },
  })

  const handleDelete = (e: React.MouseEvent, candidateId: string, name: string) => {
    e.preventDefault() // Prevent navigation
    if (window.confirm(`Are you sure you want to delete ${name}? This will also delete all their resumes and data.`)) {
      deleteMutation.mutate(candidateId)
    }
  }

  const filteredCandidates = data?.data?.filter((candidate: any) => {
    const searchLower = searchTerm.toLowerCase()
    const matchesSearch = (
      candidate.first_name.toLowerCase().includes(searchLower) ||
      candidate.last_name.toLowerCase().includes(searchLower) ||
      candidate.email.toLowerCase().includes(searchLower) ||
      candidate.phone?.toLowerCase().includes(searchLower) ||
      candidate.current_location?.toLowerCase().includes(searchLower)
    )
    
    const matchesStatus = statusFilter === 'all' || candidate.status === statusFilter
    const matchesCareerLevel = careerLevelFilter === 'all' || candidate.career_level === careerLevelFilter
    
    return matchesSearch && matchesStatus && matchesCareerLevel
  })

  // Sort candidates
  const sortedCandidates = filteredCandidates?.sort((a: any, b: any) => {
    switch (sortBy) {
      case 'name':
        return `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`)
      case 'recent':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'updated':
        return new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime()
      default:
        return 0
    }
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Candidates
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {sortedCandidates?.length || 0} total candidates
          </p>
        </div>
        <Link to="/upload" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Add Candidate
        </Link>
      </div>

      {/* Filters and Controls */}
      <div className="card mb-6">
        <div className="flex flex-col gap-4">
          {/* Search and View Toggle */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, email, phone, location..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10 w-full"
              />
            </div>
            
            {/* View Mode Toggle */}
            <div className="flex gap-2 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-2 rounded transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-white dark:bg-gray-600 text-primary-600 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
                title="Grid view"
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-2 rounded transition-colors ${
                  viewMode === 'list'
                    ? 'bg-white dark:bg-gray-600 text-primary-600 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
                title="List view"
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Filters Row */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex items-center gap-2 flex-1">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input flex-1"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="archived">Archived</option>
                <option value="hired">Hired</option>
                <option value="interviewing">Interviewing</option>
              </select>
            </div>

            <select
              value={careerLevelFilter}
              onChange={(e) => setCareerLevelFilter(e.target.value)}
              className="input flex-1"
            >
              <option value="all">All Levels</option>
              <option value="entry">Entry Level</option>
              <option value="junior">Junior</option>
              <option value="mid">Mid Level</option>
              <option value="senior">Senior</option>
              <option value="lead">Lead</option>
              <option value="principal">Principal</option>
              <option value="executive">Executive</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input flex-1"
            >
              <option value="recent">Recently Added</option>
              <option value="updated">Recently Updated</option>
              <option value="name">Name (A-Z)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="text-center py-20">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-primary-600"></div>
          <p className="text-gray-600 dark:text-gray-400 mt-4">Loading candidates...</p>
        </div>
      ) : sortedCandidates?.length === 0 ? (
        /* Empty State */
        <div className="text-center py-20">
          <User className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-xl font-medium text-gray-900 dark:text-white mb-2">
            No candidates found
          </p>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {searchTerm || statusFilter !== 'all' || careerLevelFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Get started by adding your first candidate'}
          </p>
          {!searchTerm && statusFilter === 'all' && careerLevelFilter === 'all' && (
            <Link to="/upload" className="btn-primary inline-flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Add First Candidate
            </Link>
          )}
        </div>
      ) : viewMode === 'grid' ? (
        /* Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {sortedCandidates?.map((candidate: any) => {
            const fullName = `${candidate.first_name} ${candidate.last_name}`
            return (
              <div key={candidate.id} className="card hover:shadow-xl transition-all duration-200 relative group">
                {/* Delete Button */}
                <button
                  onClick={(e) => handleDelete(e, candidate.id, fullName)}
                  className="absolute top-3 right-3 p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors opacity-0 group-hover:opacity-100 z-10"
                  title="Delete candidate"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                
                <Link to={`/candidates/${candidate.id}`} className="block">
                  {/* Avatar and Basic Info */}
                  <div className="flex flex-col items-center text-center mb-4">
                    <div className="bg-gradient-to-br from-primary-500 to-primary-600 rounded-full p-4 mb-3">
                      <User className="w-10 h-10 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                      {fullName}
                    </h3>
                    {candidate.career_level && (
                      <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                        {candidate.career_level} Level
                      </span>
                    )}
                  </div>

                  {/* Contact Info */}
                  <div className="space-y-2 mb-4">
                    {candidate.email && (
                      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <Mail className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{candidate.email}</span>
                      </div>
                    )}
                    {candidate.current_location && (
                      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <MapPin className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{candidate.current_location}</span>
                      </div>
                    )}
                    {candidate.created_at && (
                      <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-500">
                        <Calendar className="w-4 h-4 flex-shrink-0" />
                        <span>Added {formatDate(candidate.created_at)}</span>
                      </div>
                    )}
                  </div>

                  {/* Status Badge */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                    <span
                      className={`px-3 py-1 text-xs font-medium rounded-full ${
                        candidate.status === 'active'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                          : candidate.status === 'hired'
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                          : candidate.status === 'interviewing'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                          : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {candidate.status || 'Unknown'}
                    </span>
                    <Eye className="w-4 h-4 text-gray-400" />
                  </div>
                </Link>
              </div>
            )
          })}
        </div>
      ) : (
        /* List View */
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Candidate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Added
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {sortedCandidates?.map((candidate: any) => {
                  const fullName = `${candidate.first_name} ${candidate.last_name}`
                  return (
                    <tr key={candidate.id} className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5 text-white" />
                          </div>
                          <div className="ml-4">
                            <Link 
                              to={`/candidates/${candidate.id}`}
                              className="text-sm font-medium text-gray-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400"
                            >
                              {fullName}
                            </Link>
                            {candidate.current_location && (
                              <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mt-1">
                                <MapPin className="w-3 h-3" />
                                {candidate.current_location}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 dark:text-white">{candidate.email}</div>
                        {candidate.phone && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">{candidate.phone}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900 dark:text-white capitalize">
                          {candidate.career_level || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            candidate.status === 'active'
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : candidate.status === 'hired'
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                              : candidate.status === 'interviewing'
                              ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                          }`}
                        >
                          {candidate.status || 'Unknown'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {candidate.created_at ? formatDate(candidate.created_at) : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/candidates/${candidate.id}`}
                            className="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 p-2 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded transition-colors"
                            title="View details"
                          >
                            <Eye className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={(e) => handleDelete(e, candidate.id, fullName)}
                            className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 p-2 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default Candidates
