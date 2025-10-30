import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { candidateApi } from '@/lib/api';
import { Save, ArrowLeft, Plus, Trash2, AlertCircle, CheckCircle, User, Mail, Phone, MapPin, Briefcase, GraduationCap, Award, Languages, Settings } from 'lucide-react';

interface Skill {
  id?: string;
  skill_name: string;
  proficiency_level: string;
  years_of_experience?: number;
  category?: string;
}

interface WorkExperience {
  id?: string;
  company_name: string;
  position: string;
  start_date: string;
  end_date?: string;
  responsibilities?: string;
  achievements?: string;
  employment_type?: string;
}

interface Education {
  id?: string;
  institution_name: string;
  degree: string;
  field_of_study?: string;
  start_date: string;
  end_date?: string;
  grade?: string;
}

interface Project {
  id?: string;
  project_name: string;
  description?: string;
  technologies_used?: string[];
  role?: string;
  start_date?: string;
  end_date?: string;
  project_url?: string;
}

interface Certification {
  id?: string;
  certification_name: string;
  issuing_organization: string;
  issue_date?: string;
  expiry_date?: string;
  credential_id?: string;
  credential_url?: string;
}

interface Language {
  id?: string;
  language_name: string;
  proficiency_level: string;
}

interface CandidateFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  current_location: string;
  professional_summary: string;
  career_level: string;
  years_of_experience: number;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  preferred_locations: string[];
  open_to_relocation: boolean;
  willing_to_travel: boolean;
  expected_salary_min: number;
  expected_salary_max: number;
  salary_currency: string;
  availability: string;
  notice_period_days: number;
}

