import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, Shield, Key, Settings, UserPlus, Edit, Trash2, Eye, EyeOff, Download, RefreshCw } from 'lucide-react';

interface User {
  user_id: string;
  username: string;
  email: string;
  role: 'admin' | 'researcher' | 'viewer' | 'guest';
  created_at: string;
  last_login?: string;
  is_active: boolean;
  api_key?: string;
}

interface Session {
  session_id: string;
  user_id: string;
  created_at: string;
  expires_at: string;
  ip_address?: string;
  is_active: boolean;
}

const AdminPanel: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedTab, setSelectedTab] = useState<'users' | 'sessions' | 'settings'>('users');
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});
  const [userStats, setUserStats] = useState({
    total_users: 0,
    active_users: 0,
    active_sessions: 0,
    role_distribution: {} as Record<string, number>
  });

  useEffect(() => {
    // Mock user data
    const mockUsers: User[] = [
      {
        user_id: 'admin_001',
        username: 'admin',
        email: 'admin@beemind.dev',
        role: 'admin',
        created_at: '2025-01-01T00:00:00Z',
        last_login: '2025-08-07T11:30:00Z',
        is_active: true,
        api_key: 'bm_admin_key_12345'
      },
      {
        user_id: 'researcher_001',
        username: 'dr_smith',
        email: 'smith@research.org',
        role: 'researcher',
        created_at: '2025-02-15T10:00:00Z',
        last_login: '2025-08-07T09:15:00Z',
        is_active: true,
        api_key: 'bm_researcher_key_67890'
      },
      {
        user_id: 'viewer_001',
        username: 'analyst',
        email: 'analyst@company.com',
        role: 'viewer',
        created_at: '2025-03-01T14:30:00Z',
        last_login: '2025-08-06T16:45:00Z',
        is_active: true,
        api_key: 'bm_viewer_key_abcdef'
      }
    ];

    const mockSessions: Session[] = [
      {
        session_id: 'sess_001',
        user_id: 'admin_001',
        created_at: '2025-08-07T11:30:00Z',
        expires_at: '2025-08-08T11:30:00Z',
        ip_address: '192.168.1.100',
        is_active: true
      },
      {
        session_id: 'sess_002',
        user_id: 'researcher_001',
        created_at: '2025-08-07T09:15:00Z',
        expires_at: '2025-08-08T09:15:00Z',
        ip_address: '10.0.0.50',
        is_active: true
      }
    ];

    setUsers(mockUsers);
    setSessions(mockSessions);
    
    // Calculate stats
    const stats = {
      total_users: mockUsers.length,
      active_users: mockUsers.filter(u => u.is_active).length,
      active_sessions: mockSessions.filter(s => s.is_active).length,
      role_distribution: mockUsers.reduce((acc, user) => {
        acc[user.role] = (acc[user.role] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    };
    setUserStats(stats);
  }, []);

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'text-red-400 bg-red-500/10';
      case 'researcher':
        return 'text-blue-400 bg-blue-500/10';
      case 'viewer':
        return 'text-green-400 bg-green-500/10';
      case 'guest':
        return 'text-gray-400 bg-gray-500/10';
      default:
        return 'text-gray-400 bg-gray-500/10';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const toggleApiKeyVisibility = (userId: string) => {
    setShowApiKeys(prev => ({
      ...prev,
      [userId]: !prev[userId]
    }));
  };

  const CreateUserModal = () => {
    const [formData, setFormData] = useState({
      username: '',
      email: '',
      password: '',
      role: 'viewer' as User['role']
    });

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      // Here you would call the API to create user
      console.log('Creating user:', formData);
      setShowCreateUser(false);
      setFormData({ username: '', email: '', password: '', role: 'viewer' });
    };

    if (!showCreateUser) return null;

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-dark-800 rounded-lg p-6 w-full max-w-md border border-dark-600"
        >
          <h3 className="text-xl font-semibold text-dark-100 mb-4">Create New User</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                className="beemind-input"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className="beemind-input"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                className="beemind-input"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">Role</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value as User['role'] }))}
                className="beemind-input"
              >
                <option value="viewer">Viewer</option>
                <option value="researcher">Researcher</option>
                <option value="admin">Admin</option>
                <option value="guest">Guest</option>
              </select>
            </div>
            
            <div className="flex space-x-3 pt-4">
              <button type="submit" className="beemind-button-primary flex-1">
                Create User
              </button>
              <button
                type="button"
                onClick={() => setShowCreateUser(false)}
                className="beemind-button-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    );
  };

  return (
    <div className="beemind-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-dark-100 flex items-center space-x-2">
          <Shield className="w-5 h-5 text-accent-500" />
          <span>Admin Panel</span>
        </h2>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowCreateUser(true)}
            className="beemind-button-primary text-sm py-2 px-3 flex items-center space-x-2"
          >
            <UserPlus className="w-4 h-4" />
            <span>Add User</span>
          </button>
          
          <button className="beemind-button-secondary p-2" title="Refresh">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-dark-300">Total Users</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">{userStats.total_users}</p>
        </div>

        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-4 h-4 text-green-400" />
            <span className="text-sm text-dark-300">Active Users</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">{userStats.active_users}</p>
        </div>

        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Shield className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-dark-300">Active Sessions</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">{userStats.active_sessions}</p>
        </div>

        <div className="bg-dark-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Key className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-dark-300">API Keys</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">{users.filter(u => u.api_key).length}</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-dark-700/30 rounded-lg p-1">
        {[
          { key: 'users', label: 'Users', icon: Users },
          { key: 'sessions', label: 'Sessions', icon: Shield },
          { key: 'settings', label: 'Settings', icon: Settings }
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setSelectedTab(key as any)}
            className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              selectedTab === key
                ? 'bg-accent-600 text-white'
                : 'text-dark-300 hover:text-dark-100 hover:bg-dark-600'
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Users Tab */}
      {selectedTab === 'users' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-600">
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">User</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">Role</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">Status</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">Last Login</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">API Key</th>
                  <th className="text-right py-3 px-4 text-dark-300 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, index) => (
                  <motion.tr
                    key={user.user_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border-b border-dark-700 hover:bg-dark-700/30 transition-colors"
                  >
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium text-dark-100">{user.username}</p>
                        <p className="text-xs text-dark-400">{user.email}</p>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getRoleColor(user.role)}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <span className={`text-sm ${user.is_active ? 'text-green-400' : 'text-red-400'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-dark-300">
                      {user.last_login ? formatDate(user.last_login) : 'Never'}
                    </td>
                    <td className="py-3 px-4">
                      {user.api_key && (
                        <div className="flex items-center space-x-2">
                          <code className="text-xs bg-dark-700 px-2 py-1 rounded">
                            {showApiKeys[user.user_id] ? user.api_key : '••••••••••••••••'}
                          </code>
                          <button
                            onClick={() => toggleApiKeyVisibility(user.user_id)}
                            className="text-dark-400 hover:text-dark-200"
                          >
                            {showApiKeys[user.user_id] ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                          </button>
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end space-x-2">
                        <button className="text-blue-400 hover:text-blue-300 p-1" title="Edit">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="text-red-400 hover:text-red-300 p-1" title="Delete">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Sessions Tab */}
      {selectedTab === 'sessions' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dark-600">
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">Session ID</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">User</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">IP Address</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">Created</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">Expires</th>
                  <th className="text-left py-3 px-4 text-dark-300 font-medium">Status</th>
                  <th className="text-right py-3 px-4 text-dark-300 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session, index) => {
                  const user = users.find(u => u.user_id === session.user_id);
                  return (
                    <motion.tr
                      key={session.session_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="border-b border-dark-700 hover:bg-dark-700/30 transition-colors"
                    >
                      <td className="py-3 px-4">
                        <code className="text-xs bg-dark-700 px-2 py-1 rounded">
                          {session.session_id.slice(0, 12)}...
                        </code>
                      </td>
                      <td className="py-3 px-4 text-dark-100">
                        {user?.username || 'Unknown'}
                      </td>
                      <td className="py-3 px-4 text-dark-300">
                        {session.ip_address || 'Unknown'}
                      </td>
                      <td className="py-3 px-4 text-dark-300">
                        {formatDate(session.created_at)}
                      </td>
                      <td className="py-3 px-4 text-dark-300">
                        {formatDate(session.expires_at)}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${session.is_active ? 'bg-green-500' : 'bg-red-500'}`}></div>
                          <span className={`text-sm ${session.is_active ? 'text-green-400' : 'text-red-400'}`}>
                            {session.is_active ? 'Active' : 'Expired'}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-end space-x-2">
                          {session.is_active && (
                            <button className="text-red-400 hover:text-red-300 p-1" title="Terminate">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Settings Tab */}
      {selectedTab === 'settings' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Security Settings */}
            <div className="bg-dark-700/30 rounded-lg p-4">
              <h3 className="text-lg font-medium text-dark-200 mb-4">Security Settings</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-dark-300">Session Timeout</span>
                  <select className="beemind-input text-sm py-1 px-2">
                    <option>24 hours</option>
                    <option>12 hours</option>
                    <option>8 hours</option>
                    <option>4 hours</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-dark-300">Require 2FA</span>
                  <input type="checkbox" className="rounded" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-dark-300">API Rate Limiting</span>
                  <input type="checkbox" defaultChecked className="rounded" />
                </div>
              </div>
            </div>

            {/* System Settings */}
            <div className="bg-dark-700/30 rounded-lg p-4">
              <h3 className="text-lg font-medium text-dark-200 mb-4">System Settings</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-dark-300">Auto Cleanup Sessions</span>
                  <input type="checkbox" defaultChecked className="rounded" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-dark-300">Audit Logging</span>
                  <input type="checkbox" defaultChecked className="rounded" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-dark-300">Email Notifications</span>
                  <input type="checkbox" className="rounded" />
                </div>
              </div>
            </div>
          </div>

          {/* Export Options */}
          <div className="bg-dark-700/30 rounded-lg p-4">
            <h3 className="text-lg font-medium text-dark-200 mb-4">Data Export</h3>
            <div className="flex space-x-3">
              <button className="beemind-button-secondary flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export User Data</span>
              </button>
              <button className="beemind-button-secondary flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export Audit Log</span>
              </button>
              <button className="beemind-button-secondary flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export System Config</span>
              </button>
            </div>
          </div>
        </motion.div>
      )}

      <CreateUserModal />
    </div>
  );
};

export default AdminPanel;
