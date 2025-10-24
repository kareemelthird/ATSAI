import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { candidateApi, resumeApi } from '@/lib/api'
import { Mail, Phone, MapPin, Linkedin, Github, Globe, Download, Trash2, FileText, Calendar, CheckCircle, Clock, XCircle, ArrowLeft, ExternalLink, Eye } from 'lucide-react'
import { useState } from 'react'

const CandidateDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [deleteResumeId, setDeleteResumeId] = useState<string | null>(null)

  const { data: candidate, isLoading } = useQuery({
    queryKey: ['candidate', id],
    queryFn: () => candidateApi.getById(id!),
  })

  const { data: resumes, isLoading: resumesLoading } = useQuery({
    queryKey: ['resumes', id],
    queryFn: () => resumeApi.getByCandidateId(id!),
    enabled: !!id,
  })

  const deleteResumeMutation = useMutation({
    mutationFn: (resumeId: string) => resumeApi.delete(resumeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes', id] })
      setDeleteResumeId(null)
    },
  })

  // Fix LinkedIn URL - ensure it starts with https://
  const fixUrl = (url: string | undefined) => {
    if (!url) return ''
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url
    }
    return `https://${url}`
  }

  const handleDownloadResume = (candidateId: string, filename: string) => {
    const downloadUrl = `http://localhost:8000/api/v1/candidates/${candidateId}/resume/download`
    window.open(downloadUrl, '_blank')
  }

  const handleDeleteResume = (resumeId: string) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      deleteResumeMutation.mutate(resumeId)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const candidateData = candidate?.data

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header with Back Button */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/candidates')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Candidates
        </button>
        
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            {/* Avatar */}
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-2xl font-bold">
              {candidateData?.first_name?.[0]}{candidateData?.last_name?.[0]}
            </div>
            
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {candidateData?.first_name} {candidateData?.last_name}
              </h1>
              <div className="flex items-center gap-3 mt-2">
                <span
                  className={`px-3 py-1 text-sm font-medium rounded-full ${
                    candidateData?.status === 'active'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                      : candidateData?.status === 'hired'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : candidateData?.status === 'interviewing'
                      ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  {candidateData?.status}
                </span>
                {candidateData?.career_level && (
                  <span className="px-3 py-1 text-sm font-medium rounded-full bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300">
                    {candidateData.career_level}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Contact Info */}
        <div className="lg:col-span-1">
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Contact Information
            </h2>
            <div className="space-y-3">
              {candidateData?.email && (
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    {candidateData.email}
                  </span>
                </div>
              )}
              {candidateData?.phone && (
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    {candidateData.phone}
                  </span>
                </div>
              )}
              {candidateData?.location && (
                <div className="flex items-center gap-3">
                  <MapPin className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    {candidateData.location}
                  </span>
                </div>
              )}
            </div>

            {(candidateData?.linkedin_url ||
              candidateData?.github_url ||
              candidateData?.portfolio_url) && (
              <>
                <hr className="my-4 border-gray-200 dark:border-gray-700" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Social Links
                </h3>
                <div className="space-y-2">
                  {candidateData?.linkedin_url && (
                    <a
                      href={fixUrl(candidateData.linkedin_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 group"
                    >
                      <Linkedin className="w-5 h-5" />
                      <span>LinkedIn</span>
                      <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  )}
                  {candidateData?.github_url && (
                    <a
                      href={fixUrl(candidateData.github_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 group"
                    >
                      <Github className="w-5 h-5" />
                      <span>GitHub</span>
                      <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  )}
                  {candidateData?.portfolio_url && (
                    <a
                      href={fixUrl(candidateData.portfolio_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 group"
                    >
                      <Globe className="w-5 h-5" />
                      <span>Portfolio</span>
                      <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  )}
                </div>
              </>
            )}
          </div>

          {/* Additional Info Card */}
          {(candidateData?.years_of_experience || candidateData?.current_location || candidateData?.created_at) && (
            <div className="card mt-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Additional Information
              </h2>
              <div className="space-y-3">
                {candidateData?.years_of_experience && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Years of Experience</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {candidateData.years_of_experience} years
                    </span>
                  </div>
                )}
                {candidateData?.current_location && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Current Location</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {candidateData.current_location}
                    </span>
                  </div>
                )}
                {candidateData?.created_at && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Added to System</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatDate(candidateData.created_at)}
                    </span>
                  </div>
                )}
                {candidateData?.updated_at && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Last Updated</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatDate(candidateData.updated_at)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Summary */}
          {candidateData?.summary && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Summary
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                {candidateData.summary}
              </p>
            </div>
          )}

          {/* Resumes */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Resumes ({resumes?.data?.length || 0})
              </h2>
              <button
                onClick={() => navigate(`/upload?candidateId=${id}`)}
                className="btn-primary text-sm"
              >
                <FileText className="w-4 h-4" />
                Upload New Resume
              </button>
            </div>

            {resumesLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
            ) : (
              <div className="space-y-3">
                {resumes?.data?.map((resume: any, index: number) => (
                  <div
                    key={resume.id}
                    className="group p-5 bg-gradient-to-r from-gray-50 to-white dark:from-gray-700 dark:to-gray-800 rounded-lg border border-gray-200 dark:border-gray-600 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-4">
                      {/* Left Side - File Info */}
                      <div className="flex items-start gap-4 flex-1">
                        {/* File Icon */}
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FileText className="w-6 h-6 text-white" />
                        </div>

                        {/* File Details */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                              {resume.original_filename || 'Resume.pdf'}
                            </h3>
                            {index === 0 && (
                              <span className="px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 rounded">
                                Latest
                              </span>
                            )}
                          </div>

                          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-gray-600 dark:text-gray-400">
                            <div className="flex items-center gap-1">
                              <span className="font-medium">Version {resume.version}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              <span>{formatDateTime(resume.upload_date)}</span>
                            </div>
                            {resume.file_size && (
                              <div className="flex items-center gap-1">
                                <FileText className="w-4 h-4" />
                                <span>{(resume.file_size / 1024).toFixed(1)} KB</span>
                              </div>
                            )}
                          </div>

                          {/* Parsed Data Preview */}
                          {resume.parsed_status === 'success' && resume.parsed_data && (
                            <div className="mt-3 p-3 bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-600">
                              <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Extracted Information:
                              </p>
                              <div className="grid grid-cols-2 gap-2 text-xs">
                                {resume.parsed_data.skills && (
                                  <div>
                                    <span className="text-gray-500 dark:text-gray-400">Skills:</span>
                                    <span className="ml-1 text-gray-900 dark:text-white">
                                      {resume.parsed_data.skills.slice(0, 3).join(', ')}
                                      {resume.parsed_data.skills.length > 3 && '...'}
                                    </span>
                                  </div>
                                )}
                                {resume.parsed_data.total_experience && (
                                  <div>
                                    <span className="text-gray-500 dark:text-gray-400">Experience:</span>
                                    <span className="ml-1 text-gray-900 dark:text-white">
                                      {resume.parsed_data.total_experience} years
                                    </span>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Right Side - Status & Actions */}
                      <div className="flex flex-col items-end gap-3">
                        {/* Parse Status */}
                        <div className="flex items-center gap-2">
                          {getStatusIcon(resume.parsed_status)}
                          <span
                            className={`px-3 py-1 text-xs font-medium rounded-full ${
                              resume.parsed_status === 'success'
                                ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                                : resume.parsed_status === 'pending'
                                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                                : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                            }`}
                          >
                            {resume.parsed_status}
                          </span>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleDownloadResume(id!, resume.original_filename)}
                            className="p-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                            title="Download Resume"
                          >
                            <Download className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleDeleteResume(resume.id)}
                            disabled={deleteResumeMutation.isPending}
                            className="p-2 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50"
                            title="Delete Resume"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {(!resumes?.data || resumes.data.length === 0) && (
                  <div className="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
                    <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      No resumes uploaded yet
                    </p>
                    <button
                      onClick={() => navigate(`/upload?candidateId=${id}`)}
                      className="btn-primary"
                    >
                      <FileText className="w-4 h-4" />
                      Upload First Resume
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CandidateDetail
