import React, { useState, useEffect } from 'react';
import { 
  Save, RefreshCw, AlertCircle, CheckCircle, Settings as SettingsIcon, 
  MessageSquare, FileText, Zap, TestTube, Power, Database, Shield, Key 
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

interface AISetting {
  id: number;
  setting_key: string;
  setting_value: string;
  setting_type: string;
  description: string;
  is_active: boolean;
  updated_at: string;
}

interface SystemSetting {
  category: string;
  key: string;
  value: string;
  label: string;
  description: string;
  data_type: string;
  is_encrypted: boolean;
  is_public: boolean;
  requires_restart: boolean;
  provider?: string;
}

type TabType = 'ai' | 'system' | 'database' | 'security';

const UnifiedSettings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('ai');
  
  // AI Settings State
  const [aiSettings, setAiSettings] = useState<AISetting[]>([]);
  const [aiLoading, setAiLoading] = useState(false);
  
  // System Settings State
  const [systemSettings, setSystemSettings] = useState<SystemSetting[]>([]);
  const [systemLoading, setSystemLoading] = useState(false);
  const [editedSystemValues, setEditedSystemValues] = useState<Record<string, string>>({});
  
  // Common State
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [testingConnection, setTestingConnection] = useState(false);
  const [restartingServer, setRestartingServer] = useState(false);

  useEffect(() => {
    if (activeTab === 'ai') {
      fetchAISettings();
    } else if (activeTab === 'system') {
      fetchSystemSettings();
    }
  }, [activeTab]);

  const getToken = () => localStorage.getItem('access_token');

  // ==================== AI SETTINGS ====================
  
  const fetchAISettings = async () => {
    try {
      setAiLoading(true);
      const token = getToken();
      if (!token) {
        setMessage({ type: 'error', text: 'يرجى تسجيل الدخول للوصول للإعدادات' });
        return;
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/v1/ai-settings/settings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAiSettings(response.data);
    } catch (error: any) {
      console.error('Error fetching AI settings:', error);
      if (error.response?.status === 401) {
        setMessage({ type: 'error', text: 'انتهت الجلسة. يرجى تسجيل الدخول مجدداً' });
      } else {
        setMessage({ type: 'error', text: 'خطأ في تحميل إعدادات الذكاء الاصطناعي' });
      }
    } finally {
      setAiLoading(false);
    }
  };

  const initializeAIDefaults = async () => {
    try {
      setSaving(true);
      const token = getToken();
      await axios.post(
        `${API_BASE_URL}/api/v1/ai-settings/settings/initialize`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage({ type: 'success', text: 'تم تهيئة الإعدادات الافتراضية بنجاح' });
      fetchAISettings();
    } catch (error: any) {
      console.error('Error initializing defaults:', error);
      setMessage({ type: 'error', text: 'خطأ في تهيئة الإعدادات الافتراضية' });
    } finally {
      setSaving(false);
    }
  };

  const startEditingAI = (setting: AISetting) => {
    setEditingKey(setting.setting_key);
    setEditValue(setting.setting_value);
  };

  const cancelEditingAI = () => {
    setEditingKey(null);
    setEditValue('');
  };

  const saveAISetting = async (key: string) => {
    try {
      setSaving(true);
      const token = getToken();
      await axios.put(
        `${API_BASE_URL}/api/v1/ai-settings/settings/${key}`,
        { setting_value: editValue },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage({ type: 'success', text: 'تم حفظ الإعداد بنجاح' });
      setEditingKey(null);
      fetchAISettings();
    } catch (error: any) {
      console.error('Error saving AI setting:', error);
      setMessage({ type: 'error', text: 'خطأ في حفظ الإعداد' });
    } finally {
      setSaving(false);
    }
  };

  // ==================== SYSTEM SETTINGS ====================
  
  const fetchSystemSettings = async () => {
    try {
      setSystemLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/v1/settings/`);
      setSystemSettings(response.data);
      
      // Initialize edited values
      const values: Record<string, string> = {};
      response.data.forEach((setting: SystemSetting) => {
        values[setting.key] = setting.value;
      });
      setEditedSystemValues(values);
    } catch (err: any) {
      console.error('Error fetching system settings:', err);
      setMessage({ type: 'error', text: 'خطأ في تحميل إعدادات النظام' });
    } finally {
      setSystemLoading(false);
    }
  };

  const updateSystemSetting = async (key: string, value: string) => {
    try {
      setSaving(true);
      const token = getToken();
      await axios.put(
        `${API_BASE_URL}/api/v1/settings/${key}`,
        { value },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage({ type: 'success', text: 'تم تحديث الإعداد بنجاح' });
      fetchSystemSettings();
    } catch (error: any) {
      console.error('Error updating system setting:', error);
      setMessage({ type: 'error', text: 'خطأ في تحديث الإعداد' });
    } finally {
      setSaving(false);
    }
  };

  const testAIConnection = async () => {
    try {
      setTestingConnection(true);
      const token = getToken();
      await axios.post(
        `${API_BASE_URL}/api/v1/settings/test-connection`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage({ type: 'success', text: 'الاتصال بخدمة الذكاء الاصطناعي يعمل بنجاح ✓' });
    } catch (error: any) {
      setMessage({ type: 'error', text: 'فشل الاتصال بخدمة الذكاء الاصطناعي ✗' });
    } finally {
      setTestingConnection(false);
    }
  };

  const restartServer = async () => {
    if (!confirm('هل أنت متأكد من إعادة تشغيل الخادم؟ سيتم قطع الاتصال مؤقتاً.')) {
      return;
    }
    
    try {
      setRestartingServer(true);
      const token = getToken();
      await axios.post(
        `${API_BASE_URL}/api/v1/settings/restart`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage({ type: 'success', text: 'جاري إعادة تشغيل الخادم... يرجى الانتظار' });
    } catch (error: any) {
      setMessage({ type: 'error', text: 'خطأ في إعادة تشغيل الخادم' });
    } finally {
      setRestartingServer(false);
    }
  };

  // ==================== RENDER HELPERS ====================
  
  const getIconForSetting = (key: string) => {
    if (key.includes('chat')) return <MessageSquare className="w-5 h-5 text-purple-500" />;
    if (key.includes('resume') || key.includes('analysis')) return <FileText className="w-5 h-5 text-blue-500" />;
    if (key.includes('temperature') || key.includes('token')) return <Zap className="w-5 h-5 text-yellow-500" />;
    if (key.includes('api')) return <Key className="w-5 h-5 text-green-500" />;
    if (key.includes('database')) return <Database className="w-5 h-5 text-indigo-500" />;
    return <SettingsIcon className="w-5 h-5 text-gray-500" />;
  };

  const renderAISettings = () => (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">إعدادات الذكاء الاصطناعي</h2>
          <p className="text-gray-600 mt-1">إدارة تعليمات وسلوك الذكاء الاصطناعي</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={initializeAIDefaults}
            disabled={saving}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${saving ? 'animate-spin' : ''}`} />
            تهيئة افتراضية
          </button>
          <button
            onClick={testAIConnection}
            disabled={testingConnection}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400 flex items-center gap-2"
          >
            <TestTube className={`w-4 h-4 ${testingConnection ? 'animate-pulse' : ''}`} />
            اختبار الاتصال
          </button>
        </div>
      </div>

      {/* Settings List */}
      {aiLoading ? (
        <div className="text-center py-8">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto" />
          <p className="text-gray-600 mt-2">جاري التحميل...</p>
        </div>
      ) : aiSettings.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
          <p className="text-gray-700">لا توجد إعدادات. انقر على "تهيئة افتراضية" للبدء.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {aiSettings.map((setting) => (
            <div key={setting.id} className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  {getIconForSetting(setting.setting_key)}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800 mb-1">{setting.setting_key}</h3>
                    <p className="text-sm text-gray-600 mb-3">{setting.description}</p>
                    
                    {editingKey === setting.setting_key ? (
                      <div className="space-y-3">
                        <textarea
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          rows={setting.setting_type === 'text' ? 10 : 3}
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                          dir="ltr"
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => saveAISetting(setting.setting_key)}
                            disabled={saving}
                            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400 flex items-center gap-2"
                          >
                            <Save className="w-4 h-4" />
                            حفظ
                          </button>
                          <button
                            onClick={cancelEditingAI}
                            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                          >
                            إلغاء
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <div className="bg-gray-50 p-3 rounded border border-gray-200">
                          <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono" dir="ltr">
                            {setting.setting_value}
                          </pre>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-500">
                            آخر تحديث: {new Date(setting.updated_at).toLocaleString('ar-EG')}
                          </span>
                          <button
                            onClick={() => startEditingAI(setting)}
                            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                          >
                            تعديل
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderSystemSettings = () => {
    const categories = Array.from(new Set(systemSettings.map(s => s.category)));
    
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">إعدادات النظام</h2>
            <p className="text-gray-600 mt-1">إعدادات قاعدة البيانات ومزود الخدمة والأمان</p>
          </div>
          <button
            onClick={restartServer}
            disabled={restartingServer}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-400 flex items-center gap-2"
          >
            <Power className={`w-4 h-4 ${restartingServer ? 'animate-spin' : ''}`} />
            إعادة تشغيل الخادم
          </button>
        </div>

        {systemLoading ? (
          <div className="text-center py-8">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto" />
            <p className="text-gray-600 mt-2">جاري التحميل...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {categories.map((category) => (
              <div key={category} className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 capitalize">
                  {category.replace('_', ' ')}
                </h3>
                <div className="space-y-4">
                  {systemSettings
                    .filter((s) => s.category === category)
                    .map((setting) => (
                      <div key={setting.key} className="border-b border-gray-100 last:border-0 pb-4 last:pb-0">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <label className="block font-medium text-gray-700 mb-1">
                              {setting.label}
                              {setting.requires_restart && (
                                <span className="ml-2 text-xs text-red-500">(يتطلب إعادة تشغيل)</span>
                              )}
                            </label>
                            <p className="text-sm text-gray-500 mb-2">{setting.description}</p>
                            {setting.data_type === 'boolean' ? (
                              <select
                                value={editedSystemValues[setting.key] || setting.value}
                                onChange={(e) => {
                                  setEditedSystemValues({
                                    ...editedSystemValues,
                                    [setting.key]: e.target.value
                                  });
                                }}
                                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                              >
                                <option value="true">نعم</option>
                                <option value="false">لا</option>
                              </select>
                            ) : setting.is_encrypted ? (
                              <input
                                type="password"
                                value={editedSystemValues[setting.key] || setting.value}
                                onChange={(e) => {
                                  setEditedSystemValues({
                                    ...editedSystemValues,
                                    [setting.key]: e.target.value
                                  });
                                }}
                                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                dir="ltr"
                              />
                            ) : (
                              <input
                                type="text"
                                value={editedSystemValues[setting.key] || setting.value}
                                onChange={(e) => {
                                  setEditedSystemValues({
                                    ...editedSystemValues,
                                    [setting.key]: e.target.value
                                  });
                                }}
                                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                dir="ltr"
                              />
                            )}
                          </div>
                          <button
                            onClick={() => updateSystemSetting(setting.key, editedSystemValues[setting.key])}
                            disabled={saving || editedSystemValues[setting.key] === setting.value}
                            className="mt-6 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                          >
                            <Save className="w-4 h-4" />
                            حفظ
                          </button>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // ==================== MAIN RENDER ====================
  
  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Message Display */}
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
          <button
            onClick={() => setMessage(null)}
            className="ml-auto text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-1">
          {[
            { id: 'ai' as TabType, label: 'الذكاء الاصطناعي', icon: Zap },
            { id: 'system' as TabType, label: 'النظام', icon: SettingsIcon },
            { id: 'database' as TabType, label: 'قاعدة البيانات', icon: Database },
            { id: 'security' as TabType, label: 'الأمان', icon: Shield }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 font-medium transition border-b-2 ${
                  activeTab === tab.id
                    ? 'text-blue-600 border-blue-600'
                    : 'text-gray-600 border-transparent hover:text-gray-800'
                }`}
              >
                <Icon className="w-5 h-5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'ai' && renderAISettings()}
      {activeTab === 'system' && renderSystemSettings()}
      {activeTab === 'database' && (
        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">إعدادات قاعدة البيانات قيد التطوير</p>
        </div>
      )}
      {activeTab === 'security' && (
        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">إعدادات الأمان قيد التطوير</p>
        </div>
      )}
    </div>
  );
};

export default UnifiedSettings;
