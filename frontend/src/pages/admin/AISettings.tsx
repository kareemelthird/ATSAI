import React, { useState, useEffect } from 'react';
import { Save, RefreshCw, AlertCircle, CheckCircle, Settings, MessageSquare, FileText, Zap } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const getAPIBaseURL = () => {
  if (import.meta.env.PROD) {
    return window.location.origin
  }
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}

const API_BASE_URL = getAPIBaseURL();

interface AISetting {
  id: number;
  setting_key: string;
  setting_value: string;
  setting_type: string;
  description: string;
  is_active: boolean;
  updated_at: string;
}

const AISettings: React.FC = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState<AISetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const getToken = () => localStorage.getItem('access_token');

  const fetchSettings = async () => {
    try {
      const token = getToken();
      if (!token) {
        setMessage({ type: 'error', text: 'Please log in to access AI settings' });
        setLoading(false);
        return;
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/v1/ai-settings/settings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSettings(response.data);
      setLoading(false);
    } catch (error: any) {
      console.error('Error fetching AI settings:', error);
      if (error.response?.status === 401) {
        setMessage({ type: 'error', text: 'Session expired. Please log in again.' });
      } else if (error.response?.status === 403) {
        setMessage({ type: 'error', text: 'Admin access required to view AI settings' });
      } else {
        setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to load settings' });
      }
      setLoading(false);
    }
  };

  const initializeDefaults = async () => {
    try {
      setSaving(true);
      const token = getToken();
      if (!token) {
        setMessage({ type: 'error', text: 'Authentication required' });
        setSaving(false);
        return;
      }
      
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/ai-settings/settings/initialize`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage({ type: 'success', text: `Initialized ${response.data.created.length} default settings` });
      fetchSettings();
    } catch (error: any) {
      if (error.response?.status === 401) {
        setMessage({ type: 'error', text: 'Session expired. Please log in again.' });
      } else if (error.response?.status === 403) {
        setMessage({ type: 'error', text: 'Admin access required' });
      } else {
        setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to initialize' });
      }
    } finally {
      setSaving(false);
    }
  };

  const startEditing = (setting: AISetting) => {
    setEditingKey(setting.setting_key);
    setEditValue(setting.setting_value);
  };

  const cancelEditing = () => {
    setEditingKey(null);
    setEditValue('');
  };

  const saveSetting = async (settingKey: string) => {
    try {
      setSaving(true);
      const token = getToken();
      if (!token) {
        setMessage({ type: 'error', text: 'Authentication required' });
        setSaving(false);
        return;
      }
      
      await axios.put(
        `${API_BASE_URL}/api/v1/ai-settings/settings/${settingKey}`,
        { setting_value: editValue, is_active: true },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage({ type: 'success', text: 'Setting updated successfully' });
      setEditingKey(null);
      fetchSettings();
    } catch (error: any) {
      if (error.response?.status === 401) {
        setMessage({ type: 'error', text: 'Session expired. Please log in again.' });
      } else if (error.response?.status === 403) {
        setMessage({ type: 'error', text: 'Admin access required' });
      } else {
        setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to save' });
      }
    } finally {
      setSaving(false);
    }
  };

  const getIcon = (key: string) => {
    if (key.includes('resume')) return <FileText className="w-5 h-5" />;
    if (key.includes('chat')) return <MessageSquare className="w-5 h-5" />;
    if (key.includes('temperature') || key.includes('token')) return <Zap className="w-5 h-5" />;
    return <Settings className="w-5 h-5" />;
  };

  const formatValue = (value: string, type: string) => {
    if (type === 'boolean') {
      return value === 'true' ? 'Enabled' : 'Disabled';
    }
    if (value.length > 100 && editingKey === null) {
      return value.substring(0, 100) + '...';
    }
    return value;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Configuration</h1>
          <p className="mt-2 text-sm text-gray-600">
            Customize AI behavior for resume analysis and chat interactions
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchSettings}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          {settings.length === 0 && (
            <button
              onClick={initializeDefaults}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Settings className="w-4 h-4" />
              Initialize Defaults
            </button>
          )}
        </div>
      </div>

      {message && (
        <div
          className={`p-4 rounded-lg flex items-center gap-3 ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {settings.length === 0 ? (
          <div className="p-12 text-center">
            <Settings className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Settings Found</h3>
            <p className="text-gray-600 mb-6">
              Initialize default AI settings to get started with customization
            </p>
            <button
              onClick={initializeDefaults}
              disabled={saving}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Initialize Default Settings
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {settings.map((setting) => (
              <div key={setting.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 p-3 bg-blue-100 rounded-lg text-blue-600">
                    {getIcon(setting.setting_key)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {setting.setting_key.replace(/_/g, ' ').toUpperCase()}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          setting.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {setting.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-700">
                        {setting.setting_type}
                      </span>
                    </div>

                    <p className="text-sm text-gray-600 mb-4">{setting.description}</p>

                    {editingKey === setting.setting_key ? (
                      <div className="space-y-3">
                        <textarea
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          rows={setting.setting_value.length > 200 ? 12 : 4}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                          placeholder="Enter setting value..."
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => saveSetting(setting.setting_key)}
                            disabled={saving}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                          >
                            <Save className="w-4 h-4" />
                            Save Changes
                          </button>
                          <button
                            onClick={cancelEditing}
                            disabled={saving}
                            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 mb-3">
                          <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                            {formatValue(setting.setting_value, setting.setting_type)}
                          </pre>
                        </div>
                        <button
                          onClick={() => startEditing(setting)}
                          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          <Settings className="w-4 h-4" />
                          Edit Setting
                        </button>
                      </div>
                    )}

                    <div className="mt-3 text-xs text-gray-500">
                      Last updated: {new Date(setting.updated_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Help Section */}
      <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          Configuration Guide
        </h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            <strong>Resume Analysis Instructions:</strong> Controls how AI extracts information from uploaded CVs.
            Customize extraction rules, date formats, and data categorization.
          </p>
          <p>
            <strong>Chat System Instructions:</strong> Defines AI behavior when answering questions about candidates,
            jobs, and applications. Update this to change response style and capabilities.
          </p>
          <p>
            <strong>Temperature:</strong> Controls AI creativity (0.0 = focused, 1.0 = creative). Recommended: 0.3-0.5 for professional use.
          </p>
          <p>
            <strong>Max Tokens:</strong> Maximum response length. Higher values allow longer, more detailed responses.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AISettings;
