import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Lock, User, Eye, EyeOff, Shield, AlertCircle } from 'lucide-react';

interface LoginFormProps {
  onLogin: (credentials: { username: string; password: string }) => Promise<boolean>;
  isLoading?: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin, isLoading = false }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!credentials.username || !credentials.password) {
      setError('Please enter both username and password');
      return;
    }

    try {
      const success = await onLogin(credentials);
      if (!success) {
        setError('Invalid username or password');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    }
  };

  const handleInputChange = (field: 'username' | 'password', value: string) => {
    setCredentials(prev => ({ ...prev, [field]: value }));
    if (error) setError(''); // Clear error when user starts typing
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23334155" fill-opacity="0.1"%3E%3Ccircle cx="7" cy="7" r="1"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="flex items-center justify-center mb-4"
          >
            <div className="relative">
              <Brain className="w-12 h-12 text-accent-500" />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
            </div>
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-3xl font-bold gradient-text mb-2"
          >
            BeeMind Dashboard
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="text-dark-400"
          >
            AI Evolution Monitoring & Analytics
          </motion.p>
        </div>

        {/* Login Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="glass rounded-xl p-8 border border-dark-600"
        >
          <div className="flex items-center space-x-2 mb-6">
            <Shield className="w-5 h-5 text-accent-500" />
            <h2 className="text-xl font-semibold text-dark-100">Secure Login</h2>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4 flex items-center space-x-2"
            >
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              <span className="text-red-400 text-sm">{error}</span>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username Field */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Username or Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="w-4 h-4 text-dark-500" />
                </div>
                <input
                  type="text"
                  value={credentials.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  className="beemind-input pl-10"
                  placeholder="Enter your username"
                  disabled={isLoading}
                  autoComplete="username"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-4 h-4 text-dark-500" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={credentials.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className="beemind-input pl-10 pr-10"
                  placeholder="Enter your password"
                  disabled={isLoading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-dark-500 hover:text-dark-300"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <div className="flex items-center justify-between">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-dark-600 bg-dark-700 text-accent-600 focus:ring-accent-500 focus:ring-offset-dark-900"
                  disabled={isLoading}
                />
                <span className="text-sm text-dark-300">Remember me</span>
              </label>
              
              <button
                type="button"
                className="text-sm text-accent-400 hover:text-accent-300 transition-colors"
                disabled={isLoading}
              >
                Forgot password?
              </button>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={isLoading || !credentials.username || !credentials.password}
              className="w-full beemind-button-primary py-3 text-base font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Signing in...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 pt-6 border-t border-dark-600">
            <div className="bg-dark-700/30 rounded-lg p-4">
              <h3 className="text-sm font-medium text-dark-300 mb-2">Demo Credentials</h3>
              <div className="space-y-1 text-xs text-dark-400">
                <p><strong>Admin:</strong> admin / BeeMind2025!</p>
                <p><strong>Researcher:</strong> dr_smith / research123</p>
                <p><strong>Viewer:</strong> analyst / view123</p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-xs text-dark-500">
              Secured by BeeMind Authentication System
            </p>
            <div className="flex items-center justify-center space-x-4 mt-2 text-xs text-dark-500">
              <span>v1.0.0</span>
              <span>•</span>
              <span>beemind.dev</span>
              <span>•</span>
              <span>© 2025</span>
            </div>
          </div>
        </motion.div>

        {/* Security Notice */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-6 text-center"
        >
          <div className="flex items-center justify-center space-x-2 text-sm text-dark-500">
            <Lock className="w-3 h-3" />
            <span>Your connection is secure and encrypted</span>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default LoginForm;
