import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/api';
import {
  CogIcon,
  UserGroupIcon,
  ChartBarIcon,
  KeyIcon,
  ShieldCheckIcon,
  ClockIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

interface SystemSetting {
  id: string;
  key: string;
  value: string;
  type: string;
  description: string;
  is_active: boolean;
  updated_at: string;
}

interface SystemStats {
  total_users: number;
  active_users_today: number;
  total_messages_today: number;
  total_uploads_today: number;
  system_messages_used: number;
  system_uploads_used: number;
  system_message_limit: number;
  system_upload_limit: number;
  system_message_percentage: number;
  system_upload_percentage: number;
}

interface UserUsage {
  user_id: string;
  user_email: string;
  user_name: string;
  messages_used_today: number;
  files_uploaded_today: number;
  messages_limit: number;
  uploads_limit: number;
  has_personal_key: boolean;
  last_active: string | null;
  role: string;
  status: string;
}

interface UsageHistory {
  id: string;
  user_email: string;
  action_type: string;
  used_personal_key: boolean;
  tokens_used: number | null;
  cost_usd: number | null;
  timestamp: string;
}

const AdminSettings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'settings' | 'stats' | 'users' | 'history'>('settings');
  const [showApiKey, setShowApiKey] = useState(false);
  const [editingSettings, setEditingSettings] = useState<Record<string, string>>({});
  const queryClient = useQueryClient();

  // Fetch all settings
  const { data: settingsData, isLoading: settingsLoading } = useQuery({
    queryKey: ['admin-settings'],
    queryFn: async () => {
      console.log('🔧 [UnifiedSettings] Starting fetchSettings API call');
      console.log('🔧 [UnifiedSettings] API URL: /settings/');
      try {
        const response = await api.get('/settings/');
        console.log('🔧 [UnifiedSettings] Settings API success:', response.status, response.data);
        
        // Transform the data format to match what UnifiedSettings expects
        const transformedSettings = response.data.map((setting: any, index: number) => ({
          id: setting.id || `setting-${index}`,
          key: setting.key,
          value: setting.value || '',
          type: setting.data_type || 'string',
          description: setting.description || '',
          is_active: true, // Default to active
          updated_at: new Date().toISOString()
        }));
        
        console.log('🔧 [UnifiedSettings] Transformed settings:', transformedSettings.length);
        return transformedSettings;
      } catch (error) {
        console.error('🔧 [UnifiedSettings] Settings API error:', error);
        throw error;
      }
    }
  });

  // Fetch system stats
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      const response = await api.get<SystemStats>('/admin/stats/system');
      return response.data;
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  // Fetch user usage
  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users-usage'],
    queryFn: async () => {
      const response = await api.get<{ users: UserUsage[] }>('/admin/users/usage');
      return response.data;
    }
  });

  // Fetch usage history
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['admin-usage-history'],
    queryFn: async () => {
      const response = await api.get<{ history: UsageHistory[] }>('/admin/usage/history?limit=50');
      return response.data;
    }
  });

  // Update settings mutation
  const updateSettingsMutation = useMutation({
    mutationFn: async (settings: Array<{ setting_key: string; setting_value: string; description?: string }>) => {
      console.log('🔧 [UnifiedSettings] Starting bulk update...');
      console.log('🔧 [UnifiedSettings] Settings to update:', settings);
      
      // Try individual updates since bulk-update might be broken
      const results = [];
      for (const setting of settings) {
        try {
          console.log(`🔧 [UnifiedSettings] Updating ${setting.setting_key}...`);
          const response = await api.put(`/settings/${setting.setting_key}`, {
            setting_value: setting.setting_value,
            is_active: true
          });
          console.log(`🔧 [UnifiedSettings] Success: ${setting.setting_key}`, response.data);
          results.push({ key: setting.setting_key, success: true });
        } catch (error) {
          console.error(`🔧 [UnifiedSettings] Failed: ${setting.setting_key}`, error);
          results.push({ key: setting.setting_key, success: false, error });
        }
      }
      
      console.log('🔧 [UnifiedSettings] All updates completed:', results);
      return results;
    },
    onSuccess: (results) => {
      const successful = results.filter(r => r.success).length;
      const total = results.length;
      
      queryClient.invalidateQueries({ queryKey: ['admin-settings'] });
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
      setEditingSettings({});
      
      if (successful === total) {
        alert(`✅ All ${total} settings updated successfully!`);
      } else {
        alert(`⚠️ Updated ${successful}/${total} settings. Check console for details.`);
      }
    },
    onError: (error: any) => {
      console.error('🔧 [UnifiedSettings] Mutation error:', error);
      alert(`Failed to update settings: ${error.response?.data?.detail || error.message}`);
    }
  });

  // Reset daily limits mutation
  const resetLimitsMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/admin/system/reset-daily-limits');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
      queryClient.invalidateQueries({ queryKey: ['admin-users-usage'] });
      alert('Daily limits reset successfully!');
    }
  });

  const handleSettingChange = (key: string, value: string) => {
    setEditingSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveSettings = () => {
    console.log('🔧 [UnifiedSettings] Save button clicked');
    console.log('🔧 [UnifiedSettings] Current editingSettings:', editingSettings);
    
    const updates = Object.entries(editingSettings).map(([key, value]) => ({
      setting_key: key,
      setting_value: value
    }));

    console.log('🔧 [UnifiedSettings] Updates to send:', updates);

    if (updates.length === 0) {
      console.log('🔧 [UnifiedSettings] No changes to save');
      alert('No changes to save');
      return;
    }

    console.log('🔧 [UnifiedSettings] Sending bulk update...');
    updateSettingsMutation.mutate(updates);
  };

  const getCurrentValue = (setting: SystemSetting) => {
    return editingSettings[setting.key] !== undefined 
      ? editingSettings[setting.key] 
      : setting.value;
  };

  const hasChanges = Object.keys(editingSettings).length > 0;

  // Group settings by category
  const groupedSettings = settingsData?.reduce((acc: Record<string, SystemSetting[]>, setting: SystemSetting) => {
    let category = 'General';
    
    if (setting.key.includes('groq') || setting.key.includes('ai_model') || setting.key.includes('openrouter')) {
      category = 'AI Configuration';
    } else if (setting.key.includes('limit') || setting.key.includes('used')) {
      category = 'Usage Limits';
    } else if (setting.key.includes('require') || setting.key.includes('enforce')) {
      category = 'Access Control';
    } else if (setting.key.includes('default')) {
      category = 'Default Settings';
    }
    
    if (!acc[category]) acc[category] = [];
    acc[category].push(setting);
    return acc;
  }, {});

  const renderSettingInput = (setting: SystemSetting) => {
    const currentValue = getCurrentValue(setting);
    
    // Special handling for API keys
    if (setting.key.includes('api_key')) {
      return (
        <div className="relative">
          <input
            type={showApiKey ? 'text' : 'password'}
            value={currentValue}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Enter API key..."
          />
          <button
            type="button"
            onClick={() => setShowApiKey(!showApiKey)}
            className="absolute right-2 top-2 text-gray-500 hover:text-gray-700"
          >
            {showApiKey ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
          </button>
        </div>
      );
    }

    // Boolean settings
    if (setting.type === 'boolean') {
      return (
        <select
          value={currentValue}
          onChange={(e) => handleSettingChange(setting.key, e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="true">Enabled</option>
          <option value="false">Disabled</option>
        </select>
      );
    }

    // Number settings
    if (setting.type === 'number') {
      return (
        <input
          type="number"
          value={currentValue}
          onChange={(e) => handleSettingChange(setting.key, e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          min="0"
        />
      );
    }

    // Instruction fields - use large textarea
    if (setting.key === 'resume_analysis_instructions' || 
        setting.key === 'chat_system_instructions' ||
        setting.key.includes('instructions') || 
        setting.key.includes('prompt')) {
      return (
        <textarea
          value={currentValue}
          onChange={(e) => handleSettingChange(setting.key, e.target.value)}
          rows={12}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm resize-vertical"
          placeholder="Enter instructions..."
        />
      );
    }

    // Text settings
    return (
      <input
        type="text"
        value={currentValue}
        onChange={(e) => handleSettingChange(setting.key, e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
      />
    );
  };

  const renderSettingsTab = () => (
    <div className="space-y-6">
      {/* Header with Save Button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">System Settings</h2>
          <p className="mt-1 text-sm text-gray-500">
            Configure all system settings without restarting the server
          </p>
        </div>
        {hasChanges && (
          <button
            onClick={handleSaveSettings}
            disabled={updateSettingsMutation.isPending}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {updateSettingsMutation.isPending ? (
              <>
                <ArrowPathIcon className="h-5 w-5 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <CheckCircleIcon className="h-5 w-5" />
                Save Changes ({Object.keys(editingSettings).length})
              </>
            )}
          </button>
        )}
      </div>

      {settingsLoading ? (
        <div className="text-center py-12">
          <ArrowPathIcon className="h-8 w-8 animate-spin mx-auto text-indigo-600" />
          <p className="mt-2 text-gray-500">Loading settings...</p>
          <p className="mt-1 text-xs text-gray-400">Debug: settingsLoading = {String(settingsLoading)}</p>
        </div>
      ) : (
        <div className="space-y-8">
          {Object.entries(groupedSettings || {}).map(([category, settings]) => (
            <div key={category} className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h3 className="text-lg font-semibold text-gray-900">{category}</h3>
              </div>
              <div className="px-6 py-4 space-y-4">
                {(settings as SystemSetting[]).map((setting: SystemSetting) => {
                  const isInstructionField = setting.key === 'resume_analysis_instructions' || 
                                           setting.key === 'chat_system_instructions' ||
                                           setting.key.includes('instructions') || 
                                           setting.key.includes('prompt');
                  
                  return (
                    <div key={setting.id} className={`grid gap-4 ${isInstructionField ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-3'} items-start`}>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          {setting.key.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                        </label>
                        <p className="mt-1 text-xs text-gray-500">{setting.description}</p>
                        <p className="mt-1 text-xs text-gray-400">
                          Last updated: {new Date(setting.updated_at).toLocaleString()}
                        </p>
                      </div>
                      <div className={isInstructionField ? '' : 'md:col-span-2'}>
                        {renderSettingInput(setting)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderStatsTab = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">System Statistics</h2>
        <p className="mt-1 text-sm text-gray-500">Real-time monitoring of system usage and performance</p>
      </div>

      {statsLoading ? (
        <div className="text-center py-12">
          <ArrowPathIcon className="h-8 w-8 animate-spin mx-auto text-indigo-600" />
          <p className="mt-2 text-gray-500">Loading statistics...</p>
        </div>
      ) : (
        <>
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Users</p>
                  <p className="mt-1 text-3xl font-bold text-gray-900">{statsData?.total_users || 0}</p>
                </div>
                <UserGroupIcon className="h-10 w-10 text-blue-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Active Today</p>
                  <p className="mt-1 text-3xl font-bold text-gray-900">{statsData?.active_users_today || 0}</p>
                </div>
                <ChartBarIcon className="h-10 w-10 text-green-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Messages Today</p>
                  <p className="mt-1 text-3xl font-bold text-gray-900">{statsData?.total_messages_today || 0}</p>
                </div>
                <DocumentTextIcon className="h-10 w-10 text-purple-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Uploads Today</p>
                  <p className="mt-1 text-3xl font-bold text-gray-900">{statsData?.total_uploads_today || 0}</p>
                </div>
                <KeyIcon className="h-10 w-10 text-orange-500" />
              </div>
            </div>
          </div>

          {/* System Limits Usage */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">System-Wide Limits</h3>
              <button
                onClick={() => resetLimitsMutation.mutate()}
                disabled={resetLimitsMutation.isPending}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-red-50 text-red-700 rounded-lg hover:bg-red-100 disabled:opacity-50"
              >
                <ArrowPathIcon className={`h-4 w-4 ${resetLimitsMutation.isPending ? 'animate-spin' : ''}`} />
                Reset Daily Limits
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">AI Messages</span>
                  <span className="text-sm text-gray-500">
                    {statsData?.system_messages_used || 0} / {statsData?.system_message_limit || 0}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${
                      (statsData?.system_message_percentage || 0) > 90 
                        ? 'bg-red-500' 
                        : (statsData?.system_message_percentage || 0) > 70 
                        ? 'bg-yellow-500' 
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(statsData?.system_message_percentage || 0, 100)}%` }}
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  {statsData?.system_message_percentage || 0}% used
                </p>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">File Uploads</span>
                  <span className="text-sm text-gray-500">
                    {statsData?.system_uploads_used || 0} / {statsData?.system_upload_limit || 0}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${
                      (statsData?.system_upload_percentage || 0) > 90 
                        ? 'bg-red-500' 
                        : (statsData?.system_upload_percentage || 0) > 70 
                        ? 'bg-yellow-500' 
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(statsData?.system_upload_percentage || 0, 100)}%` }}
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  {statsData?.system_upload_percentage || 0}% used
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderUsersTab = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Usage Tracking</h2>
        <p className="mt-1 text-sm text-gray-500">
          Monitor individual user limits and usage. To manage users (create, edit, delete, roles), go to{' '}
          <a href="/admin/users" className="text-indigo-600 hover:text-indigo-800 font-medium underline">
            User Management
          </a>
        </p>
      </div>

      {usersLoading ? (
        <div className="text-center py-12">
          <ArrowPathIcon className="h-8 w-8 animate-spin mx-auto text-indigo-600" />
          <p className="mt-2 text-gray-500">Loading users...</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Messages
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploads
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Personal Key
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Active
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {usersData?.users?.map((user: UserUsage) => (
                  <tr key={user.user_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{user.user_name}</div>
                        <div className="text-sm text-gray-500">{user.user_email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        user.role === 'admin' 
                          ? 'bg-purple-100 text-purple-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {user.messages_used_today} / {user.messages_limit}
                      </div>
                      <div className="w-24 bg-gray-200 rounded-full h-2 mt-1">
                        <div
                          className="bg-indigo-500 h-2 rounded-full"
                          style={{ width: `${Math.min((user.messages_used_today / user.messages_limit) * 100, 100)}%` }}
                        />
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {user.files_uploaded_today} / {user.uploads_limit}
                      </div>
                      <div className="w-24 bg-gray-200 rounded-full h-2 mt-1">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${Math.min((user.files_uploaded_today / user.uploads_limit) * 100, 100)}%` }}
                        />
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.has_personal_key ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      ) : (
                        <ExclamationCircleIcon className="h-5 w-5 text-gray-300" />
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.last_active ? new Date(user.last_active).toLocaleDateString() : 'Never'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );

  const renderHistoryTab = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Usage History</h2>
        <p className="mt-1 text-sm text-gray-500">Track all AI operations and file uploads</p>
      </div>

      {historyLoading ? (
        <div className="text-center py-12">
          <ArrowPathIcon className="h-8 w-8 animate-spin mx-auto text-indigo-600" />
          <p className="mt-2 text-gray-500">Loading history...</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    API Key Used
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tokens
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {historyData?.history?.map((record: UsageHistory) => (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(record.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {record.user_email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        record.action_type === 'ai_message' 
                          ? 'bg-blue-100 text-blue-800' 
                          : record.action_type === 'file_upload'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-purple-100 text-purple-800'
                      }`}>
                        {record.action_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        record.used_personal_key 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        {record.used_personal_key ? 'Personal' : 'System'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {record.tokens_used || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {record.cost_usd ? `$${record.cost_usd.toFixed(4)}` : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3">
            <ShieldCheckIcon className="h-10 w-10 text-indigo-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Control Panel</h1>
              <p className="mt-1 text-sm text-gray-500">
                Full system control and monitoring dashboard
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('settings')}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'settings'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <CogIcon className="h-5 w-5" />
                Settings
              </button>

              <button
                onClick={() => setActiveTab('stats')}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'stats'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <ChartBarIcon className="h-5 w-5" />
                Statistics
              </button>

              <button
                onClick={() => setActiveTab('users')}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'users'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <UserGroupIcon className="h-5 w-5" />
                <div className="flex flex-col items-start">
                  <span>Usage Tracking</span>
                  <span className="text-xs font-normal text-gray-400">Monitor user activity</span>
                </div>
              </button>

              <button
                onClick={() => setActiveTab('history')}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'history'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <ClockIcon className="h-5 w-5" />
                Usage History
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'settings' && renderSettingsTab()}
          {activeTab === 'stats' && renderStatsTab()}
          {activeTab === 'users' && renderUsersTab()}
          {activeTab === 'history' && renderHistoryTab()}
        </div>
      </div>
    </div>
  );
};

export default AdminSettings;
