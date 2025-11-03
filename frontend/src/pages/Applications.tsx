import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { FileText, User, Briefcase, Calendar, TrendingUp, Filter, X, Plus, Trash2, Edit } from 'lucide-react';
import axios from 'axios';

const getAPIBaseURL = () => {
  if (import.meta.env.PROD) {
    return window.location.origin
  }
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}

const API_BASE_URL = getAPIBaseURL();
const API_URL = `${API_BASE_URL}/api/v1`;

interface Application {
  id: string;
  candidate_id: string;
  job_id: string;
  status: string;
  application_date: string;
  match_score: number;
  notes: string;
  interview_date: string;
  offer_details: string;
  rejection_reason: string;
}

const Applications = () => {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [error, setError] = useState('');
  const [candidates, setCandidates] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  
  const [formData, setFormData] = useState({
    candidate_id: '',
    job_id: '',
    status: 'submitted',
    notes: '',
    interview_date: '',
    offer_details: '',
    rejection_reason: ''
  });

  // Fetch candidates and jobs for dropdowns
  useState(() => {
    const fetchData = async () => {
      try {
        const [candidatesRes, jobsRes] = await Promise.all([
          axios.get(`${API_URL}/candidates/?limit=1000`),
          axios.get(`${API_URL}/jobs/?limit=1000`)
        ]);
        setCandidates(candidatesRes.data);
        setJobs(jobsRes.data);
      } catch (err) {
        console.error('Failed to fetch data:', err);
      }
    };
    fetchData();
  });

  const { data, isLoading } = useQuery({
    queryKey: ['applications', statusFilter],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/applications/`);
      let apps = response.data;
      if (statusFilter) {
        apps = apps.filter((app: Application) => app.status === statusFilter);
      }
      
      // Fetch related candidate and job data
      const enrichedApps = await Promise.all(
        apps.map(async (app: Application) => {
          try {
            const [candidateRes, jobRes] = await Promise.all([
              axios.get(`${API_URL}/candidates/${app.candidate_id}`),
              axios.get(`${API_URL}/jobs/${app.job_id}`)
            ]);
            return {
              ...app,
              candidate: candidateRes.data,
              job: jobRes.data
            };
          } catch {
            return app;
          }
        })
      );
      
      return enrichedApps;
    },
  });

  const createMutation = useMutation({
    mutationFn: async (appData: any) => {
      const response = await axios.post(`${API_URL}/applications/`, appData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      setShowCreateModal(false);
      resetForm();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create application');
    }
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: any }) => {
      const response = await axios.put(`${API_URL}/applications/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      setShowEditModal(false);
      resetForm();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to update application');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await axios.delete(`${API_URL}/applications/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to delete application');
    }
  });

  const resetForm = () => {
    setFormData({
      candidate_id: '',
      job_id: '',
      status: 'submitted',
      notes: '',
      interview_date: '',
      offer_details: '',
      rejection_reason: ''
    });
    setSelectedApp(null);
    setError('');
  };

  const openEditModal = (app: Application) => {
    setSelectedApp(app);
    setFormData({
      candidate_id: app.candidate_id,
      job_id: app.job_id,
      status: app.status,
      notes: app.notes || '',
      interview_date: app.interview_date || '',
      offer_details: app.offer_details || '',
      rejection_reason: app.rejection_reason || ''
    });
    setShowEditModal(true);
  };

  const handleCreate = () => {
    createMutation.mutate(formData);
  };

  const handleUpdate = () => {
    if (selectedApp) {
      updateMutation.mutate({ id: selectedApp.id, data: formData });
    }
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this application?')) {
      deleteMutation.mutate(id);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'submitted': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      'under_review': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      'interview_scheduled': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      'interviewed': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
      'offer_extended': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      'hired': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300',
      'rejected': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      'withdrawn': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    };
    return colors[status] || colors['submitted'];
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <FileText className="w-8 h-8 mr-3 text-blue-600" />
            Job Applications
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Track and manage candidate applications
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
          Create Application
        </button>
      </div>

      {/* Filters */}
      <div className="mb-6 bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="">All Status</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="interview_scheduled">Interview Scheduled</option>
            <option value="interviewed">Interviewed</option>
            <option value="offer_extended">Offer Extended</option>
            <option value="hired">Hired</option>
            <option value="rejected">Rejected</option>
            <option value="withdrawn">Withdrawn</option>
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
      ) : !data || data.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <FileText className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No applications found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Start tracking candidate applications
          </p>
          <button
            onClick={() => {
              resetForm();
              setShowCreateModal(true);
            }}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Application
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700 border-b dark:border-gray-600">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Candidate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Job Position
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Match Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Applied Date
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {data.map((app: any) => (
                <tr key={app.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-blue-600 dark:text-blue-300" />
                      </div>
                      <div className="ml-4">
                        <Link
                          to={`/candidates/${app.candidate_id}`}
                          className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          {app.candidate?.first_name} {app.candidate?.last_name}
                        </Link>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {app.candidate?.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <Link
                      to={`/jobs/${app.job_id}`}
                      className="flex items-center text-sm text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      <Briefcase className="w-4 h-4 mr-2" />
                      {app.job?.title || 'Unknown Job'}
                    </Link>
                    {app.job?.location && (
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {app.job.location}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(app.status)}`}>
                      {app.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {app.match_score ? (
                      <div className="flex items-center">
                        <TrendingUp className={`w-4 h-4 mr-2 ${getMatchScoreColor(app.match_score)}`} />
                        <span className={`text-sm font-semibold ${getMatchScoreColor(app.match_score)}`}>
                          {app.match_score}%
                        </span>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <Calendar className="w-4 h-4 mr-2" />
                      {new Date(app.application_date).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => openEditModal(app)}
                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                        title="Edit application"
                      >
                        <Edit className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(app.id)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                        title="Delete application"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Application Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Create Application</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Candidate *
                  </label>
                  <select
                    value={formData.candidate_id}
                    onChange={(e) => setFormData({ ...formData, candidate_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    required
                  >
                    <option value="">Select Candidate</option>
                    {candidates.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.first_name} {c.last_name} ({c.email})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Job Position *
                  </label>
                  <select
                    value={formData.job_id}
                    onChange={(e) => setFormData({ ...formData, job_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    required
                  >
                    <option value="">Select Job</option>
                    {jobs.map((j) => (
                      <option key={j.id} value={j.id}>
                        {j.title} - {j.location || 'Remote'}
                      </option>
                    ))}
                  </select>
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
                    <option value="submitted">Submitted</option>
                    <option value="under_review">Under Review</option>
                    <option value="interview_scheduled">Interview Scheduled</option>
                    <option value="interviewed">Interviewed</option>
                    <option value="offer_extended">Offer Extended</option>
                    <option value="hired">Hired</option>
                    <option value="rejected">Rejected</option>
                    <option value="withdrawn">Withdrawn</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Notes
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
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
                  Create Application
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Application Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Edit Application</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="submitted">Submitted</option>
                    <option value="under_review">Under Review</option>
                    <option value="interview_scheduled">Interview Scheduled</option>
                    <option value="interviewed">Interviewed</option>
                    <option value="offer_extended">Offer Extended</option>
                    <option value="hired">Hired</option>
                    <option value="rejected">Rejected</option>
                    <option value="withdrawn">Withdrawn</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Interview Date
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.interview_date}
                    onChange={(e) => setFormData({ ...formData, interview_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Notes
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
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
                  Update Application
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Applications
