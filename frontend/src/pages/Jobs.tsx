import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { jobApi } from '@/lib/api';
import { Briefcase, MapPin, DollarSign, Plus, Calendar, Users, Edit, Trash2, X, Building2, Clock, TrendingUp } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE_URL}/api/v1`;

interface Job {
  id: string;
  title: string;
  department: string;
  location: string;
  employment_type: string;
  experience_level: string;
  salary_range_min: number;
  salary_range_max: number;
  status: string;
  required_skills: string[];
  description: string;
  requirements: string;
  responsibilities: string;
  benefits: string;
  posted_date: string;
  deadline: string;
  number_of_positions: number;
}

const Jobs = () => {
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    title: '',
    department: '',
    location: '',
    employment_type: 'Full-time',
    experience_level: 'Mid-Level',
    salary_range_min: 0,
    salary_range_max: 0,
    status: 'open',
    required_skills: '',
    description: '',
    requirements: '',
    responsibilities: '',
    benefits: '',
    deadline: '',
    number_of_positions: 1
  });

  const { data, isLoading } = useQuery({
    queryKey: ['jobs', statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      const response = await axios.get(`${API_URL}/jobs/?${params}`);
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: async (jobData: any) => {
      const response = await axios.post(`${API_URL}/jobs/`, {
        ...jobData,
        required_skills: jobData.required_skills.split(',').map((s: string) => s.trim()).filter(Boolean)
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setShowCreateModal(false);
      resetForm();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create job');
    }
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await axios.put(`${API_URL}/jobs/${id}`, {
        ...data,
        required_skills: typeof data.required_skills === 'string' 
          ? data.required_skills.split(',').map((s: string) => s.trim()).filter(Boolean)
          : data.required_skills
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setShowEditModal(false);
      resetForm();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to update job');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await axios.delete(`${API_URL}/jobs/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to delete job');
    }
  });

  const resetForm = () => {
    setFormData({
      title: '',
      department: '',
      location: '',
      employment_type: 'Full-time',
      experience_level: 'Mid-Level',
      salary_range_min: 0,
      salary_range_max: 0,
      status: 'open',
      required_skills: '',
      description: '',
      requirements: '',
      responsibilities: '',
      benefits: '',
      deadline: '',
      number_of_positions: 1
    });
    setSelectedJob(null);
    setError('');
  };

  const openEditModal = (job: Job) => {
    setSelectedJob(job);
    setFormData({
      title: job.title,
      department: job.department || '',
      location: job.location || '',
      employment_type: job.employment_type || 'Full-time',
      experience_level: job.experience_level || 'Mid-Level',
      salary_range_min: job.salary_range_min || 0,
      salary_range_max: job.salary_range_max || 0,
      status: job.status,
      required_skills: job.required_skills?.join(', ') || '',
      description: job.description || '',
      requirements: job.requirements || '',
      responsibilities: job.responsibilities || '',
      benefits: job.benefits || '',
      deadline: job.deadline || '',
      number_of_positions: job.number_of_positions || 1
    });
    setShowEditModal(true);
  };

  const handleCreate = () => {
    createMutation.mutate(formData);
  };

  const handleUpdate = () => {
    if (selectedJob) {
      updateMutation.mutate({ id: selectedJob.id, data: formData });
    }
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this job?')) {
      deleteMutation.mutate(id);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'open': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      'closed': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      'on_hold': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      'draft': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    };
    return colors[status] || colors['draft'];
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <Briefcase className="w-8 h-8 mr-3 text-blue-600" />
            Job Openings
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage job postings and track applications
          </p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowCreateModal(true);
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Create Job
        </button>
      </div>

      {/* Filters */}
      <div className="mb-6 bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter by Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="">All Status</option>
            <option value="open">Open</option>
            <option value="closed">Closed</option>
            <option value="on_hold">On Hold</option>
            <option value="draft">Draft</option>
          </select>
          {statusFilter && (
            <button
              onClick={() => setStatusFilter('')}
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/20 border border-red-400 text-red-700 dark:text-red-400 rounded-lg">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : data && data.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <Briefcase className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No jobs found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Create your first job posting to get started
          </p>
          <button
            onClick={() => {
              resetForm();
              setShowCreateModal(true);
            }}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Job
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data?.map((job: Job) => (
            <div key={job.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="bg-blue-100 dark:bg-blue-900 rounded-full p-3">
                  <Briefcase className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(job.status)}`}>
                  {job.status.replace('_', ' ').toUpperCase()}
                </span>
              </div>

              <Link to={`/jobs/${job.id}`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 hover:text-blue-600">
                  {job.title}
                </h3>
              </Link>

              {job.department && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <Building2 className="w-4 h-4" />
                  <span>{job.department}</span>
                </div>
              )}

              {job.location && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <MapPin className="w-4 h-4" />
                  <span>{job.location}</span>
                </div>
              )}

              {(job.salary_range_min || job.salary_range_max) && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <DollarSign className="w-4 h-4" />
                  <span>
                    ${job.salary_range_min?.toLocaleString()} - ${job.salary_range_max?.toLocaleString()}
                  </span>
                </div>
              )}

              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                <Clock className="w-4 h-4" />
                <span>{job.employment_type}</span>
              </div>

              {job.experience_level && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <TrendingUp className="w-4 h-4" />
                  <span>{job.experience_level}</span>
                </div>
              )}

              {job.number_of_positions > 1 && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <Users className="w-4 h-4" />
                  <span>{job.number_of_positions} positions</span>
                </div>
              )}

              {job.deadline && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                  <Calendar className="w-4 h-4" />
                  <span>Deadline: {new Date(job.deadline).toLocaleDateString()}</span>
                </div>
              )}

              {job.required_skills && job.required_skills.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {job.required_skills.slice(0, 3).map((skill, idx) => (
                    <span key={idx} className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                      {skill}
                    </span>
                  ))}
                  {job.required_skills.length > 3 && (
                    <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                      +{job.required_skills.length - 3} more
                    </span>
                  )}
                </div>
              )}

              <div className="flex gap-2 pt-4 border-t dark:border-gray-700">
                <button
                  onClick={() => openEditModal(job)}
                  className="flex-1 flex items-center justify-center px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(job.id)}
                  className="flex-1 flex items-center justify-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Job Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Create New Job</h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Employment Type
                  </label>
                  <select
                    value={formData.employment_type}
                    onChange={(e) => setFormData({ ...formData, employment_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Full-time</option>
                    <option>Part-time</option>
                    <option>Contract</option>
                    <option>Internship</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Experience Level
                  </label>
                  <select
                    value={formData.experience_level}
                    onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Entry-Level</option>
                    <option>Mid-Level</option>
                    <option>Senior-Level</option>
                    <option>Lead</option>
                    <option>Executive</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Salary Min
                  </label>
                  <input
                    type="number"
                    value={formData.salary_range_min}
                    onChange={(e) => setFormData({ ...formData, salary_range_min: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Salary Max
                  </label>
                  <input
                    type="number"
                    value={formData.salary_range_max}
                    onChange={(e) => setFormData({ ...formData, salary_range_max: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Number of Positions
                  </label>
                  <input
                    type="number"
                    value={formData.number_of_positions}
                    onChange={(e) => setFormData({ ...formData, number_of_positions: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    min="1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Application Deadline
                  </label>
                  <input
                    type="date"
                    value={formData.deadline}
                    onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="open">Open</option>
                    <option value="closed">Closed</option>
                    <option value="on_hold">On Hold</option>
                    <option value="draft">Draft</option>
                  </select>
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Required Skills (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={formData.required_skills}
                    onChange={(e) => setFormData({ ...formData, required_skills: e.target.value })}
                    placeholder="e.g., Python, React, AWS"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Job Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Requirements
                  </label>
                  <textarea
                    value={formData.requirements}
                    onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreate}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create Job
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Job Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Edit Job</h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="open">Open</option>
                    <option value="closed">Closed</option>
                    <option value="on_hold">On Hold</option>
                    <option value="draft">Draft</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdate}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Update Job
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Jobs
