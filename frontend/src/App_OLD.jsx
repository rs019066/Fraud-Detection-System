import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, TrendingUp, Shield, Activity, Database, Trash2, Search, Zap, Target } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const api = {
  predict: async (transaction) => {
    const response = await fetch(`${API_URL}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(transaction),
    });
    if (!response.ok) throw new Error(`Predict failed: ${response.status} ${response.statusText}`);
    return response.json();
  },
  getTransactions: async () => {
    const response = await fetch(`${API_URL}/api/transactions`);
    if (!response.ok) throw new Error(`Get transactions failed: ${response.status}`);
    return response.json();
  },
  getStatistics: async () => {
    const response = await fetch(`${API_URL}/api/statistics`);
    if (!response.ok) throw new Error(`Get statistics failed: ${response.status}`);
    return response.json();
  },
  deleteTransaction: async (id) => {
    const response = await fetch(`${API_URL}/api/transactions/${id}`, { method: 'DELETE' });
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

// Simplified Transaction Form with Presets
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
      const result = await api.predict(formData);
      if (result && result.fraud_probability !== undefined) {
        onPredict(result);
      } else {
        alert('Invalid response from server. Please try again.');
      }
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
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800 flex items-center gap-2">
        <Shield className="w-6 h-6 text-blue-600" />
        Test Transaction
      </h2>

      {/* Quick Test Scenarios */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-500" />
          Quick Test Scenarios
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {fraudScenarios.map((scenario, index) => (
            <button
              key={index}
              onClick={() => loadScenario(scenario)}
              className={`p-3 rounded-lg border-2 text-left transition-all hover:shadow-md ${
                scenario.expected === 'fraud' 
                  ? 'border-red-300 bg-red-50 hover:bg-red-100' 
                  : scenario.expected === 'medium_risk'
                  ? 'border-orange-300 bg-orange-50 hover:bg-orange-100'
                  : 'border-green-300 bg-green-50 hover:bg-green-100'
              }`}
            >
              <div className="font-semibold text-sm">{scenario.name}</div>
              <div className="text-xs text-gray-600 mt-1">{scenario.description}</div>
              <div className={`text-xs font-bold mt-2 ${
                scenario.expected === 'fraud' ? 'text-red-600' : 
                scenario.expected === 'medium_risk' ? 'text-orange-600' :
                'text-green-600'
              }`}>
                Expected: {scenario.expected === 'fraud' ? '🚨 FRAUD' : 
                          scenario.expected === 'medium_risk' ? '⚠️ MEDIUM' :
                          '✅ SAFE'}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Essential Fields Only */}
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Amount ($)</label>
            <input
              type="number"
              step="0.01"
              value={formData.transaction_amount}
              onChange={(e) => updateField('transaction_amount', parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 text-lg font-semibold"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Merchant</label>
            <input
              type="text"
              value={formData.merchant_name}
              onChange={(e) => updateField('merchant_name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Key Risk Indicators */}
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="font-semibold text-purple-900 mb-3 text-sm">Risk Indicators</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-600 mb-1">Distance (miles)</label>
              <input
                type="number"
                value={formData.distance_from_home}
                onChange={(e) => updateField('distance_from_home', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
                placeholder="0 = local"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">Hour (0-23)</label>
              <input
                type="number"
                min="0"
                max="23"
                value={formData.transaction_hour}
                onChange={(e) => updateField('transaction_hour', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
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
                className="w-5 h-5 text-purple-600"
              />
              <span className="text-sm font-medium text-gray-700">🌍 International</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_online}
                onChange={(e) => updateField('is_online', e.target.checked)}
                className="w-5 h-5 text-purple-600"
              />
              <span className="text-sm font-medium text-gray-700">💻 Online</span>
            </label>
          </div>
        </div>

        {/* Advanced Options (Collapsible) */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          {showAdvanced ? '▼ Hide' : '▶ Show'} Advanced Options
        </button>

        {showAdvanced && (
          <div className="bg-gray-50 p-4 rounded-lg space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Card Number (Last 4)</label>
                <input
                  type="text"
                  maxLength="4"
                  value={formData.card_number}
                  onChange={(e) => updateField('card_number', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Card Type</label>
                <select
                  value={formData.card_type}
                  onChange={(e) => updateField('card_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  {options.card_types.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Category</label>
                <select
                  value={formData.merchant_category}
                  onChange={(e) => updateField('merchant_category', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  {options.merchant_categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Location</label>
                <input
                  type="text"
                  value={formData.location_city}
                  onChange={(e) => updateField('location_city', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 transition-all font-semibold text-lg shadow-lg flex items-center justify-center gap-2"
        >
          {loading ? 'Analyzing...' : 'Analyze Transaction'}
          <Target className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

const PredictionResult = ({ result }) => {
  if (!result) return null;

  // Safely extract values with defaults
  const fraudProb = Number.isFinite(result.fraud_probability) ? result.fraud_probability : 0;
  const riskScore = Number.isFinite(result.risk_score) ? result.risk_score : 0;
  const isFraud = Boolean(result.is_fraud);
  const confidence = result.confidence ?? 'UNKNOWN';

  const riskColor = isFraud ? 'text-red-600' : 'text-green-600';
  const bgColor = isFraud ? 'bg-red-50' : 'bg-green-50';
  const borderColor = isFraud ? 'border-red-300' : 'border-green-300';
  const Icon = isFraud ? AlertCircle : CheckCircle;

  const fraudPct = (fraudProb * 100) || 0;

  return (
    <div className={`${bgColor} rounded-lg shadow-lg p-6 border-2 ${borderColor} animate-fadeIn`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Analysis Result</h2>
        <Icon className={`w-10 h-10 ${riskColor} animate-pulse`} />
      </div>

      {/* Main Status */}
      <div className={`${isFraud ? 'bg-red-100' : 'bg-green-100'} p-6 rounded-lg mb-4 text-center`}>
        <p className="text-sm text-gray-600 mb-2">Transaction Status</p>
        <p className={`text-4xl font-bold ${riskColor}`}>
          {isFraud ? '🚨 FRAUDULENT' : '✅ LEGITIMATE'}
        </p>
        <p className={`text-lg font-semibold mt-2 ${riskColor}`}>
          {confidence} Risk Level
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white p-4 rounded-md shadow-sm">
          <p className="text-xs text-gray-600 mb-1">Fraud Probability</p>
          <p className="text-2xl font-bold text-gray-800">
            {fraudPct.toFixed(1)}%
          </p>
        </div>

        <div className="bg-white p-4 rounded-md shadow-sm">
          <p className="text-xs text-gray-600 mb-1">Risk Score</p>
          <p className="text-2xl font-bold text-gray-800">
            {Number.isFinite(riskScore) ? riskScore.toFixed(0) : '0'}/100
          </p>
        </div>
      </div>

      {/* Transaction Summary */}
      {result.transaction_summary && (
        <div className="bg-white p-4 rounded-md mb-4 text-sm">
          <p className="font-semibold text-gray-700 mb-2">Transaction Details:</p>
          <div className="space-y-1 text-gray-600">
            <p>💰 <span className="font-medium">Amount:</span> ${result.transaction_summary.amount ?? '-'}</p>
            <p>🏪 <span className="font-medium">Merchant:</span> {result.transaction_summary.merchant ?? '-'}</p>
            <p>📍 <span className="font-medium">Location:</span> {result.transaction_summary.location ?? '-'}</p>
            <p>💳 <span className="font-medium">Card:</span> {result.transaction_summary.card_type ?? '-'}</p>
            <p>🌐 <span className="font-medium">Type:</span> {result.transaction_summary.is_online ? 'Online' : 'In-Person'}</p>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className="bg-white p-4 rounded-md">
        <div className="w-full bg-gray-200 rounded-full h-6 mb-2">
          <div
            className={`h-6 rounded-full transition-all duration-1000 flex items-center justify-center text-white text-xs font-bold ${
              isFraud ? 'bg-red-600' : 'bg-green-600'
            }`}
            style={{ width: `${Math.max(fraudPct, 5)}%` }}
          >
            {fraudPct.toFixed(1)}%
          </div>
        </div>
        <p className="text-xs text-gray-600 text-center">
          Detection Threshold: {((result.details?.threshold ?? 0.5) * 100).toFixed(1)}%
        </p>
      </div>
    </div>
  );
};

const StatsDashboard = ({ stats }) => {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200 shadow-sm">
        <Database className="w-6 h-6 text-blue-600 mb-2" />
        <p className="text-3xl font-bold text-blue-900">{stats.total_transactions}</p>
        <p className="text-sm text-blue-700 font-medium">Total Tests</p>
      </div>

      <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200 shadow-sm">
        <AlertCircle className="w-6 h-6 text-red-600 mb-2" />
        <p className="text-3xl font-bold text-red-900">{stats.fraudulent_transactions}</p>
        <p className="text-sm text-red-700 font-medium">Detected Fraud</p>
      </div>

      <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200 shadow-sm">
        <CheckCircle className="w-6 h-6 text-green-600 mb-2" />
        <p className="text-3xl font-bold text-green-900">{stats.legitimate_transactions}</p>
        <p className="text-sm text-green-700 font-medium">Legitimate</p>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200 shadow-sm">
        <TrendingUp className="w-6 h-6 text-purple-600 mb-2" />
        <p className="text-3xl font-bold text-purple-900">
          {(stats.fraud_rate * 100).toFixed(1)}%
        </p>
        <p className="text-sm text-purple-700 font-medium">Fraud Rate</p>
      </div>
    </div>
  );
};

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
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Test History</h2>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      <div className="flex gap-4 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Tests</option>
          <option value="fraud">Fraud Only</option>
          <option value="legitimate">Legitimate Only</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Merchant</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Result</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredTransactions.map(t => (
              <tr key={t.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-mono">#{t.id}</td>
                <td className="px-4 py-3 text-sm">{t.merchant_name}</td>
                <td className="px-4 py-3 text-sm font-semibold">${t.transaction_amount.toFixed(2)}</td>
                <td className="px-4 py-3">
                  <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                    t.is_fraud 
                      ? 'bg-red-100 text-red-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {t.is_fraud ? '🚨 FRAUD' : '✅ SAFE'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  {(t.fraud_probability * 100).toFixed(1)}%
                </td>
                <td className="px-4 py-3 text-xs text-gray-500">
                  {new Date(t.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => onDelete(t.id)}
                    className="text-red-600 hover:text-red-800 transition-colors"
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
        <p className="text-center text-gray-500 py-8">No tests found</p>
      )}
    </div>
  );
};

const FraudDetectionApp = () => {
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

  

  async function loadData() {
    try {
      const [txns, stats] = await Promise.all([
        api.getTransactions().catch(() => []),
        api.getStatistics().catch(() => ({
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
      // Set default values on error
      setTransactions([]);
      setStatistics({
        total_transactions: 0,
        fraudulent_transactions: 0,
        legitimate_transactions: 0,
        fraud_rate: 0
      });
    }
  }

  async function loadOptions() {
    try {
      const opts = await api.getOptions();
      setOptions(opts);
    } catch (err) {
      console.error('Failed to load options:', err);
    }
  }

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
  }, []);

  const handlePredict = (result) => {
    setPredictionResult(result);
    loadData();
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this test?')) {
      try {
        await api.deleteTransaction(id);
        loadData();
      } catch (error) {
        console.error('Delete failed:', error);
        alert('Failed to delete');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-xl p-6 mb-6 border-t-4 border-blue-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-12 h-12 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-800">
                  Fraud Detection System
                </h1>
                <p className="text-sm text-gray-600">
                  KNN Algorithm - Improved Sensitivity 🎯
                </p>
              </div>
            </div>
            <Activity className="w-10 h-10 text-green-500 animate-pulse" />
          </div>
        </div>

        {/* Stats */}
        {statistics && <StatsDashboard stats={statistics} />}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6 p-1">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('predict')}
              className={`flex-1 py-3 px-4 rounded-md font-semibold transition-all ${
                activeTab === 'predict'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              🎯 Test Transaction
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex-1 py-3 px-4 rounded-md font-semibold transition-all ${
                activeTab === 'history'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-gray-100'
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

export default FraudDetectionApp;