import { useState, useCallback } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { useNavigate, Link } from 'react-router-dom'
import { resumeApi, api } from '@/lib/api'
import { Upload as UploadIcon, Check, FileText, Loader2, Sparkles, AlertTriangle } from 'lucide-react'

const UploadResume = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState<string>('')
  const [candidateInfo, setCandidateInfo] = useState<any>(null)

  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Check if user has personal API key configured
  const { data: aiSettings } = useQuery({
    queryKey: ['profile-ai-settings'],
    queryFn: async () => {
      const response = await api.get('/profile/ai-settings')
      return response.data
    }
  })

  const uploadResumeMutation = useMutation({
    mutationFn: (file: File) => resumeApi.uploadAuto(file),
    onMutate: () => {
      setUploadStatus('uploading')
      setErrorMessage('')
    },
    onSuccess: (response) => {
      setUploadStatus('success')
      setCandidateInfo(response.data)
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
      
      // Auto-navigate to candidates page after 3 seconds
      setTimeout(() => navigate('/candidates'), 3000)
    },
    onError: (error: any) => {
      setUploadStatus('error')
      setErrorMessage(error.response?.data?.detail || 'Failed to upload resume. Please try again.')
    },
  })

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file && (file.type === 'application/pdf' || file.name.endsWith('.pdf'))) {
      setSelectedFile(file)
      uploadResumeMutation.mutate(file)
    } else {
      setErrorMessage('Please upload a PDF file')
    }
  }, [uploadResumeMutation])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      uploadResumeMutation.mutate(file)
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Upload Resume</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8 flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-primary-500" />
        AI will automatically extract all candidate information from the CV
      </p>

      {/* API Key Warning Banner */}
      {aiSettings && (!aiSettings.has_personal_key || !aiSettings.use_personal_ai_key) && (
        <div className="max-w-3xl mx-auto mb-6 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 p-4 rounded-lg">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-1">
                ⚠️ Limited System API Usage
              </h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-2">
                You're using the system API key which has very limited usage. For unlimited resume parsing, 
                please add your free personal Groq API key.
              </p>
              <Link
                to="/profile"
                className="inline-flex items-center px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded transition-colors"
              >
                🔑 Add Personal Key (Free)
              </Link>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-3xl mx-auto">
        {uploadStatus === 'idle' && (
          <div className="card">
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-all ${
                isDragging
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-300 dark:border-gray-600'
              }`}
            >
              <UploadIcon className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Drop your CV here
              </h3>
              <p className="text-gray-500 mb-4">or click to browse</p>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="btn-primary inline-block cursor-pointer"
              >
                Choose PDF File
              </label>
              <p className="text-sm text-gray-500 mt-4">
                Supports PDF files (max 10MB)
              </p>
              
              {errorMessage && (
                <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-red-600 dark:text-red-400 text-sm">{errorMessage}</p>
                </div>
              )}
            </div>

            <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
              <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-3 flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                AI-Powered Extraction
              </h4>
              <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Automatically extracts name, contact info, and location</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Identifies all skills with proficiency levels</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Parses work experience, education, and certifications</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Generates career insights and strengths analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>Creates smart tags for easy candidate matching</span>
                </li>
              </ul>
            </div>
          </div>
        )}

        {uploadStatus === 'uploading' && (
          <div className="card text-center py-12">
            <Loader2 className="w-16 h-16 mx-auto text-primary-600 animate-spin mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              Processing Resume...
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              AI is analyzing the CV and extracting all information
            </p>
            {selectedFile && (
              <div className="inline-flex items-center gap-3 px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                <FileText className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {selectedFile.name}
                </span>
                <span className="text-xs text-gray-500">
                  {(selectedFile.size / 1024).toFixed(0)} KB
                </span>
              </div>
            )}
          </div>
        )}

        {uploadStatus === 'success' && (
          <div className="card text-center py-12">
            <div className="bg-green-100 dark:bg-green-900 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
              <Check className="w-12 h-12 text-green-600 dark:text-green-400" />
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              Resume Processed Successfully!
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              AI has extracted all candidate information
            </p>
            
            {candidateInfo && (
              <div className="max-w-md mx-auto bg-gray-50 dark:bg-gray-800 rounded-lg p-6 mb-6">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Extracted Information
                </h3>
                <div className="text-left space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Name:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {candidateInfo.first_name} {candidateInfo.last_name}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Email:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {candidateInfo.email}
                    </span>
                  </div>
                  {candidateInfo.phone && (
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Phone:</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {candidateInfo.phone}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            <p className="text-sm text-gray-500 mb-4">
              Redirecting to candidates page...
            </p>
            <button
              onClick={() => navigate('/candidates')}
              className="btn-primary"
            >
              View All Candidates
            </button>
          </div>
        )}

        {uploadStatus === 'error' && (
          <div className="card text-center py-12">
            <div className="bg-red-100 dark:bg-red-900 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
              <FileText className="w-12 h-12 text-red-600 dark:text-red-400" />
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              Upload Failed
            </h2>
            <p className="text-red-600 dark:text-red-400 mb-6">{errorMessage}</p>
            <button
              onClick={() => {
                setUploadStatus('idle')
                setSelectedFile(null)
                setErrorMessage('')
              }}
              className="btn-primary"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadResume
