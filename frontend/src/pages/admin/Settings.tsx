import { Settings as SettingsIcon, Save, Check, X, Loader, AlertCircle, TestTube, RefreshCw, Power } from 'lucide-react';
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface Setting {
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

export default function AdminSettings() {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeCategory, setActiveCategory] = useState('ai_provider');
  const [editedValues, setEditedValues] = useState<Record<string, string>>({});
  const [testingConnection, setTestingConnection] = useState(false);
  const [testResult, setTestResult] = useState<{success: boolean; message: string} | null>(null);
  const [restartingServer, setRestartingServer] = useState(false);
  const [restartResult, setRestartResult] = useState<{success: boolean; message: string} | null>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/settings/`);
      setSettings(response.data);
      setError('');
      
      // Initialize edited values
      const values: Record<string, string> = {};
      response.data.forEach((setting: Setting) => {
        values[setting.key] = setting.value;
      });
      setEditedValues(values);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch settings');
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleValueChange = (key: string, value: string) => {
    setEditedValues(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveSetting = async (setting: Setting) => {
    try {
      const response = await axios.put(`${API_URL}/settings/${setting.key}`, {
        value: editedValues[setting.key]
      });
      
      setSuccess(`${setting.label} updated successfully!${response.data.requires_restart ? ' Server restart required.' : ''}`);
      setTimeout(() => setSuccess(''), 5000);
      
      // Refresh settings
      await fetchSettings();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to update ${setting.label}`);
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleTestAIConnection = async () => {
    try {
      setTestingConnection(true);
      setTestResult(null);
      
      // Get provider from edited values
      const provider = editedValues['AI_PROVIDER'] || 'groq';
      const apiKey = editedValues[`${provider.toUpperCase()}_API_KEY`] || '';
      
      // Get provider-specific model
      const modelKey = `${provider.toUpperCase()}_MODEL`;
      const model = editedValues[modelKey] || editedValues['AI_MODEL'] || 'llama-3.3-70b-versatile';
      
      // Check if API key is the masked value or empty
      // If so, tell backend to use the actual value from .env
      const useStoredKey = !apiKey || apiKey === '***ENCRYPTED***';
      
      const response = await axios.post(`${API_URL}/settings/test-ai-connection`, {
        provider,
        api_key: useStoredKey ? undefined : apiKey,
        model,
        use_stored_credentials: useStoredKey
      });
      
      setTestResult(response.data);
    } catch (err: any) {
      setTestResult({
        success: false,
        message: err.response?.data?.detail || 'Connection test failed'
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleRestartServer = async () => {
    if (!confirm('Are you sure you want to restart the server? This will temporarily interrupt all connections.')) {
      return;
    }

    try {
      setRestartingServer(true);
      setRestartResult(null);
      
      const response = await axios.post(`${API_URL}/settings/restart-server`);
      
      setRestartResult({
        success: true,
        message: response.data.message || 'Server restart initiated successfully'
      });

      // Show reconnecting message after 2 seconds
      setTimeout(() => {
        setRestartResult({
          success: true,
          message: 'Server is restarting... You may need to refresh the page in a few seconds.'
        });
      }, 2000);

      // Try to reconnect after 5 seconds
      setTimeout(async () => {
        try {
          await axios.get(`${API_URL}/settings/`);
          setRestartResult({
            success: true,
            message: 'Server restarted successfully! Page will reload...'
          });
          setTimeout(() => window.location.reload(), 1000);
        } catch {
          setRestartResult({
            success: false,
            message: 'Server is still restarting. Please refresh the page manually.'
          });
        }
      }, 5000);

    } catch (err: any) {
      setRestartResult({
        success: false,
        message: err.response?.data?.detail || 'Failed to restart server'
      });
    } finally {
      setRestartingServer(false);
    }
  };

  const filteredSettings = settings.filter(s => {
    // Filter by category
    if (s.category !== activeCategory) return false;
    
    // For AI provider category, filter based on selected provider
    if (s.category === 'ai_provider') {
      // Always show AI_PROVIDER selector and USE_MOCK_AI
      if (s.key === 'AI_PROVIDER' || s.key === 'USE_MOCK_AI') return true;
      
      // Get current provider
      const currentProvider = editedValues['AI_PROVIDER'] || 'groq';
      
      // Show only settings for the selected provider
      if (s.key.includes('GROQ') && currentProvider !== 'groq') return false;
      if (s.key.includes('DEEPSEEK') && currentProvider !== 'deepseek') return false;
      if (s.key.includes('OPENROUTER') && currentProvider !== 'openrouter') return false;
    }
    
    return true;
  });
  
  const hasUnsavedChanges = (setting: Setting) => {
    return editedValues[setting.key] !== setting.value && editedValues[setting.key] !== '***ENCRYPTED***';
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
              <SettingsIcon className="w-8 h-8 mr-3 text-blue-600" />
              System Settings
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Configure system-wide settings and preferences (stored in .env file)
            </p>
          </div>
          <button
            onClick={handleRestartServer}
            disabled={restartingServer}
            className="flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Power className={`w-5 h-5 mr-2 ${restartingServer ? 'animate-spin' : ''}`} />
            {restartingServer ? 'Restarting...' : 'Restart Server'}
          </button>
        </div>
      </div>

      {/* Restart Result */}
      {restartResult && (
        <div className={`mb-4 p-4 border rounded-lg flex items-center ${
          restartResult.success 
            ? 'bg-blue-100 dark:bg-blue-900/20 border-blue-400 text-blue-700 dark:text-blue-400'
            : 'bg-red-100 dark:bg-red-900/20 border-red-400 text-red-700 dark:text-red-400'
        }`}>
          <RefreshCw className={`w-5 h-5 mr-2 ${restartResult.success ? 'animate-spin' : ''}`} />
          {restartResult.message}
        </div>
      )}

      {/* Success/Error Messages */}
      {success && (
        <div className="mb-4 p-4 bg-green-100 dark:bg-green-900/20 border border-green-400 text-green-700 dark:text-green-400 rounded-lg flex items-center">
          <Save className="w-5 h-5 mr-2" />
          {success}
        </div>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/20 border border-red-400 text-red-700 dark:text-red-400 rounded-lg">
          {error}
        </div>
      )}

      {/* Category Tabs */}
      <div className="mb-6 flex gap-2 flex-wrap">
        {[
          { key: 'ai_provider', label: 'AI Provider', icon: '🤖' },
          { key: 'database', label: 'Database', icon: '🗄️' },
          { key: 'application', label: 'Application', icon: '⚙️' },
          { key: 'security', label: 'Security', icon: '🔒' },
          { key: 'server', label: 'Server', icon: '🖥️' }
        ].map(cat => (
          <button
            key={cat.key}
            onClick={() => setActiveCategory(cat.key)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeCategory === cat.key
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <span className="mr-2">{cat.icon}</span>
            {cat.label}
          </button>
        ))}
      </div>

      {/* Settings List */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {/* AI Provider Test Button */}
          {activeCategory === 'ai_provider' && (
            <div className="mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-300">Test AI Connection</h3>
                  <p className="text-xs text-blue-700 dark:text-blue-400 mt-1">
                    Verify your AI provider configuration is working correctly
                  </p>
                </div>
                <button
                  onClick={handleTestAIConnection}
                  disabled={testingConnection}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  <SettingsIcon className={`w-4 h-4 mr-2 ${testingConnection ? 'animate-spin' : ''}`} />
                  {testingConnection ? 'Testing...' : 'Test Connection'}
                </button>
              </div>
              
              {testResult && (
                <div className={`mt-3 p-3 rounded-lg ${
                  testResult.success 
                    ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300' 
                    : 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300'
                }`}>
                  <p className="text-sm font-medium">{testResult.message}</p>
                </div>
              )}
            </div>
          )}

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            {filteredSettings.length === 0 ? (
              <div className="p-12 text-center text-gray-500 dark:text-gray-400">
                No settings found in this category
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredSettings.map((setting) => (
                  <div key={setting.key} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                          {setting.label}
                          {setting.requires_restart && (
                            <span className="ml-2 text-xs text-orange-600 dark:text-orange-400">
                              (restart required)
                            </span>
                          )}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {setting.description}
                        </p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 font-mono">
                          {setting.key}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      {setting.data_type === 'boolean' ? (
                        <select
                          value={editedValues[setting.key] || 'false'}
                          onChange={(e) => handleValueChange(setting.key, e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        >
                          <option value="true">True</option>
                          <option value="false">False</option>
                        </select>
                      ) : setting.data_type === 'select' ? (
                        <select
                          value={editedValues[setting.key] || ''}
                          onChange={(e) => handleValueChange(setting.key, e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        >
                          <option value="groq">Groq</option>
                          <option value="deepseek">DeepSeek</option>
                          <option value="openrouter">OpenRouter</option>
                        </select>
                      ) : setting.data_type === 'number' ? (
                        <input
                          type="number"
                          value={editedValues[setting.key] || ''}
                          onChange={(e) => handleValueChange(setting.key, e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      ) : (
                        <input
                          type={setting.data_type === 'password' ? 'password' : 'text'}
                          value={editedValues[setting.key] || ''}
                          onChange={(e) => handleValueChange(setting.key, e.target.value)}
                          placeholder={setting.is_encrypted ? '***ENCRYPTED***' : ''}
                          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      )}

                      <button
                        onClick={() => handleSaveSetting(setting)}
                        disabled={!hasUnsavedChanges(setting)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                      >
                        <Save className="w-4 h-4 mr-2" />
                        Save
                      </button>
                    </div>

                    {hasUnsavedChanges(setting) && (
                      <p className="text-xs text-orange-600 dark:text-orange-400 mt-2">
                        Unsaved changes
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">ℹ️ Important Notes</h3>
        <ul className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
          <li>• Settings are stored in the <code className="px-1 py-0.5 bg-blue-100 dark:bg-blue-900 rounded">.env</code> file</li>
          <li>• Changes marked with "restart required" need backend server restart to take effect</li>
          <li>• Click the orange "Restart Server" button to apply changes that require restart</li>
          <li>• API keys are masked for security (***ENCRYPTED***)</li>
          <li>• Test AI connection after changing AI provider settings</li>
          <li>• Only settings relevant to selected AI provider are shown</li>
        </ul>
      </div>
    </div>
  );
}
