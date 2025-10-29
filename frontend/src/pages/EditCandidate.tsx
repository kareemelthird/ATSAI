import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { candidateApi } from '@/lib/api';
import { Save, ArrowLeft, Plus, Trash2, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

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

export default function EditCandidate() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [activeSection, setActiveSection] = useState('basic');

  // Basic Info State
  const [formData, setFormData] = useState({
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
    preferred_locations: [] as string[],
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
  const { data: candidate, isLoading } = useQuery({
    queryKey: ['candidate', id],
    queryFn: () => candidateApi.getById(id!),
    enabled: !!id
  });

  useEffect(() => {
    if (candidate) {
      setFormData({
        first_name: candidate.first_name || '',
        last_name: candidate.last_name || '',
        email: candidate.email || '',
        phone: candidate.phone || '',
        current_location: candidate.current_location || '',
        professional_summary: candidate.professional_summary || '',
        career_level: candidate.career_level || '',
        years_of_experience: candidate.years_of_experience || 0,
        linkedin_url: candidate.linkedin_url || '',
        github_url: candidate.github_url || '',
        portfolio_url: candidate.portfolio_url || '',
        preferred_locations: candidate.preferred_locations || [],
        open_to_relocation: candidate.open_to_relocation || false,
        willing_to_travel: candidate.willing_to_travel || false,
        expected_salary_min: candidate.expected_salary_min || 0,
        expected_salary_max: candidate.expected_salary_max || 0,
        salary_currency: candidate.salary_currency || 'USD',
        availability: candidate.availability || '',
        notice_period_days: candidate.notice_period_days || 0
      });
      setSkills(candidate.skills || []);
      setWorkExperiences(candidate.work_experiences || []);
      setEducation(candidate.education || []);
      setProjects(candidate.projects || []);
      setCertifications(candidate.certifications || []);
      setLanguages(candidate.languages || []);
    }
  }, [candidate]);

  const handleSave = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      // Update basic info
      await axios.put(
        `${API_BASE_URL}/api/v1/candidates/${id}`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update skills
      await axios.put(
        `${API_BASE_URL}/api/v1/candidates/${id}/skills`,
        { skills },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update work experiences
      await axios.put(
        `${API_BASE_URL}/api/v1/candidates/${id}/work-experiences`,
        { work_experiences: workExperiences },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update education
      await axios.put(
        `${API_BASE_URL}/api/v1/candidates/${id}/education`,
        { education },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update projects
      await axios.put(
        `${API_BASE_URL}/api/v1/candidates/${id}/projects`,
        { projects },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update certifications
      await axios.put(
        `${API_BASE_URL}/api/v1/candidates/${id}/certifications`,
        { certifications },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update languages
      await axios.put(
        `${API_BASE_URL}/api/v1/candidates/${id}/languages`,
        { languages },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setMessage({ type: 'success', text: 'تم حفظ التعديلات بنجاح ✓' });
      setTimeout(() => navigate(`/candidates/${id}`), 2000);
    } catch (error: any) {
      console.error('Error saving candidate:', error);
      setMessage({ type: 'error', text: 'خطأ في حفظ التعديلات' });
    }
  };

  // Add/Remove handlers
  const addSkill = () => {
    setSkills([...skills, { skill_name: '', proficiency_level: 'Intermediate', years_of_experience: 0, category: 'Technical' }]);
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
    setEducation([...education, { institution_name: '', degree: '', start_date: '' }]);
  };

  const removeEducation = (index: number) => {
    setEducation(education.filter((_, i) => i !== index));
  };

  const addProject = () => {
    setProjects([...projects, { project_name: '', technologies_used: [] }]);
  };

  const removeProject = (index: number) => {
    setProjects(projects.filter((_, i) => i !== index));
  };

  const addCertification = () => {
    setCertifications([...certifications, { certification_name: '', issuing_organization: '' }]);
  };

  const removeCertification = (index: number) => {
    setCertifications(certifications.filter((_, i) => i !== index));
  };

  const addLanguage = () => {
    setLanguages([...languages, { language_name: '', proficiency_level: 'Intermediate' }]);
  };

  const removeLanguage = (index: number) => {
    setLanguages(languages.filter((_, i) => i !== index));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">جاري التحميل...</p>
        </div>
      </div>
    );
  }

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
              تعديل بيانات المرشح
            </h1>
            <p className="text-gray-600 mt-1">
              {formData.first_name} {formData.last_name}
            </p>
          </div>
        </div>
        <button
          onClick={handleSave}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Save className="w-5 h-5" />
          حفظ التعديلات
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
          {[
            { id: 'basic', label: 'المعلومات الأساسية' },
            { id: 'skills', label: 'المهارات' },
            { id: 'experience', label: 'الخبرات العملية' },
            { id: 'education', label: 'التعليم' },
            { id: 'projects', label: 'المشاريع' },
            { id: 'certifications', label: 'الشهادات' },
            { id: 'languages', label: 'اللغات' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id)}
              className={`px-6 py-3 font-medium transition border-b-2 whitespace-nowrap ${
                activeSection === tab.id
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-600 border-transparent hover:text-gray-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {/* Basic Info */}
        {activeSection === 'basic' && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">الاسم الأول *</label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">الاسم الأخير *</label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">البريد الإلكتروني *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">رقم الهاتف</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">الموقع الحالي</label>
              <input
                type="text"
                value={formData.current_location}
                onChange={(e) => setFormData({...formData, current_location: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-lg"
                placeholder="المدينة، الدولة"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">الملخص المهني</label>
              <textarea
                value={formData.professional_summary}
                onChange={(e) => setFormData({...formData, professional_summary: e.target.value})}
                rows={4}
                className="w-full p-2 border border-gray-300 rounded-lg"
                placeholder="نبذة مختصرة عن خبراتك ومهاراتك..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">المستوى المهني</label>
                <select
                  value={formData.career_level}
                  onChange={(e) => setFormData({...formData, career_level: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value="">-- اختر --</option>
                  <option value="Entry">مبتدئ</option>
                  <option value="Mid">متوسط</option>
                  <option value="Senior">أقدم</option>
                  <option value="Lead">قائد فريق</option>
                  <option value="Manager">مدير</option>
                  <option value="Director">مدير تنفيذي</option>
                  <option value="Executive">إداري عالي</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">سنوات الخبرة</label>
                <input
                  type="number"
                  value={formData.years_of_experience}
                  onChange={(e) => setFormData({...formData, years_of_experience: parseInt(e.target.value) || 0})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  min="0"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">LinkedIn</label>
                <input
                  type="url"
                  value={formData.linkedin_url}
                  onChange={(e) => setFormData({...formData, linkedin_url: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  placeholder="https://linkedin.com/in/..."
                  dir="ltr"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">GitHub</label>
                <input
                  type="url"
                  value={formData.github_url}
                  onChange={(e) => setFormData({...formData, github_url: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  placeholder="https://github.com/..."
                  dir="ltr"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Portfolio</label>
                <input
                  type="url"
                  value={formData.portfolio_url}
                  onChange={(e) => setFormData({...formData, portfolio_url: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  placeholder="https://..."
                  dir="ltr"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="relocation"
                  checked={formData.open_to_relocation}
                  onChange={(e) => setFormData({...formData, open_to_relocation: e.target.checked})}
                  className="w-4 h-4"
                />
                <label htmlFor="relocation" className="text-sm text-gray-700">مستعد للانتقال</label>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="travel"
                  checked={formData.willing_to_travel}
                  onChange={(e) => setFormData({...formData, willing_to_travel: e.target.checked})}
                  className="w-4 h-4"
                />
                <label htmlFor="travel" className="text-sm text-gray-700">مستعد للسفر</label>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">الراتب المتوقع (من)</label>
                <input
                  type="number"
                  value={formData.expected_salary_min}
                  onChange={(e) => setFormData({...formData, expected_salary_min: parseInt(e.target.value) || 0})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">الراتب المتوقع (إلى)</label>
                <input
                  type="number"
                  value={formData.expected_salary_max}
                  onChange={(e) => setFormData({...formData, expected_salary_max: parseInt(e.target.value) || 0})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">العملة</label>
                <select
                  value={formData.salary_currency}
                  onChange={(e) => setFormData({...formData, salary_currency: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
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
                <label className="block text-sm font-medium text-gray-700 mb-2">التوافر</label>
                <select
                  value={formData.availability}
                  onChange={(e) => setFormData({...formData, availability: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value="">-- اختر --</option>
                  <option value="Immediate">فوري</option>
                  <option value="2 weeks">أسبوعين</option>
                  <option value="1 month">شهر</option>
                  <option value="2 months">شهرين</option>
                  <option value="3 months">3 أشهر</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">مدة الإشعار (بالأيام)</label>
                <input
                  type="number"
                  value={formData.notice_period_days}
                  onChange={(e) => setFormData({...formData, notice_period_days: parseInt(e.target.value) || 0})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
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
              <h3 className="text-lg font-semibold">المهارات</h3>
              <button
                onClick={addSkill}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                إضافة مهارة
              </button>
            </div>
            {skills.map((skill, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">اسم المهارة</label>
                      <input
                        type="text"
                        value={skill.skill_name}
                        onChange={(e) => {
                          const newSkills = [...skills];
                          newSkills[index].skill_name = e.target.value;
                          setSkills(newSkills);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                        placeholder="مثال: Python, React, Project Management"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">المستوى</label>
                      <select
                        value={skill.proficiency_level}
                        onChange={(e) => {
                          const newSkills = [...skills];
                          newSkills[index].proficiency_level = e.target.value;
                          setSkills(newSkills);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        <option value="Beginner">مبتدئ</option>
                        <option value="Intermediate">متوسط</option>
                        <option value="Advanced">متقدم</option>
                        <option value="Expert">خبير</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">سنوات الخبرة</label>
                      <input
                        type="number"
                        value={skill.years_of_experience || 0}
                        onChange={(e) => {
                          const newSkills = [...skills];
                          newSkills[index].years_of_experience = parseInt(e.target.value) || 0;
                          setSkills(newSkills);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
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
                لا توجد مهارات. انقر على "إضافة مهارة" لإضافة مهارة جديدة.
              </div>
            )}
          </div>
        )}

        {/* Work Experience Section */}
        {activeSection === 'experience' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">الخبرات العملية</h3>
              <button
                onClick={addWorkExperience}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                إضافة خبرة
              </button>
            </div>
            {workExperiences.map((exp, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">اسم الشركة</label>
                        <input
                          type="text"
                          value={exp.company_name}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].company_name = e.target.value;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">المسمى الوظيفي</label>
                        <input
                          type="text"
                          value={exp.position}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].position = e.target.value;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ البدء</label>
                        <input
                          type="date"
                          value={exp.start_date}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].start_date = e.target.value;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الانتهاء</label>
                        <input
                          type="date"
                          value={exp.end_date || ''}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].end_date = e.target.value || undefined;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">نوع التوظيف</label>
                        <select
                          value={exp.employment_type || 'Full-time'}
                          onChange={(e) => {
                            const newExps = [...workExperiences];
                            newExps[index].employment_type = e.target.value;
                            setWorkExperiences(newExps);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        >
                          <option value="Full-time">دوام كامل</option>
                          <option value="Part-time">دوام جزئي</option>
                          <option value="Contract">عقد</option>
                          <option value="Freelance">عمل حر</option>
                          <option value="Internship">تدريب</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">المسؤوليات</label>
                      <textarea
                        value={exp.responsibilities || ''}
                        onChange={(e) => {
                          const newExps = [...workExperiences];
                          newExps[index].responsibilities = e.target.value;
                          setWorkExperiences(newExps);
                        }}
                        rows={3}
                        className="w-full p-2 border border-gray-300 rounded-lg"
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
                لا توجد خبرات عملية. انقر على "إضافة خبرة" لإضافة خبرة جديدة.
              </div>
            )}
          </div>
        )}

        {/* Education Section */}
        {activeSection === 'education' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">التعليم</h3>
              <button
                onClick={addEducation}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                إضافة مؤهل
              </button>
            </div>
            {education.map((edu, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">اسم المؤسسة</label>
                        <input
                          type="text"
                          value={edu.institution_name}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].institution_name = e.target.value;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">الدرجة العلمية</label>
                        <input
                          type="text"
                          value={edu.degree}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].degree = e.target.value;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                          placeholder="مثال: بكالوريوس، ماجستير"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">التخصص</label>
                        <input
                          type="text"
                          value={edu.field_of_study || ''}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].field_of_study = e.target.value;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ البدء</label>
                        <input
                          type="date"
                          value={edu.start_date}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].start_date = e.target.value;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ التخرج</label>
                        <input
                          type="date"
                          value={edu.end_date || ''}
                          onChange={(e) => {
                            const newEdu = [...education];
                            newEdu[index].end_date = e.target.value || undefined;
                            setEducation(newEdu);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">التقدير</label>
                      <input
                        type="text"
                        value={edu.grade || ''}
                        onChange={(e) => {
                          const newEdu = [...education];
                          newEdu[index].grade = e.target.value;
                          setEducation(newEdu);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                        placeholder="مثال: ممتاز، جيد جداً، 3.8 GPA"
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
                لا توجد مؤهلات تعليمية. انقر على "إضافة مؤهل" لإضافة مؤهل جديد.
              </div>
            )}
          </div>
        )}

        {/* Projects Section */}
        {activeSection === 'projects' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">المشاريع</h3>
              <button
                onClick={addProject}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                إضافة مشروع
              </button>
            </div>
            {projects.map((proj, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">اسم المشروع</label>
                        <input
                          type="text"
                          value={proj.project_name}
                          onChange={(e) => {
                            const newProj = [...projects];
                            newProj[index].project_name = e.target.value;
                            setProjects(newProj);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">الدور</label>
                        <input
                          type="text"
                          value={proj.role || ''}
                          onChange={(e) => {
                            const newProj = [...projects];
                            newProj[index].role = e.target.value;
                            setProjects(newProj);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                          placeholder="مثال: مطور رئيسي، مدير مشروع"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">الوصف</label>
                      <textarea
                        value={proj.description || ''}
                        onChange={(e) => {
                          const newProj = [...projects];
                          newProj[index].description = e.target.value;
                          setProjects(newProj);
                        }}
                        rows={3}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ البدء</label>
                        <input
                          type="date"
                          value={proj.start_date || ''}
                          onChange={(e) => {
                            const newProj = [...projects];
                            newProj[index].start_date = e.target.value;
                            setProjects(newProj);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الانتهاء</label>
                        <input
                          type="date"
                          value={proj.end_date || ''}
                          onChange={(e) => {
                            const newProj = [...projects];
                            newProj[index].end_date = e.target.value;
                            setProjects(newProj);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">رابط المشروع</label>
                      <input
                        type="url"
                        value={proj.project_url || ''}
                        onChange={(e) => {
                          const newProj = [...projects];
                          newProj[index].project_url = e.target.value;
                          setProjects(newProj);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                        placeholder="https://..."
                        dir="ltr"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">التقنيات المستخدمة</label>
                      <input
                        type="text"
                        value={proj.technologies_used?.join(', ') || ''}
                        onChange={(e) => {
                          const newProj = [...projects];
                          newProj[index].technologies_used = e.target.value.split(',').map(t => t.trim());
                          setProjects(newProj);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                        placeholder="مثال: React, Node.js, PostgreSQL"
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
                لا توجد مشاريع. انقر على "إضافة مشروع" لإضافة مشروع جديد.
              </div>
            )}
          </div>
        )}

        {/* Certifications Section */}
        {activeSection === 'certifications' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">الشهادات</h3>
              <button
                onClick={addCertification}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                إضافة شهادة
              </button>
            </div>
            {certifications.map((cert, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">اسم الشهادة</label>
                        <input
                          type="text"
                          value={cert.certification_name}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].certification_name = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">الجهة المانحة</label>
                        <input
                          type="text"
                          value={cert.issuing_organization}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].issuing_organization = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الإصدار</label>
                        <input
                          type="date"
                          value={cert.issue_date || ''}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].issue_date = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الانتهاء</label>
                        <input
                          type="date"
                          value={cert.expiry_date || ''}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].expiry_date = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">رقم الشهادة</label>
                        <input
                          type="text"
                          value={cert.credential_id || ''}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].credential_id = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">رابط الشهادة</label>
                        <input
                          type="url"
                          value={cert.credential_url || ''}
                          onChange={(e) => {
                            const newCert = [...certifications];
                            newCert[index].credential_url = e.target.value;
                            setCertifications(newCert);
                          }}
                          className="w-full p-2 border border-gray-300 rounded-lg"
                          placeholder="https://..."
                          dir="ltr"
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
                لا توجد شهادات. انقر على "إضافة شهادة" لإضافة شهادة جديدة.
              </div>
            )}
          </div>
        )}

        {/* Languages Section */}
        {activeSection === 'languages' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">اللغات</h3>
              <button
                onClick={addLanguage}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                إضافة لغة
              </button>
            </div>
            {languages.map((lang, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1 grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">اللغة</label>
                      <input
                        type="text"
                        value={lang.language_name}
                        onChange={(e) => {
                          const newLang = [...languages];
                          newLang[index].language_name = e.target.value;
                          setLanguages(newLang);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                        placeholder="مثال: العربية، الإنجليزية"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">المستوى</label>
                      <select
                        value={lang.proficiency_level}
                        onChange={(e) => {
                          const newLang = [...languages];
                          newLang[index].proficiency_level = e.target.value;
                          setLanguages(newLang);
                        }}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        <option value="Beginner">مبتدئ</option>
                        <option value="Intermediate">متوسط</option>
                        <option value="Advanced">متقدم</option>
                        <option value="Native">لغة أم</option>
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
                لا توجد لغات. انقر على "إضافة لغة" لإضافة لغة جديدة.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
