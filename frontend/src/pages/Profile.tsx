import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

interface PersonalAISettings {
  has_personal_key: boolean;
  use_personal_ai_key: boolean;
  key_preview?: string;
}

interface CustomInstructions {
  custom_chat_instructions?: string;
  custom_cv_analysis_instructions?: string;
  use_custom_instructions: boolean;
}

interface GuideStep {
  number: number;
  title: string;
  description: string;
  url?: string;
}

interface SetupGuide {
  title: string;
  steps: GuideStep[];
  benefits: string[];
  model_info: {
    name: string;
    speed: string;
    context: string;
  };
}

interface TestResult {
  success: boolean;
  message: string;
  response_time?: number;
}

export default function Profile() {
  const queryClient = useQueryClient();
  const [apiKey, setApiKey] = useState('');
  const [usePersonalKey, setUsePersonalKey] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [testing, setTesting] = useState(false);

  // Password change state
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);

  // Custom instructions state
  const [customChatInstructions, setCustomChatInstructions] = useState('');
  const [customCvInstructions, setCustomCvInstructions] = useState('');
  const [useCustomInstructions, setUseCustomInstructions] = useState(false);
  const [savingCustomInstructions, setSavingCustomInstructions] = useState(false);

  // Fetch current AI settings
  const { data: settings, isLoading } = useQuery<PersonalAISettings>({
    queryKey: ['profile-ai-settings'],
    queryFn: async () => {
      const response = await api.get('/profile/ai-settings');
      return response.data;
    }
  });

  // Fetch setup guide
  const { data: guide } = useQuery<SetupGuide>({
    queryKey: ['groq-setup-guide'],
    queryFn: async () => {
      const response = await api.get('/profile/ai-settings/guide');
      return response.data;
    }
  });

  // Fetch custom instructions
  const { data: customInstructions } = useQuery<CustomInstructions>({
    queryKey: ['custom-instructions'],
    queryFn: async () => {
      const response = await api.get('/users/me/custom-instructions');
      return response.data;
    }
  });

  // Update settings when loaded
  useEffect(() => {
    if (settings) {
      setUsePersonalKey(settings.use_personal_ai_key);
    }
  }, [settings]);

  // Update custom instructions when loaded
  useEffect(() => {
    if (customInstructions) {
      setCustomChatInstructions(customInstructions.custom_chat_instructions || '');
      setCustomCvInstructions(customInstructions.custom_cv_analysis_instructions || '');
      setUseCustomInstructions(customInstructions.use_custom_instructions);
    }
  }, [customInstructions]);

  // Update AI settings mutation
  const updateSettings = useMutation({
    mutationFn: async (data: { personal_groq_api_key?: string; use_personal_ai_key: boolean }) => {
      const response = await api.put('/profile/ai-settings', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile-ai-settings'] });
      setApiKey(''); // Clear input after save
      alert('✅ AI settings updated successfully!');
    },
    onError: (error: any) => {
      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
    }
  });

  // Update custom instructions mutation
  const updateCustomInstructions = useMutation({
    mutationFn: async (data: CustomInstructions) => {
      const response = await api.put('/users/me/custom-instructions', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['custom-instructions'] });
      alert('✅ Custom instructions updated successfully!');
    },
    onError: (error: any) => {
      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
    }
  });

  // Delete API key mutation
  const deleteKey = useMutation({
    mutationFn: async () => {
      const response = await api.delete('/profile/ai-settings');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile-ai-settings'] });
      setApiKey('');
      setUsePersonalKey(false);
      alert('✅ Personal API key removed successfully!');
    },
    onError: (error: any) => {
      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
    }
  });

  // Test API key
  const testApiKey = async () => {
    if (!apiKey.trim()) {
      alert('Please enter an API key to test');
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const response = await api.post('/profile/ai-settings/test', {
        api_key: apiKey
      });
      setTestResult(response.data);
    } catch (error: any) {
      setTestResult({
        success: false,
        message: error.response?.data?.detail || error.message
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    const data: any = {
      use_personal_ai_key: usePersonalKey
    };

    if (apiKey.trim()) {
      data.personal_groq_api_key = apiKey;
    }

    updateSettings.mutate(data);
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to remove your personal API key?')) {
      deleteKey.mutate();
    }
  };

  const handleSaveCustomInstructions = () => {
    setSavingCustomInstructions(true);
    updateCustomInstructions.mutate({
      custom_chat_instructions: customChatInstructions.trim() || undefined,
      custom_cv_analysis_instructions: customCvInstructions.trim() || undefined,
      use_custom_instructions: useCustomInstructions
    });
    setSavingCustomInstructions(false);
  };

  const handleChangePassword = async () => {
    setPasswordError('');

    // Validation
    if (!oldPassword || !newPassword || !confirmPassword) {
      setPasswordError('All fields are required');
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setPasswordError('Password must be at least 8 characters long');
      return;
    }

    setChangingPassword(true);

    try {
      await api.post('/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword
      });

      alert('✅ Password changed successfully!');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      setPasswordError(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setChangingPassword(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Profile Settings</h1>

      {/* Personal AI Configuration Card */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">Personal AI Configuration</h2>
            <p className="text-sm text-gray-600 mt-1">
              🎁 <strong>100% Free</strong> - Get your personal Groq API key (no credit card required)
            </p>
          </div>
          <button
            onClick={() => setShowGuide(!showGuide)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            {showGuide ? '📖 Hide Guide' : '📖 Setup Guide'}
          </button>
        </div>

        {/* Warning if no personal key */}
        {!settings?.has_personal_key && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <div className="flex items-center">
              <span className="text-yellow-600 text-xl mr-2">⚠️</span>
              <div>
                <p className="text-yellow-800 font-medium">Personal API Key Required</p>
                <p className="text-yellow-700 text-sm">
                  The system API key has very limited usage. Please add your free personal key below to use AI features.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Current Status */}
        {settings?.has_personal_key && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <div className="flex items-center">
              <span className="text-green-600 text-xl mr-2">✅</span>
              <div>
                <p className="text-green-800 font-medium">Personal API Key Configured</p>
                <p className="text-green-600 text-sm">
                  Preview: <code className="bg-green-100 px-2 py-1 rounded">{settings.key_preview}</code>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Setup Guide */}
        {showGuide && guide && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">{guide.title}</h3>
            
            {/* Benefits */}
            <div className="mb-6">
              <h4 className="font-medium text-blue-800 mb-2">✨ Benefits:</h4>
              <ul className="space-y-1">
                {guide.benefits.map((benefit, index) => (
                  <li key={index} className="text-blue-700 text-sm">{benefit}</li>
                ))}
              </ul>
            </div>

            {/* Steps */}
            <div className="space-y-4 mb-6">
              {guide.steps.map((step) => (
                <div key={step.number} className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                    {step.number}
                  </div>
                  <div className="flex-1">
                    <h5 className="font-medium text-blue-900">{step.title}</h5>
                    <p className="text-blue-700 text-sm mt-1">{step.description}</p>
                    {step.url && (
                      <a
                        href={step.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm font-medium mt-1 inline-block"
                      >
                        {step.url} →
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Model Info */}
            <div className="bg-white rounded p-4 border border-blue-200">
              <h4 className="font-medium text-blue-800 mb-2">🚀 Model Information:</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li><strong>Model:</strong> {guide.model_info.name}</li>
                <li><strong>Speed:</strong> {guide.model_info.speed}</li>
                <li><strong>Context Window:</strong> {guide.model_info.context}</li>
              </ul>
            </div>
          </div>
        )}

        {/* API Key Input */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Groq API Key
            </label>
            <div className="flex gap-2">
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={settings?.has_personal_key ? "Enter new key to replace" : "gsk_..."}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                onClick={testApiKey}
                disabled={testing || !apiKey.trim()}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {testing ? '⏳ Testing...' : '🧪 Test'}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Your personal Groq API key. Leave empty to keep current key.
            </p>
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`p-4 rounded-lg border ${
              testResult.success 
                ? 'bg-green-50 border-green-200' 
                : 'bg-red-50 border-red-200'
            }`}>
              <p className={`font-medium ${
                testResult.success ? 'text-green-800' : 'text-red-800'
              }`}>
                {testResult.success ? '✅ Success!' : '❌ Failed'}
              </p>
              <p className={`text-sm ${
                testResult.success ? 'text-green-700' : 'text-red-700'
              }`}>
                {testResult.message}
              </p>
              {testResult.response_time && (
                <p className="text-xs text-green-600 mt-1">
                  Response time: {testResult.response_time.toFixed(2)}s
                </p>
              )}
            </div>
          )}

          {/* Toggle Use Personal Key */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="usePersonalKey"
              checked={usePersonalKey}
              onChange={(e) => setUsePersonalKey(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="usePersonalKey" className="ml-2 block text-sm text-gray-700">
              Use my personal API key for AI operations
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              onClick={handleSave}
              disabled={updateSettings.isPending}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed font-medium"
            >
              {updateSettings.isPending ? '⏳ Saving...' : '💾 Save Settings'}
            </button>
            
            {settings?.has_personal_key && (
              <button
                onClick={handleDelete}
                disabled={deleteKey.isPending}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-red-400 disabled:cursor-not-allowed font-medium"
              >
                {deleteKey.isPending ? '⏳ Removing...' : '🗑️ Remove Key'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Change Password Card */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Change Password</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Password
            </label>
            <input
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter current password"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New Password
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter new password (min 8 characters)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirm New Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Confirm new password"
            />
          </div>

          {/* Error Message */}
          {passwordError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">❌ {passwordError}</p>
            </div>
          )}

          {/* Change Password Button */}
          <button
            onClick={handleChangePassword}
            disabled={changingPassword}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed font-medium"
          >
            {changingPassword ? '⏳ Changing Password...' : '🔒 Change Password'}
          </button>
        </div>
      </div>

      {/* Custom AI Instructions Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🤖</span>
          <h2 className="text-xl font-semibold text-gray-900">Custom AI Instructions</h2>
        </div>
        
        <p className="text-gray-600 mb-6">
          Customize how the AI assistant responds to your chat messages and analyzes CVs. 
          These personal instructions will override the system defaults when enabled.
        </p>

        <div className="space-y-6">
          {/* Enable Custom Instructions Toggle */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">Enable Custom Instructions</h3>
              <p className="text-sm text-gray-600">Use your personal AI instructions instead of system defaults</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={useCustomInstructions}
                onChange={(e) => setUseCustomInstructions(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* Chat Instructions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              💬 Custom Chat Instructions
            </label>
            <textarea
              value={customChatInstructions}
              onChange={(e) => setCustomChatInstructions(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
              placeholder="Enter custom instructions for AI chat responses (e.g., 'Always be concise and professional', 'Focus on technical skills when discussing candidates')"
              disabled={!useCustomInstructions}
            />
            <p className="text-xs text-gray-500 mt-1">
              These instructions will guide how the AI responds to your chat messages
            </p>
          </div>

          {/* CV Analysis Instructions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📄 Custom CV Analysis Instructions
            </label>
            <textarea
              value={customCvInstructions}
              onChange={(e) => setCustomCvInstructions(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
              placeholder="Enter custom instructions for CV analysis (e.g., 'Pay special attention to leadership experience', 'Prioritize certifications and education')"
              disabled={!useCustomInstructions}
            />
            <p className="text-xs text-gray-500 mt-1">
              These instructions will guide how the AI analyzes and evaluates CVs
            </p>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSaveCustomInstructions}
            disabled={savingCustomInstructions || updateCustomInstructions.isPending}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed font-medium transition-colors"
          >
            {savingCustomInstructions || updateCustomInstructions.isPending ? '⏳ Saving...' : '💾 Save Custom Instructions'}
          </button>
        </div>
      </div>

      {/* Information Card */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-medium text-yellow-800 mb-2">ℹ️ Important Information</h3>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Your API key is encrypted and stored securely</li>
          <li>• When enabled, your personal key will be used for resume parsing and AI chat</li>
          <li>• This allows you to have separate rate limits from the system</li>
          <li>• You can disable your personal key anytime without deleting it</li>
          <li>• Free Groq tier provides generous limits with no credit card required</li>
        </ul>
      </div>
    </div>
  );
}