export default function EditCandidate() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [activeSection, setActiveSection] = useState('basic');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form Data State
  const [formData, setFormData] = useState<CandidateFormData>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    current_location: '',
    professional_summary: '',
    career_level: '',
    years_of_experience: 0,
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
    preferred_locations: [],
    open_to_relocation: false,
    willing_to_travel: false,
    expected_salary_min: 0,
    expected_salary_max: 0,
    salary_currency: 'USD',
    availability: '',
    notice_period_days: 0
  });

  // Related Data State
  const [skills, setSkills] = useState<Skill[]>([]);
  const [workExperiences, setWorkExperiences] = useState<WorkExperience[]>([]);
  const [education, setEducation] = useState<Education[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [certifications, setCertifications] = useState<Certification[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);

  // Load candidate data
  const { data: candidate, isLoading, error } = useQuery({
    queryKey: ['candidate', id],
    queryFn: () => candidateApi.getById(id!),
    enabled: !!id,
    refetchOnWindowFocus: false
  });

  // Update mutation
  const updateCandidateMutation = useMutation({
    mutationFn: async (data: any) => {
      const token = localStorage.getItem('access_token');
      const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/candidates/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error('Failed to update candidate');
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidate', id] });
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setTimeout(() => {
        navigate(`/candidates/${id}`);
      }, 2000);
    },
    onError: (error) => {
      console.error('Update error:', error);
      setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' });
    }
  });

  // Load data into form when candidate data is available
  useEffect(() => {
    if (candidate?.data) {
      const candidateData = candidate.data;
      console.log('Loading candidate data:', candidateData);
      
      setFormData({
        first_name: candidateData.first_name || '',
        last_name: candidateData.last_name || '',
        email: candidateData.email || '',
        phone: candidateData.phone || '',
        current_location: candidateData.current_location || '',
        professional_summary: candidateData.professional_summary || '',
        career_level: candidateData.career_level || '',
        years_of_experience: candidateData.years_of_experience || 0,
        linkedin_url: candidateData.linkedin_url || '',
        github_url: candidateData.github_url || '',
        portfolio_url: candidateData.portfolio_url || '',
        preferred_locations: Array.isArray(candidateData.preferred_locations) ? candidateData.preferred_locations : [],
        open_to_relocation: candidateData.open_to_relocation || false,
        willing_to_travel: candidateData.willing_to_travel || false,
        expected_salary_min: candidateData.expected_salary_min || 0,
        expected_salary_max: candidateData.expected_salary_max || 0,
        salary_currency: candidateData.salary_currency || 'USD',
        availability: candidateData.availability || '',
        notice_period_days: candidateData.notice_period_days || 0
      });

      setSkills(candidateData.skills || []);
      setWorkExperiences(candidateData.work_experiences || []);
      setEducation(candidateData.education || []);
      setProjects(candidateData.projects || []);
      setCertifications(candidateData.certifications || []);
      setLanguages(candidateData.languages || []);
    } else if (candidate && typeof candidate === 'object' && !candidate.data) {
      // Handle case where candidate is returned directly (not wrapped in data)
      console.log('Loading candidate data (direct):', candidate);
      
      setFormData({
        first_name: (candidate as any).first_name || '',
        last_name: (candidate as any).last_name || '',
        email: (candidate as any).email || '',
        phone: (candidate as any).phone || '',
        current_location: (candidate as any).current_location || '',
        professional_summary: (candidate as any).professional_summary || '',
        career_level: (candidate as any).career_level || '',
        years_of_experience: (candidate as any).years_of_experience || 0,
        linkedin_url: (candidate as any).linkedin_url || '',
        github_url: (candidate as any).github_url || '',
        portfolio_url: (candidate as any).portfolio_url || '',
        preferred_locations: Array.isArray((candidate as any).preferred_locations) ? (candidate as any).preferred_locations : [],
        open_to_relocation: (candidate as any).open_to_relocation || false,
        willing_to_travel: (candidate as any).willing_to_travel || false,
        expected_salary_min: (candidate as any).expected_salary_min || 0,
        expected_salary_max: (candidate as any).expected_salary_max || 0,
        salary_currency: (candidate as any).salary_currency || 'USD',
        availability: (candidate as any).availability || '',
        notice_period_days: (candidate as any).notice_period_days || 0
      });

      setSkills((candidate as any).skills || []);
      setWorkExperiences((candidate as any).work_experiences || []);
      setEducation((candidate as any).education || []);
      setProjects((candidate as any).projects || []);
      setCertifications((candidate as any).certifications || []);
      setLanguages((candidate as any).languages || []);
    }
  }, [candidate]);

  const handleSave = async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    setMessage(null);

    try {
      // Prepare complete data payload
      const completeData = {
        ...formData,
        skills,
        work_experiences: workExperiences,
        education,
        projects,
        certifications,
        languages
      };

      await updateCandidateMutation.mutateAsync(completeData);
    } catch (error) {
      console.error('Save error:', error);
      setMessage({ type: 'error', text: 'Failed to save changes. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Add/Remove handlers
  const addSkill = () => {
    setSkills([...skills, { 
      skill_name: '', 
      proficiency_level: 'Intermediate', 
      years_of_experience: 0, 
      category: 'Technical' 
    }]);
  };

  const removeSkill = (index: number) => {
    setSkills(skills.filter((_, i) => i !== index));
  };

  const addWorkExperience = () => {
    setWorkExperiences([...workExperiences, { 
      company_name: '', 
      position: '', 
      start_date: '', 
      employment_type: 'Full-time' 
    }]);
  };

  const removeWorkExperience = (index: number) => {
    setWorkExperiences(workExperiences.filter((_, i) => i !== index));
  };

  const addEducation = () => {
    setEducation([...education, { 
      institution_name: '', 
      degree: '', 
      start_date: '' 
    }]);
  };

  const removeEducation = (index: number) => {
    setEducation(education.filter((_, i) => i !== index));
  };

  const addProject = () => {
    setProjects([...projects, { 
      project_name: '', 
      technologies_used: [] 
    }]);
  };

  const removeProject = (index: number) => {
    setProjects(projects.filter((_, i) => i !== index));
  };

  const addCertification = () => {
    setCertifications([...certifications, { 
      certification_name: '', 
      issuing_organization: '' 
    }]);
  };

  const removeCertification = (index: number) => {
    setCertifications(certifications.filter((_, i) => i !== index));
  };

  const addLanguage = () => {
    setLanguages([...languages, { 
      language_name: '', 
      proficiency_level: 'Intermediate' 
    }]);
  };

  const removeLanguage = (index: number) => {
    setLanguages(languages.filter((_, i) => i !== index));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading candidate data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">Failed to load candidate data</p>
          <button 
            onClick={() => navigate('/candidates')}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Back to Candidates
          </button>
        </div>
      </div>
    );
  }

  const sections = [
    { id: 'basic', label: 'Basic Information', icon: User },
    { id: 'skills', label: 'Skills', icon: Settings },
    { id: 'experience', label: 'Work Experience', icon: Briefcase },
    { id: 'education', label: 'Education', icon: GraduationCap },
    { id: 'projects', label: 'Projects', icon: Settings },
    { id: 'certifications', label: 'Certifications', icon: Award },
    { id: 'languages', label: 'Languages', icon: Languages }
  ];

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(`/candidates/${id}`)}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">
              Edit Candidate Profile
            </h1>
            <p className="text-gray-600 mt-1">
              {formData.first_name} {formData.last_name}
            </p>
          </div>
        </div>
        <button
          onClick={handleSave}
          disabled={isSubmitting}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <Save className="w-5 h-5" />
          {isSubmitting ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Message */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
          message.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5 text-green-500" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-500" />
          )}
          <span className={message.type === 'success' ? 'text-green-700' : 'text-red-700'}>
            {message.text}
          </span>
          <button onClick={() => setMessage(null)} className="ml-auto text-gray-500">✕</button>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-1 overflow-x-auto">
          {sections.map((section) => {
            const IconComponent = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`px-6 py-3 font-medium transition border-b-2 whitespace-nowrap flex items-center gap-2 ${
                  activeSection === section.id
                    ? 'text-blue-600 border-blue-600'
                    : 'text-gray-600 border-transparent hover:text-gray-800'
                }`}
              >
                <IconComponent className="w-4 h-4" />
                {section.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {/* Basic Information */}
        {activeSection === 'basic' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">First Name *</label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Last Name *</label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Current Location</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={formData.current_location}
                  onChange={(e) => setFormData({...formData, current_location: e.target.value})}
                  className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="City, Country"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Professional Summary</label>
              <textarea
                value={formData.professional_summary}
                onChange={(e) => setFormData({...formData, professional_summary: e.target.value})}
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Brief overview of your experience and skills..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Career Level</label>
                <select
                  value={formData.career_level}
                  onChange={(e) => setFormData({...formData, career_level: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">-- Select --</option>
                  <option value="Entry">Entry Level</option>
                  <option value="Mid">Mid Level</option>
                  <option value="Senior">Senior Level</option>
                  <option value="Lead">Lead</option>
                  <option value="Manager">Manager</option>
                  <option value="Director">Director</option>
                  <option value="Executive">Executive</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Years of Experience</label>
                <input
                  type="number"
                  value={formData.years_of_experience}
                  onChange={(e) => setFormData({...formData, years_of_experience: parseInt(e.target.value) || 0})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">LinkedIn URL</label>
                <input
                  type="url"
                  value={formData.linkedin_url}
                  onChange={(e) => setFormData({...formData, linkedin_url: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://linkedin.com/in/..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">GitHub URL</label>
                <input
                  type="url"
                  value={formData.github_url}
                  onChange={(e) => setFormData({...formData, github_url: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://github.com/..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Portfolio URL</label>
                <input
                  type="url"
                  value={formData.portfolio_url}
                  onChange={(e) => setFormData({...formData, portfolio_url: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://..."
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="relocation"
                  checked={formData.open_to_relocation}
                  onChange={(e) => setFormData({...formData, open_to_relocation: e.target.checked})}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="relocation" className="text-sm text-gray-700">Open to relocation</label>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="travel"
                  checked={formData.willing_to_travel}
                  onChange={(e) => setFormData({...formData, willing_to_travel: e.target.checked})}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="travel" className="text-sm text-gray-700">Willing to travel</label>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Expected Salary (Min)</label>
                <input
                  type="number"
                  value={formData.expected_salary_min}
                  onChange={(e) => setFormData({...formData, expected_salary_min: parseInt(e.target.value) || 0})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Expected Salary (Max)</label>
                <input
                  type="number"
                  value={formData.expected_salary_max}
                  onChange={(e) => setFormData({...formData, expected_salary_max: parseInt(e.target.value) || 0})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                <select
                  value={formData.salary_currency}
                  onChange={(e) => setFormData({...formData, salary_currency: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="SAR">SAR</option>
                  <option value="AED">AED</option>
                  <option value="EGP">EGP</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Availability</label>
                <select
                  value={formData.availability}
                  onChange={(e) => setFormData({...formData, availability: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">-- Select --</option>
                  <option value="Immediate">Immediate</option>
                  <option value="2 weeks">2 weeks</option>
                  <option value="1 month">1 month</option>
                  <option value="2 months">2 months</option>
                  <option value="3 months">3 months</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Notice Period (days)</label>
                <input
                  type="number"
                  value={formData.notice_period_days}
                  onChange={(e) => setFormData({...formData, notice_period_days: parseInt(e.target.value) || 0})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0"
                />
              </div>
            </div>
          </div>
        )}

        {/* Skills Section */}
        {activeSection === 'skills' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Skills</h3>
              <button
                onClick={addSkill}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Skill
              </button>
            </div>
            {skills.map((skill, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Skill Name</label>
                      <input
                        type="text"
                        value={skill.skill_name}
                        onChange={(e) => {
                          const newSkills = [...skills];
                          newSkills[index].skill_name = e.target.value;
                          setSkills(newSkills);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., Python, React, Project Management"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Proficiency Level</label>
                      <select
                        value={skill.proficiency_level}
                        onChange={(e) => {
                          const newSkills = [...skills];
                          newSkills[index].proficiency_level = e.target.value;
                          setSkills(newSkills);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="Beginner">Beginner</option>
                        <option value="Intermediate">Intermediate</option>
                        <option value="Advanced">Advanced</option>
                        <option value="Expert">Expert</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Years of Experience</label>
                      <input
                        type="number"
                        value={skill.years_of_experience || 0}
                        onChange={(e) => {
                          const newSkills = [...skills];
                          newSkills[index].years_of_experience = parseInt(e.target.value) || 0;
                          setSkills(newSkills);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        min="0"
                      />
                    </div>
                  </div>
                  <button
                    onClick={() => removeSkill(index)}
                    className="ml-2 p-2 text-red-500 hover:bg-red-50 rounded-lg"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            {skills.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No skills added yet. Click "Add Skill" to add your first skill.
              </div>
            )}
          </div>
        )}

        {/* Work Experience Section */}
        {activeSection === 'experience' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Work Experience</h3>
              <button
                onClick={addWorkExperience}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Experience
              </button>
            </div>
            {workExperiences.map((exp, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                        <input
                          type="text"
                          value={exp.company_name}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].company_name = e.target.value;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
                        <input
                          type="text"
                          value={exp.position}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].position = e.target.value;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                        <input
                          type="date"
                          value={exp.start_date}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].start_date = e.target.value;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                        <input
                          type="date"
                          value={exp.end_date || ''}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].end_date = e.target.value || undefined;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Employment Type</label>
                        <select
                          value={exp.employment_type || 'Full-time'}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].employment_type = e.target.value;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="Full-time">Full-time</option>
                          <option value="Part-time">Part-time</option>
                          <option value="Contract">Contract</option>
                          <option value="Freelance">Freelance</option>
                          <option value="Internship">Internship</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Responsibilities</label>
                      <textarea
                        value={exp.responsibilities || ''}
                        onChange={(e) => {
                          const newExps = [...workExperiences];
                          newExps[index].responsibilities = e.target.value;
                          setWorkExperiences(newExps);
                        }}
                        rows={3}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <button
                    onClick={() => removeWorkExperience(index)}
                    className="ml-2 p-2 text-red-500 hover:bg-red-50 rounded-lg"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            {workExperiences.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No work experience added yet. Click "Add Experience" to add your first job.
              </div>
            )}
          </div>
        )}

        {/* Education Section */}
        {activeSection === 'education' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Education</h3>
              <button
                onClick={addEducation}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Education
              </button>
            </div>
            {education.map((edu, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Institution Name</label>
                        <input
                          type="text"
                          value={edu.institution_name}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].institution_name = e.target.value;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Degree</label>
                        <input
                          type="text"
                          value={edu.degree}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].degree = e.target.value;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., Bachelor's, Master's, PhD"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Field of Study</label>
                        <input
                          type="text"
                          value={edu.field_of_study || ''}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].field_of_study = e.target.value;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                        <input
                          type="date"
                          value={edu.start_date}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].start_date = e.target.value;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Graduation Date</label>
                        <input
                          type="date"
                          value={edu.end_date || ''}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].end_date = e.target.value || undefined;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Grade/GPA</label>
                      <input
                        type="text"
                        value={edu.grade || ''}
                        onChange={(e) => {
                          const newEdu = [...education];
                          newEdu[index].grade = e.target.value;
                          setEducation(newEdu);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., Excellent, Distinction, 3.8 GPA"
                      />
                    </div>
                  </div>
                  <button
                    onClick={() => removeEducation(index)}
                    className="ml-2 p-2 text-red-500 hover:bg-red-50 rounded-lg"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            {education.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No education added yet. Click "Add Education" to add your first qualification.
              </div>
            )}
          </div>
        )}

        {/* Projects Section */}
        {activeSection === 'projects' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Projects</h3>
              <button
                onClick={addProject}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Project
              </button>
            </div>
            {projects.map((proj, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Project Name</label>
                        <input
                          type="text"
                          value={proj.project_name}
                          onChange={(e) => {
                            const newProj = [...projects];
                            newProj[index].project_name = e.target.value;
                            setProjects(newProj);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                        <input
                          type="text"
                          value={proj.role || ''}
                          onChange={(e) => {
                            const newProj = [...projects];
                            newProj[index].role = e.target.value;
                            setProjects(newProj);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="e.g., Lead Developer, Project Manager"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <textarea
                        value={proj.description || ''}
                        onChange={(e) => {
                          const newProj = [...projects];
                          newProj[index].description = e.target.value;
                          setProjects(newProj);
                        }}
                        rows={3}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                        <input
                          type="date"
                          value={proj.start_date || ''}
                          onChange={(e) => {
                            const newProj = [...projects];
                            newProj[index].start_date = e.target.value;
                            setProjects(newProj);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                        <input
                          type="date"
                          value={proj.end_date || ''}
                          onChange={(e) => {
                            const newProj = [...projects];
                            newProj[index].end_date = e.target.value;
                            setProjects(newProj);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Project URL</label>
                      <input
                        type="url"
                        value={proj.project_url || ''}
                        onChange={(e) => {
                          const newProj = [...projects];
                          newProj[index].project_url = e.target.value;
                          setProjects(newProj);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="https://..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Technologies Used</label>
                      <input
                        type="text"
                        value={proj.technologies_used?.join(', ') || ''}
                        onChange={(e) => {
                          const newProj = [...projects];
                          newProj[index].technologies_used = e.target.value.split(',').map(t => t.trim()).filter(t => t);
                          setProjects(newProj);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., React, Node.js, PostgreSQL"
                      />
                    </div>
                  </div>
                  <button
                    onClick={() => removeProject(index)}
                    className="ml-2 p-2 text-red-500 hover:bg-red-50 rounded-lg"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            {projects.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No projects added yet. Click "Add Project" to add your first project.
              </div>
            )}
          </div>
        )}

        {/* Certifications Section */}
        {activeSection === 'certifications' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Certifications</h3>
              <button
                onClick={addCertification}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Certification
              </button>
            </div>
            {certifications.map((cert, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Certification Name</label>
                        <input
                          type="text"
                          value={cert.certification_name}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].certification_name = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Issuing Organization</label>
                        <input
                          type="text"
                          value={cert.issuing_organization}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].issuing_organization = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Issue Date</label>
                        <input
                          type="date"
                          value={cert.issue_date || ''}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].issue_date = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
                        <input
                          type="date"
                          value={cert.expiry_date || ''}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].expiry_date = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Credential ID</label>
                        <input
                          type="text"
                          value={cert.credential_id || ''}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].credential_id = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Credential URL</label>
                        <input
                          type="url"
                          value={cert.credential_url || ''}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].credential_url = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="https://..."
                        />
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeCertification(index)}
                    className="ml-2 p-2 text-red-500 hover:bg-red-50 rounded-lg"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            {certifications.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No certifications added yet. Click "Add Certification" to add your first certification.
              </div>
            )}
          </div>
        )}

        {/* Languages Section */}
        {activeSection === 'languages' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Languages</h3>
              <button
                onClick={addLanguage}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Language
              </button>
            </div>
            {languages.map((lang, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1 grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
                      <input
                        type="text"
                        value={lang.language_name}
                        onChange={(e) => {
                          const newLang = [...languages];
                          newLang[index].language_name = e.target.value;
                          setLanguages(newLang);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., Arabic, English, French"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Proficiency Level</label>
                      <select
                        value={lang.proficiency_level}
                        onChange={(e) => {
                          const newLang = [...languages];
                          newLang[index].proficiency_level = e.target.value;
                          setLanguages(newLang);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="Beginner">Beginner</option>
                        <option value="Intermediate">Intermediate</option>
                        <option value="Advanced">Advanced</option>
                        <option value="Native">Native</option>
                      </select>
                    </div>
                  </div>
                  <button
                    onClick={() => removeLanguage(index)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            {languages.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No languages added yet. Click "Add Language" to add your first language.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}