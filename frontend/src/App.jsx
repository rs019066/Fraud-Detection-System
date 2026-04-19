/**
 * Fraud Detection Application - Integrated Version
 * =================================================
 * Dark blue theme consistent with Home page
 */

import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useLocation } from 'react-router-dom';
import {
  AlertCircle, CheckCircle, TrendingUp, Shield, Activity, Database,
  Trash2, Search, Zap, Target, LogOut, Home, Users, BarChart2
} from 'lucide-react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './components/LoginPage';
import AdminDashboard from './components/AdminDashboard';
import HomePage from './components/Home';
import AboutPage from './components/About';
import ContactPage from './components/Contact';
import VisualizationPage from './components/VisualizationPage';

const API_URL = 'http://localhost:8000';

// ============================================================================
// API Service with Authentication
// ============================================================================

const api = {
  predict: async (transaction, token) => {
    const response = await fetch(`${API_URL}/api/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(transaction),
    });
    if (!response.ok) throw new Error(`Predict failed: ${response.status} ${response.statusText}`);
    return response.json();
  },

  getTransactions: async (token) => {
    const response = await fetch(`${API_URL}/api/transactions`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error(`Get transactions failed: ${response.status}`);
    return response.json();
  },

  getStatistics: async (token) => {
    const response = await fetch(`${API_URL}/api/statistics`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error(`Get statistics failed: ${response.status}`);
    return response.json();
  },

  deleteTransaction: async (id, token) => {
    const response = await fetch(`${API_URL}/api/transactions/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error(`Delete failed: ${response.status}`);
    return true;
  },

  getOptions: async () => {
    const response = await fetch(`${API_URL}/api/options`);
    if (!response.ok) throw new Error(`Get options failed: ${response.status}`);
    return response.json();
  },

  getFraudScenarios: async () => {
    const response = await fetch(`${API_URL}/api/fraud-scenarios`);
    if (!response.ok) throw new Error(`Get scenarios failed: ${response.status}`);
    return response.json();
  }
};

// ============================================================================
// Protected Route Component
// ============================================================================

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// ============================================================================
// Navigation Bar Component
// ============================================================================

const NavBar = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const navLink = (to, label) => {
    const active = location.pathname === to;
    return (
      <Link
        to={to}
        className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-colors ${
          active
            ? 'border-blue-400 text-blue-300'
            : 'border-transparent text-white/60 hover:text-white hover:border-blue-400/50'
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <nav className="bg-slate-900/95 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">

          {/* Left — Logo + public links + protected links */}
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2 flex-shrink-0">
              <Shield className="h-7 w-7 text-blue-400" />
              <span className="text-lg font-bold text-white">Fraud Detection</span>
            </Link>

            <div className="hidden sm:flex sm:items-center sm:gap-6 h-16">
              {navLink('/', 'Home')}
              {navLink('/about', 'About')}
              {navLink('/contact', 'Contact')}

              {user && (
                <>
                  <Link
                    to="/dashboard"
                    className={`inline-flex items-center gap-1 px-1 pt-1 text-sm font-medium border-b-2 transition-colors ${
                      location.pathname === '/dashboard'
                        ? 'border-blue-400 text-blue-300'
                        : 'border-transparent text-white/60 hover:text-white hover:border-blue-400/50'
                    }`}
                  >
                    <Home className="h-4 w-4" />
                    Dashboard
                  </Link>

                  {/* ── NEW: Visualization link ── */}
                  <Link
                    to="/visualization"
                    className={`inline-flex items-center gap-1 px-1 pt-1 text-sm font-medium border-b-2 transition-colors ${
                      location.pathname === '/visualization'
                        ? 'border-blue-400 text-blue-300'
                        : 'border-transparent text-white/60 hover:text-white hover:border-blue-400/50'
                    }`}
                  >
                    <BarChart2 className="h-4 w-4" />
                    Visualization
                  </Link>

                  {isAdmin() && (
                    <Link
                      to="/admin"
                      className={`inline-flex items-center gap-1 px-1 pt-1 text-sm font-medium border-b-2 transition-colors ${
                        location.pathname === '/admin'
                          ? 'border-blue-400 text-blue-300'
                          : 'border-transparent text-white/60 hover:text-white hover:border-blue-400/50'
                      }`}
                    >
                      <Users className="h-4 w-4" />
                      Admin
                    </Link>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Right — login button OR user info + logout */}
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm text-white/80">
                  <span className="font-medium text-white">{user.username}</span>
                  <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                    user.role === 'admin'
                      ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30'
                      : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                  }`}>
                    {user.role}
                  </span>
                </span>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center gap-2 px-3 py-2 border border-white/20 rounded-md text-sm font-medium text-white/80 bg-white/5 hover:bg-white/10 transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-md transition-colors"
              >
                Login
              </Link>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
};

// ============================================================================
// Transaction Form Component
// ============================================================================

const SimplifiedTransactionForm = ({ onPredict, options }) => {
  const [formData, setFormData] = useState({
    card_number: '1234',
    card_type: 'Visa',
    transaction_amount: 150.00,
    merchant_name: 'Amazon.com',
    merchant_category: 'Online Shopping',
    location_city: 'New York',
    location_country: 'USA',
    is_online: true,
    is_international: false,
    transaction_hour: 14,
    day_of_week: 2,
    transaction_type: 'Online',
    distance_from_home: 0
  });

  const [loading, setLoading] = useState(false);
  const [fraudScenarios, setFraudScenarios] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    loadFraudScenarios();
  }, []);

  const loadFraudScenarios = async () => {
    try {
      const data = await api.getFraudScenarios();
      setFraudScenarios(data.scenarios || []);
    } catch (error) {
      console.error('Failed to load scenarios:', error);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await onPredict(formData);
    } catch (error) {
      console.error('Prediction error:', error);
      alert('Prediction failed: ' + (error.message || 'Server error'));
    } finally {
      setLoading(false);
    }
  };

  const loadScenario = (scenario) => {
    setFormData(scenario.data);
  };

  const updateField = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
      <h2 className="text-2xl font-bold mb-4 text-white flex items-center gap-2">
        <Shield className="w-6 h-6 text-blue-400" />
        Test Transaction
      </h2>

      {/* Quick Test Scenarios */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-white/70 mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          Quick Test Scenarios
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {fraudScenarios.map((scenario, index) => (
            <button
              key={index}
              onClick={() => loadScenario(scenario)}
              className={`p-3 rounded-lg border text-left transition-all hover:shadow-md ${
                scenario.expected === 'fraud'
                  ? 'border-red-500/30 bg-red-500/10 hover:bg-red-500/20'
                  : scenario.expected === 'medium_risk'
                  ? 'border-orange-500/30 bg-orange-500/10 hover:bg-orange-500/20'
                  : 'border-green-500/30 bg-green-500/10 hover:bg-green-500/20'
              }`}
            >
              <div className="font-semibold text-sm text-white">{scenario.name}</div>
              <div className="text-xs text-white/50 mt-1">{scenario.description}</div>
              <div className={`text-xs font-bold mt-2 ${
                scenario.expected === 'fraud' ? 'text-red-400' :
                scenario.expected === 'medium_risk' ? 'text-orange-400' :
                'text-green-400'
              }`}>
                Expected: {scenario.expected === 'fraud' ? '🚨 FRAUD' :
                          scenario.expected === 'medium_risk' ? '⚠️ MEDIUM' :
                          '✅ SAFE'}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Essential Fields */}
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Amount ($)</label>
            <input
              type="number"
              step="0.01"
              value={formData.transaction_amount}
              onChange={(e) => updateField('transaction_amount', parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-white/30 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg font-semibold"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-white/70 mb-1">Merchant</label>
            <input
              type="text"
              value={formData.merchant_name}
              onChange={(e) => updateField('merchant_name', e.target.value)}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-white/30 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Risk Indicators */}
        <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-300 mb-3 text-sm">Risk Indicators</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-white/50 mb-1">Distance (miles)</label>
              <input
                type="number"
                value={formData.distance_from_home}
                onChange={(e) => updateField('distance_from_home', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-white/30 focus:ring-2 focus:ring-blue-500"
                placeholder="0 = local"
              />
            </div>
            <div>
              <label className="block text-xs text-white/50 mb-1">Hour (0-23)</label>
              <input
                type="number"
                min="0"
                max="23"
                value={formData.transaction_hour}
                onChange={(e) => updateField('transaction_hour', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-white/30 focus:ring-2 focus:ring-blue-500"
                placeholder="14 = 2 PM"
              />
            </div>
          </div>

          <div className="flex items-center gap-6 mt-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_international}
                onChange={(e) => updateField('is_international', e.target.checked)}
                className="w-5 h-5 text-blue-500 rounded"
              />
              <span className="text-sm font-medium text-white/80">🌍 International</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_online}
                onChange={(e) => updateField('is_online', e.target.checked)}
                className="w-5 h-5 text-blue-500 rounded"
              />
              <span className="text-sm font-medium text-white/80">💻 Online</span>
            </label>
          </div>
        </div>

        {/* Advanced Options */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
        >
          {showAdvanced ? '▼ Hide' : '▶ Show'} Advanced Options
        </button>

        {showAdvanced && (
          <div className="bg-white/5 border border-white/10 p-4 rounded-lg space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-white/50 mb-1">Card Number (Last 4)</label>
                <input
                  type="text"
                  maxLength="4"
                  value={formData.card_number}
                  onChange={(e) => updateField('card_number', e.target.value)}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-white/50 mb-1">Card Type</label>
                <select
                  value={formData.card_type}
                  onChange={(e) => updateField('card_type', e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-white/20 rounded-md text-white text-sm focus:ring-2 focus:ring-blue-500"
                >
                  {options.card_types && options.card_types.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-white/50 mb-1">Category</label>
                <select
                  value={formData.merchant_category}
                  onChange={(e) => updateField('merchant_category', e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-white/20 rounded-md text-white text-sm focus:ring-2 focus:ring-blue-500"
                >
                  {options.merchant_categories && options.merchant_categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-white/50 mb-1">Location</label>
                <input
                  type="text"
                  value={formData.location_city}
                  onChange={(e) => updateField('location_city', e.target.value)}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white text-sm focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        )}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 disabled:text-blue-400 text-white py-3 px-4 rounded-lg transition-all font-semibold text-lg flex items-center justify-center gap-2 border border-blue-500/30"
        >
          {loading ? 'Analyzing...' : 'Analyze Transaction'}
          <Target className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

// ============================================================================
// Prediction Result Component
// ============================================================================

const PredictionResult = ({ result }) => {
  if (!result) return null;

  const fraudProb = Number.isFinite(result.fraud_probability) ? result.fraud_probability : 0;
  const riskScore = Number.isFinite(result.risk_score) ? result.risk_score : 0;
  const isFraud = Boolean(result.is_fraud);
  const confidence = result.confidence ?? 'UNKNOWN';

  const fraudPct = (fraudProb * 100) || 0;

  return (
    <div className={`rounded-xl border p-6 ${
      isFraud
        ? 'bg-red-500/10 border-red-500/30'
        : 'bg-green-500/10 border-green-500/30'
    }`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-white">Analysis Result</h2>
        {isFraud
          ? <AlertCircle className="w-10 h-10 text-red-400 animate-pulse" />
          : <CheckCircle className="w-10 h-10 text-green-400 animate-pulse" />
        }
      </div>

      {/* Main Status */}
      <div className={`p-6 rounded-lg mb-4 text-center border ${
        isFraud ? 'bg-red-500/20 border-red-500/30' : 'bg-green-500/20 border-green-500/30'
      }`}>
        <p className="text-sm text-white/60 mb-2">Transaction Status</p>
        <p className={`text-4xl font-bold ${isFraud ? 'text-red-400' : 'text-green-400'}`}>
          {isFraud ? '🚨 FRAUDULENT' : '✅ LEGITIMATE'}
        </p>
        <p className={`text-lg font-semibold mt-2 ${isFraud ? 'text-red-300' : 'text-green-300'}`}>
          {confidence} Risk Level
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white/5 border border-white/10 p-4 rounded-md">
          <p className="text-xs text-white/50 mb-1">Fraud Probability</p>
          <p className="text-2xl font-bold text-white">{fraudPct.toFixed(1)}%</p>
        </div>
        <div className="bg-white/5 border border-white/10 p-4 rounded-md">
          <p className="text-xs text-white/50 mb-1">Risk Score</p>
          <p className="text-2xl font-bold text-white">
            {Number.isFinite(riskScore) ? riskScore.toFixed(0) : '0'}/100
          </p>
        </div>
      </div>

      {/* Transaction Summary */}
      {result.transaction_summary && (
        <div className="bg-white/5 border border-white/10 p-4 rounded-md mb-4 text-sm">
          <p className="font-semibold text-white/80 mb-2">Transaction Details:</p>
          <div className="space-y-1 text-white/60">
            <p>💰 <span className="font-medium text-white/80">Amount:</span> ${result.transaction_summary.amount ?? '-'}</p>
            <p>🏪 <span className="font-medium text-white/80">Merchant:</span> {result.transaction_summary.merchant ?? '-'}</p>
            <p>📍 <span className="font-medium text-white/80">Location:</span> {result.transaction_summary.location ?? '-'}</p>
            <p>💳 <span className="font-medium text-white/80">Card:</span> {result.transaction_summary.card_type ?? '-'}</p>
            <p>🌐 <span className="font-medium text-white/80">Type:</span> {result.transaction_summary.is_online ? 'Online' : 'In-Person'}</p>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className="bg-white/5 border border-white/10 p-4 rounded-md">
        <div className="w-full bg-white/10 rounded-full h-6 mb-2">
          <div
            className={`h-6 rounded-full transition-all duration-1000 flex items-center justify-center text-white text-xs font-bold ${
              isFraud ? 'bg-red-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.max(fraudPct, 5)}%` }}
          >
            {fraudPct.toFixed(1)}%
          </div>
        </div>
        <p className="text-xs text-white/40 text-center">
          Detection Threshold: {((result.details?.threshold ?? 0.5) * 100).toFixed(1)}%
        </p>
      </div>
    </div>
  );
};

// ============================================================================
// Statistics Dashboard Component
// ============================================================================

const StatsDashboard = ({ stats }) => {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      <div className="bg-white/5 border border-white/10 p-4 rounded-lg hover:border-blue-500/30 transition-colors">
        <Database className="w-6 h-6 text-blue-400 mb-2" />
        <p className="text-3xl font-bold text-white">{stats.total_transactions}</p>
        <p className="text-sm text-white/50 font-medium">Total Tests</p>
      </div>

      <div className="bg-white/5 border border-white/10 p-4 rounded-lg hover:border-red-500/30 transition-colors">
        <AlertCircle className="w-6 h-6 text-red-400 mb-2" />
        <p className="text-3xl font-bold text-red-400">{stats.fraudulent_transactions}</p>
        <p className="text-sm text-white/50 font-medium">Detected Fraud</p>
      </div>

      <div className="bg-white/5 border border-white/10 p-4 rounded-lg hover:border-green-500/30 transition-colors">
        <CheckCircle className="w-6 h-6 text-green-400 mb-2" />
        <p className="text-3xl font-bold text-green-400">{stats.legitimate_transactions}</p>
        <p className="text-sm text-white/50 font-medium">Legitimate</p>
      </div>

      <div className="bg-white/5 border border-white/10 p-4 rounded-lg hover:border-purple-500/30 transition-colors">
        <TrendingUp className="w-6 h-6 text-purple-400 mb-2" />
        <p className="text-3xl font-bold text-purple-400">
          {(stats.fraud_rate * 100).toFixed(1)}%
        </p>
        <p className="text-sm text-white/50 font-medium">Fraud Rate</p>
      </div>
    </div>
  );
};

// ============================================================================
// Transaction History Component
// ============================================================================

const TransactionHistory = ({ transactions, onDelete, onRefresh }) => {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filteredTransactions = transactions
    .filter(t => {
      if (filter === 'fraud') return t.is_fraud;
      if (filter === 'legitimate') return !t.is_fraud;
      return true;
    })
    .filter(t =>
      t.merchant_name.toLowerCase().includes(search.toLowerCase()) ||
      t.card_number.includes(search)
    );

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-white">Test History</h2>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md transition-colors text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      <div className="flex gap-4 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-2.5 w-5 h-5 text-white/30" />
          <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-white/30 focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 bg-slate-800 border border-white/20 rounded-md text-white focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Tests</option>
          <option value="fraud">Fraud Only</option>
          <option value="legitimate">Legitimate Only</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase">ID</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase">Merchant</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase">Amount</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase">Result</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase">Confidence</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase">Tested By</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase">Date</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {filteredTransactions.map(t => (
              <tr key={t.id} className="hover:bg-white/5 transition-colors">
                <td className="px-4 py-3 text-sm font-mono text-white/60">#{t.id}</td>
                <td className="px-4 py-3 text-sm text-white/80">{t.merchant_name}</td>
                <td className="px-4 py-3 text-sm font-semibold text-white">${t.transaction_amount.toFixed(2)}</td>
                <td className="px-4 py-3">
                  <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                    t.is_fraud
                      ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                      : 'bg-green-500/20 text-green-300 border border-green-500/30'
                  }`}>
                    {t.is_fraud ? '🚨 FRAUD' : '✅ SAFE'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-white/60">
                  {(t.fraud_probability * 100).toFixed(1)}%
                </td>
                <td className="px-4 py-3 text-sm text-white/70 font-medium">
                  {t.created_by_username || 'Unknown'}
                </td>
                <td className="px-4 py-3 text-xs text-white/40">
                  {new Date(t.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => onDelete(t.id)}
                    className="text-red-400 hover:text-red-300 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredTransactions.length === 0 && (
        <p className="text-center text-white/30 py-8">No tests found</p>
      )}
    </div>
  );
};

// ============================================================================
// Main Dashboard Component
// ============================================================================

const Dashboard = () => {
  const { user, token } = useAuth();
  const [predictionResult, setPredictionResult] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [options, setOptions] = useState({
    card_types: [],
    merchant_categories: [],
    transaction_types: [],
    countries: []
  });
  const [activeTab, setActiveTab] = useState('predict');

  const loadData = async () => {
    try {
      const [txns, stats] = await Promise.all([
        api.getTransactions(token).catch(() => []),
        api.getStatistics(token).catch(() => ({
          total_transactions: 0,
          fraudulent_transactions: 0,
          legitimate_transactions: 0,
          fraud_rate: 0
        })),
      ]);
      setTransactions(txns || []);
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to load data:', err);
      setTransactions([]);
      setStatistics({
        total_transactions: 0,
        fraudulent_transactions: 0,
        legitimate_transactions: 0,
        fraud_rate: 0
      });
    }
  };

  const loadOptions = async () => {
    try {
      const opts = await api.getOptions();
      setOptions(opts);
    } catch (err) {
      console.error('Failed to load options:', err);
    }
  };

  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        await loadData();
        await loadOptions();
      } catch (err) {
        if (isMounted) console.error('Initial load failed:', err);
      }
    })();
    return () => { isMounted = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handlePredict = async (formData) => {
    const result = await api.predict(formData, token);
    if (result && result.fraud_probability !== undefined) {
      setPredictionResult(result);
      loadData();
    } else {
      alert('Invalid response from server. Please try again.');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this test?')) {
      try {
        await api.deleteTransaction(id, token);
        loadData();
      } catch (error) {
        console.error('Delete failed:', error);
        alert('Failed to delete');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
      <div className="max-w-7xl mx-auto p-6">

        {/* Header */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-6 border-t-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-12 h-12 text-blue-400" />
              <div>
                <h1 className="text-3xl font-bold text-white">
                  Fraud Detection System
                </h1>
                <p className="text-sm text-blue-300">
                  Welcome, {user?.username}! | KNN Algorithm 🎯
                </p>
              </div>
            </div>
            <Activity className="w-10 h-10 text-green-400 animate-pulse" />
          </div>
        </div>

        {/* Stats */}
        {statistics && <StatsDashboard stats={statistics} />}

        {/* Tabs */}
        <div className="bg-white/5 border border-white/10 rounded-xl mb-6 p-1">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('predict')}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all ${
                activeTab === 'predict'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-white/60 hover:bg-white/5 hover:text-white'
              }`}
            >
              🎯 Test Transaction
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all ${
                activeTab === 'history'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-white/60 hover:bg-white/5 hover:text-white'
              }`}
            >
              📊 Test History
            </button>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'predict' ? (
          <div className="grid grid-cols-2 gap-6">
            <SimplifiedTransactionForm onPredict={handlePredict} options={options} />
            {predictionResult && <PredictionResult result={predictionResult} />}
          </div>
        ) : (
          <TransactionHistory
            transactions={transactions}
            onDelete={handleDelete}
            onRefresh={loadData}
          />
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  );
};

// ============================================================================
// Admin Page Wrapper
// ============================================================================

const AdminPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
      <AdminDashboard />
    </div>
  );
};

// ============================================================================
// App Routes
// ============================================================================

const AppContent = () => {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/"        element={<HomePage />} />
        <Route path="/about"   element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/login"   element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
        } />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        {/* ── NEW: Visualization route ── */}
        <Route
          path="/visualization"
          element={
            <ProtectedRoute>
              <VisualizationPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute adminOnly>
              <AdminPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
};

// ============================================================================
// Root App with Providers
// ============================================================================

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;