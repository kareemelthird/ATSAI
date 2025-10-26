import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { candidateApi, resumeApi } from '@/lib/api'
import { 
  Mail, Phone, MapPin, Linkedin, Github, Globe, Download, Trash2, FileText, 
  Calendar, CheckCircle, Clock, XCircle, ArrowLeft, ExternalLink, Eye, 
  Briefcase, GraduationCap, Award, Code, Languages, FolderGit2, DollarSign,
  MapPinned, Building2, Star, BookOpen, BarChart3, TrendingUp, PieChart
} from 'lucide-react'
import { useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type TabType = 'overview' | 'skills' | 'experience' | 'education' | 'projects' | 'certifications' | 'resumes' | 'analytics'

const CandidateDetailEnhanced = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<TabType>('overview')

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
    },
  })

  const fixUrl = (url: string | undefined) => {
    if (!url) return ''
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url
    }
    return `https://${url}`
  }

  const handleDownloadResume = (candidateId: string) => {
    const downloadUrl = `${API_BASE_URL}/api/v1/candidates/${candidateId}/resume/download`
    window.open(downloadUrl, '_blank')
  }

  const handleDeleteResume = (resumeId: string) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      deleteResumeMutation.mutate(resumeId)
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Present'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
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

  const getProficiencyColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'expert':
        return 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
      case 'advanced':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
      case 'intermediate':
        return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
      case 'beginner':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
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

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Eye },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'skills', label: 'Skills', icon: Code, count: candidateData?.skills?.length },
    { id: 'experience', label: 'Experience', icon: Briefcase, count: candidateData?.work_experiences?.length },
    { id: 'education', label: 'Education', icon: GraduationCap, count: candidateData?.educations?.length },
    { id: 'projects', label: 'Projects', icon: FolderGit2, count: candidateData?.projects?.length },
    { id: 'certifications', label: 'Certifications', icon: Award, count: candidateData?.certifications?.length },
    { id: 'resumes', label: 'Resumes', icon: FileText, count: resumes?.data?.length },
  ]

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
        
        {/* Candidate Header Card */}
        <div className="card">
          <div className="flex items-start gap-6">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-3xl font-bold flex-shrink-0">
              {candidateData?.first_name?.[0]}{candidateData?.last_name?.[0]}
            </div>
            
            <div className="flex-1">
              {/* Name and Status */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                    {candidateData?.first_name} {candidateData?.last_name}
                  </h1>
                  <div className="flex items-center gap-3 mb-3">
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
                    {candidateData?.availability_status && (
                      <span className="px-3 py-1 text-sm font-medium rounded-full bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">
                        Available: {candidateData.availability_status}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Contact Info - Horizontal */}
              <div className="flex flex-wrap items-center gap-6 text-sm mb-4">
                {candidateData?.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <a href={`mailto:${candidateData.email}`} className="text-primary-600 hover:text-primary-700 dark:text-primary-400">
                      {candidateData.email}
                    </a>
                  </div>
                )}
                {candidateData?.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-gray-400" />
                    <a href={`tel:${candidateData.phone}`} className="text-gray-700 dark:text-gray-300">
                      {candidateData.phone}
                    </a>
                  </div>
                )}
                {candidateData?.current_location && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-700 dark:text-gray-300">
                      {candidateData.current_location}
                    </span>
                  </div>
                )}
              </div>

              {/* Social Links - Horizontal */}
              {(candidateData?.linkedin_url || candidateData?.github_url || candidateData?.portfolio_url || candidateData?.personal_website) && (
                <div className="flex items-center gap-4">
                  {candidateData?.linkedin_url && (
                    <a
                      href={fixUrl(candidateData.linkedin_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 text-sm group"
                    >
                      <Linkedin className="w-4 h-4" />
                      <span>LinkedIn</span>
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  )}
                  {candidateData?.github_url && (
                    <a
                      href={fixUrl(candidateData.github_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 text-sm group"
                    >
                      <Github className="w-4 h-4" />
                      <span>GitHub</span>
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  )}
                  {candidateData?.portfolio_url && (
                    <a
                      href={fixUrl(candidateData.portfolio_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 text-sm group"
                    >
                      <Globe className="w-4 h-4" />
                      <span>Portfolio</span>
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  )}
                  {candidateData?.personal_website && (
                    <a
                      href={fixUrl(candidateData.personal_website)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 text-sm group"
                    >
                      <Globe className="w-4 h-4" />
                      <span>Website</span>
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="card mb-6 overflow-x-auto">
        <div className="flex gap-1 min-w-max">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`flex items-center gap-2 px-4 py-3 rounded-lg font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                    : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.label}</span>
                {tab.count !== undefined && tab.count > 0 && (
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    activeTab === tab.id
                      ? 'bg-primary-200 text-primary-800 dark:bg-primary-800 dark:text-primary-200'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-600 dark:text-gray-300'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Professional Summary */}
            {candidateData?.professional_summary && (
              <div className="card">
                <div className="flex items-center gap-2 mb-4">
                  <BookOpen className="w-5 h-5 text-primary-600" />
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Professional Summary
                  </h2>
                </div>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-base">
                  {candidateData.professional_summary}
                </p>
              </div>
            )}

            {/* Key Information Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Compensation */}
              {(candidateData?.current_salary_amount || candidateData?.expected_salary_amount) && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <DollarSign className="w-5 h-5 text-green-600" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Compensation
                    </h3>
                  </div>
                  <div className="space-y-3">
                    {candidateData?.current_salary_amount && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Current Salary</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-white">
                          {candidateData.current_salary_currency || 'USD'} {candidateData.current_salary_amount?.toLocaleString()}
                        </p>
                      </div>
                    )}
                    {candidateData?.expected_salary_amount && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Expected Salary</p>
                        <p className="text-lg font-semibold text-green-600 dark:text-green-400">
                          {candidateData.expected_salary_currency || 'USD'} {candidateData.expected_salary_amount?.toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Location & Mobility */}
              {(candidateData?.preferred_locations || candidateData?.open_to_relocation || candidateData?.willing_to_travel || candidateData?.notice_period_days) && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <MapPinned className="w-5 h-5 text-blue-600" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Location & Mobility
                    </h3>
                  </div>
                  <div className="space-y-3">
                    {candidateData?.preferred_locations && candidateData.preferred_locations.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Preferred Locations</p>
                        <div className="flex flex-wrap gap-2">
                          {candidateData.preferred_locations.map((loc: string, idx: number) => (
                            <span key={idx} className="px-2 py-1 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 rounded text-xs">
                              {loc}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="space-y-2">
                      {candidateData?.open_to_relocation && (
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Open to Relocation</span>
                        </div>
                      )}
                      {candidateData?.willing_to_travel && (
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Willing to Travel</span>
                        </div>
                      )}
                    </div>
                    {candidateData?.notice_period_days && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Notice Period</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{candidateData.notice_period_days} days</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Languages */}
              {candidateData?.languages && candidateData.languages.length > 0 && (
                <div className="card">
                  <div className="flex items-center gap-2 mb-4">
                    <Languages className="w-5 h-5 text-purple-600" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Languages ({candidateData.languages.length})
                    </h3>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {candidateData.languages.map((lang: any) => (
                      <div key={lang.id} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <p className="font-medium text-gray-900 dark:text-white text-sm mb-1">{lang.language_name}</p>
                        <span className={`inline-block px-2 py-0.5 text-xs rounded ${getProficiencyColor(lang.proficiency_level)}`}>
                          {lang.proficiency_level || 'Not specified'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Skills Tab */}
        {activeTab === 'skills' && (
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Code className="w-5 h-5" />
              Skills ({candidateData?.skills?.length || 0})
            </h2>
            {candidateData?.skills && candidateData.skills.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {candidateData.skills.map((skill: any) => (
                  <div key={skill.id} className="p-4 bg-gradient-to-r from-gray-50 to-white dark:from-gray-700 dark:to-gray-800 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">{skill.skill_name}</h3>
                        {skill.skill_type && (
                          <p className="text-sm text-gray-600 dark:text-gray-400">{skill.skill_type}</p>
                        )}
                      </div>
                      <span className={`px-2 py-1 text-xs rounded ${getProficiencyColor(skill.proficiency_level)}`}>
                        {skill.proficiency_level || 'N/A'}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-3 text-xs text-gray-600 dark:text-gray-400">
                      {skill.years_of_experience && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {skill.years_of_experience} yrs
                        </span>
                      )}
                      {skill.last_used_date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          Last used: {formatDate(skill.last_used_date)}
                        </span>
                      )}
                      {skill.certification_name && (
                        <span className="flex items-center gap-1">
                          <Award className="w-3 h-3" />
                          Certified
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center py-8 text-gray-500 dark:text-gray-400">No skills added yet</p>
            )}
          </div>
        )}

        {/* Experience Tab */}
        {activeTab === 'experience' && (
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Briefcase className="w-5 h-5" />
              Work Experience ({candidateData?.work_experiences?.length || 0})
            </h2>
            {candidateData?.work_experiences && candidateData.work_experiences.length > 0 ? (
              <div className="space-y-6">
                {candidateData.work_experiences.map((exp: any) => (
                  <div key={exp.id} className="relative pl-8 pb-6 border-l-2 border-gray-200 dark:border-gray-700 last:border-l-0 last:pb-0">
                    {/* Timeline dot */}
                    <div className="absolute left-0 top-0 -ml-[9px] w-4 h-4 rounded-full bg-primary-500 border-4 border-white dark:border-gray-900"></div>
                    
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-5">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{exp.job_title}</h3>
                          <p className="text-primary-600 dark:text-primary-400 font-medium">{exp.company_name}</p>
                        </div>
                        {exp.is_current_job && (
                          <span className="px-3 py-1 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 text-xs font-medium rounded-full">
                            Current
                          </span>
                        )}
                      </div>
                      
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {formatDate(exp.start_date)} - {formatDate(exp.end_date)}
                        </span>
                        {exp.company_location && (
                          <span className="flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {exp.company_location}
                          </span>
                        )}
                        {exp.employment_type && (
                          <span className="flex items-center gap-1">
                            <Building2 className="w-4 h-4" />
                            {exp.employment_type}
                          </span>
                        )}
                      </div>

                      {exp.job_description && (
                        <p className="text-gray-700 dark:text-gray-300 mb-3">{exp.job_description}</p>
                      )}

                      {exp.key_achievements && (
                        <div className="mt-3">
                          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Key Achievements:</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{exp.key_achievements}</p>
                        </div>
                      )}

                      {exp.technologies_used && exp.technologies_used.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {exp.technologies_used.map((tech: string, techIdx: number) => (
                            <span key={techIdx} className="px-2 py-1 bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 rounded text-xs">
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center py-8 text-gray-500 dark:text-gray-400">No work experience added yet</p>
            )}
          </div>
        )}

        {/* Education Tab */}
        {activeTab === 'education' && (
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <GraduationCap className="w-5 h-5" />
              Education ({candidateData?.educations?.length || 0})
            </h2>
            {candidateData?.educations && candidateData.educations.length > 0 ? (
              <div className="space-y-4">
                {candidateData.educations.map((edu: any) => (
                  <div key={edu.id} className="p-5 bg-gradient-to-r from-gray-50 to-white dark:from-gray-700 dark:to-gray-800 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{edu.degree_type} in {edu.field_of_study}</h3>
                        <p className="text-primary-600 dark:text-primary-400 font-medium">{edu.institution_name}</p>
                      </div>
                      {edu.is_highest_degree && (
                        <span className="px-3 py-1 bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 text-xs font-medium rounded-full">
                          Highest
                        </span>
                      )}
                    </div>
                    
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-2">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {formatDate(edu.start_date)} - {formatDate(edu.end_date)}
                      </span>
                      {edu.institution_location && (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          {edu.institution_location}
                        </span>
                      )}
                      {edu.gpa && (
                        <span className="flex items-center gap-1">
                          <Star className="w-4 h-4" />
                          GPA: {edu.gpa} / {edu.gpa_scale || 4}
                        </span>
                      )}
                    </div>

                    {edu.achievements && (
                      <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">{edu.achievements}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center py-8 text-gray-500 dark:text-gray-400">No education records added yet</p>
            )}
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <FolderGit2 className="w-5 h-5" />
              Projects ({candidateData?.projects?.length || 0})
            </h2>
            {candidateData?.projects && candidateData.projects.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {candidateData.projects.map((project: any) => (
                  <div key={project.id} className="p-5 bg-gradient-to-r from-gray-50 to-white dark:from-gray-700 dark:to-gray-800 rounded-lg border border-gray-200 dark:border-gray-600">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{project.project_name}</h3>
                    
                    {project.role && (
                      <p className="text-sm text-primary-600 dark:text-primary-400 font-medium mb-2">{project.role}</p>
                    )}
                    
                    {project.description && (
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{project.description}</p>
                    )}

                    <div className="flex flex-wrap gap-2 text-xs text-gray-600 dark:text-gray-400 mb-3">
                      {project.start_date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatDate(project.start_date)} - {formatDate(project.end_date)}
                        </span>
                      )}
                    </div>

                    {project.technologies_used && project.technologies_used.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {project.technologies_used.map((tech: string, idx: number) => (
                          <span key={idx} className="px-2 py-1 bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 rounded text-xs">
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}

                    {(project.project_url || project.github_url) && (
                      <div className="flex gap-3 mt-3">
                        {project.project_url && (
                          <a
                            href={fixUrl(project.project_url)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 flex items-center gap-1"
                          >
                            <ExternalLink className="w-3 h-3" />
                            Demo
                          </a>
                        )}
                        {project.github_url && (
                          <a
                            href={fixUrl(project.github_url)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 flex items-center gap-1"
                          >
                            <Github className="w-3 h-3" />
                            Code
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center py-8 text-gray-500 dark:text-gray-400">No projects added yet</p>
            )}
          </div>
        )}

        {/* Certifications Tab */}
        {activeTab === 'certifications' && (
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Award className="w-5 h-5" />
              Certifications ({candidateData?.certifications?.length || 0})
            </h2>
            {candidateData?.certifications && candidateData.certifications.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {candidateData.certifications.map((cert: any) => (
                  <div key={cert.id} className="p-5 bg-gradient-to-r from-gray-50 to-white dark:from-gray-700 dark:to-gray-800 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Award className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{cert.certification_name}</h3>
                        <p className="text-sm text-primary-600 dark:text-primary-400 mb-2">{cert.issuing_organization}</p>
                        
                        <div className="flex flex-wrap gap-2 text-xs text-gray-600 dark:text-gray-400">
                          {cert.issue_date && (
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              Issued: {formatDate(cert.issue_date)}
                            </span>
                          )}
                          {cert.expiry_date && (
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              Expires: {formatDate(cert.expiry_date)}
                            </span>
                          )}
                        </div>

                        {cert.credential_id && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                            ID: {cert.credential_id}
                          </p>
                        )}

                        {cert.credential_url && (
                          <a
                            href={fixUrl(cert.credential_url)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 dark:text-primary-400 mt-2"
                          >
                            <ExternalLink className="w-3 h-3" />
                            View Certificate
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center py-8 text-gray-500 dark:text-gray-400">No certifications added yet</p>
            )}
          </div>
        )}

        {/* Resumes Tab */}
        {activeTab === 'resumes' && (
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <FileText className="w-5 h-5" />
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
                      <div className="flex items-start gap-4 flex-1">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FileText className="w-6 h-6 text-white" />
                        </div>

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
                            <span className="font-medium">Version {resume.version}</span>
                            <span className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {formatDateTime(resume.upload_date)}
                            </span>
                            {resume.file_size && (
                              <span className="flex items-center gap-1">
                                <FileText className="w-4 h-4" />
                                {(resume.file_size / 1024).toFixed(1)} KB
                              </span>
                            )}
                          </div>

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

                      <div className="flex flex-col items-end gap-3">
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

                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleDownloadResume(id!)}
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
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {/* Career Timeline */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Career Timeline
              </h2>
              {candidateData?.work_experiences && candidateData.work_experiences.length > 0 ? (
                <div className="space-y-4">
                  {/* Timeline visualization */}
                  <div className="relative">
                    {candidateData.work_experiences
                      .sort((a: any, b: any) => new Date(b.start_date || 0).getTime() - new Date(a.start_date || 0).getTime())
                      .map((exp: any) => {
                        const startYear = exp.start_date ? new Date(exp.start_date).getFullYear() : null;
                        const endYear = exp.end_date ? new Date(exp.end_date).getFullYear() : new Date().getFullYear();
                        const duration = endYear - (startYear || endYear);
                        
                        return (
                          <div key={exp.id} className="flex items-center gap-4 mb-4">
                            <div className="w-24 text-sm text-gray-600 dark:text-gray-400 text-right">
                              {startYear || 'Unknown'}
                            </div>
                            <div className="flex-1">
                              <div className="relative h-16 bg-gradient-to-r from-primary-100 to-primary-200 dark:from-primary-900 dark:to-primary-800 rounded-lg p-3">
                                <p className="font-semibold text-gray-900 dark:text-white text-sm">{exp.job_title}</p>
                                <p className="text-xs text-gray-600 dark:text-gray-400">{exp.company_name}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                                  {duration > 0 ? `${duration} year${duration > 1 ? 's' : ''}` : 'Less than 1 year'}
                                </p>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>
              ) : (
                <p className="text-center py-8 text-gray-500 dark:text-gray-400">No work experience data</p>
              )}
            </div>

            {/* Skills Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Skills by Category */}
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <PieChart className="w-5 h-5" />
                  Skills by Category
                </h2>
                {candidateData?.skills && candidateData.skills.length > 0 ? (
                  <div className="space-y-3">
                    {(() => {
                      const categories = candidateData.skills.reduce((acc: any, skill: any) => {
                        const cat = skill.skill_category || 'Uncategorized';
                        acc[cat] = (acc[cat] || 0) + 1;
                        return acc;
                      }, {});
                      
                      const total = candidateData.skills.length;
                      const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-yellow-500', 'bg-red-500', 'bg-pink-500'];
                      
                      return Object.entries(categories).map(([category, count]: any, idx) => (
                        <div key={category}>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{category}</span>
                            <span className="text-sm text-gray-600 dark:text-gray-400">{count} ({Math.round((count / total) * 100)}%)</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className={`${colors[idx % colors.length]} h-2 rounded-full transition-all`}
                              style={{ width: `${(count / total) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      ));
                    })()}
                  </div>
                ) : (
                  <p className="text-center py-8 text-gray-500 dark:text-gray-400">No skills data</p>
                )}
              </div>

              {/* Skills by Proficiency */}
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Skills by Proficiency
                </h2>
                {candidateData?.skills && candidateData.skills.length > 0 ? (
                  <div className="space-y-3">
                    {(() => {
                      const proficiencies = candidateData.skills.reduce((acc: any, skill: any) => {
                        const prof = skill.proficiency_level || 'Not Specified';
                        acc[prof] = (acc[prof] || 0) + 1;
                        return acc;
                      }, {});
                      
                      const total = candidateData.skills.length;
                      const order = ['Expert', 'Advanced', 'Intermediate', 'Beginner', 'Not Specified'];
                      const profColors: any = {
                        'Expert': 'bg-purple-500',
                        'Advanced': 'bg-blue-500',
                        'Intermediate': 'bg-green-500',
                        'Beginner': 'bg-yellow-500',
                        'Not Specified': 'bg-gray-500'
                      };
                      
                      return order
                        .filter(level => proficiencies[level])
                        .map((level) => {
                          const count = proficiencies[level];
                          return (
                            <div key={level}>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{level}</span>
                                <span className="text-sm text-gray-600 dark:text-gray-400">{count} ({Math.round((count / total) * 100)}%)</span>
                              </div>
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div 
                                  className={`${profColors[level]} h-2 rounded-full transition-all`}
                                  style={{ width: `${(count / total) * 100}%` }}
                                ></div>
                              </div>
                            </div>
                          );
                        });
                    })()}
                  </div>
                ) : (
                  <p className="text-center py-8 text-gray-500 dark:text-gray-400">No skills data</p>
                )}
              </div>
            </div>

            {/* Experience Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
                    <Briefcase className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Experience</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {candidateData?.work_experiences?.reduce((total: number, exp: any) => {
                        const start = exp.start_date ? new Date(exp.start_date) : null;
                        const end = exp.end_date ? new Date(exp.end_date) : new Date();
                        if (!start) return total;
                        const years = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 365);
                        return total + years;
                      }, 0).toFixed(1) || 0} years
                    </p>
                  </div>
                </div>
              </div>

              <div className="card bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
                    <Code className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Skills</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {candidateData?.skills?.length || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
                    <Award className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Certifications</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {candidateData?.certifications?.length || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Technology Stack */}
            {candidateData?.work_experiences?.some((exp: any) => exp.technologies_used?.length > 0) && (
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  Technology Stack Experience
                </h2>
                <div className="flex flex-wrap gap-2">
                  {(() => {
                    const allTechs = candidateData.work_experiences
                      .filter((exp: any) => exp.technologies_used)
                      .flatMap((exp: any) => exp.technologies_used);
                    
                    const techCount = allTechs.reduce((acc: any, tech: string) => {
                      acc[tech] = (acc[tech] || 0) + 1;
                      return acc;
                    }, {});
                    
                    return Object.entries(techCount)
                      .sort((a: any, b: any) => b[1] - a[1])
                      .map(([tech, count]: any) => (
                        <span 
                          key={tech}
                          className="px-3 py-1.5 bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 rounded-full text-sm font-medium"
                        >
                          {tech} {count > 1 && <span className="text-xs opacity-70">×{count}</span>}
                        </span>
                      ));
                  })()}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default CandidateDetailEnhanced
