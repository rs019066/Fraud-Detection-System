/**
 * Admin Dashboard Component
 * ==========================
 * Dark blue theme consistent with Home page
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  Users, UserPlus, Shield, User, Activity, BarChart3,
  AlertCircle, CheckCircle, History, CreditCard, TrendingUp,
  UserCheck, MessageSquare, Send, Clock, CheckCircle2, RefreshCw
} from 'lucide-react';

const API_URL = 'http://localhost:8000';

const AdminDashboard = () => {
  const { fetchWithAuth, user, isAdmin } = useAuth();

  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers]           = useState([]);
  const [stats, setStats]           = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [messages, setMessages]     = useState([]);
  const [loading, setLoading]       = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const [error, setError]           = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newUser, setNewUser]       = useState({ username: '', email: '', password: '', role: 'analyst' });
  const [replies, setReplies]       = useState({});
  const [sendingReply, setSendingReply] = useState(null);

  if (!isAdmin()) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="bg-white/5 border border-white/10 rounded-xl p-8 max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Access Denied</h2>
          <p className="text-white/50">This page is only accessible to administrators.</p>
        </div>
      </div>
    );
  }

  useEffect(() => {
    loadDashboardData();
    loadMessages();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const usersRes = await fetchWithAuth('/auth/admin/users');
      if (usersRes.ok) setUsers(await usersRes.json());
      else if (usersRes.status === 403) setError('Access denied: Admin privileges required');

      const statsRes = await fetchWithAuth('/api/statistics');
      if (statsRes.ok) setStats(await statsRes.json());

      const txRes = await fetchWithAuth('/api/transactions?limit=20');
      if (txRes.ok) setTransactions(await txRes.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async () => {
    setLoadingMsgs(true);
    try {
      const res = await fetchWithAuth('/api/messages');
      if (res.ok) setMessages(await res.json());
    } catch (err) {
      console.error('Failed to load messages:', err);
    } finally {
      setLoadingMsgs(false);
    }
  };

  const sendReply = async (msgId) => {
    const replyText = replies[msgId]?.trim();
    if (!replyText) return;
    setSendingReply(msgId);
    try {
      const res = await fetchWithAuth(`/api/messages/${msgId}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reply: replyText }),
      });
      if (res.ok) {
        const updated = await res.json();
        setMessages(prev => prev.map(m => m.id === msgId ? updated : m));
        setReplies(prev => ({ ...prev, [msgId]: '' }));
      } else {
        setError('Failed to send reply');
      }
    } catch (err) {
      setError('Failed to send reply');
    } finally {
      setSendingReply(null);
    }
  };

  const markAsRead = async (msgId) => {
    try {
      const res = await fetchWithAuth(`/api/messages/${msgId}/read`, { method: 'PATCH' });
      if (res.ok) {
        const updated = await res.json();
        setMessages(prev => prev.map(m => m.id === msgId ? updated : m));
      }
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  const toggleUserStatus = async (userId) => {
    const u = users.find(u => u.id === userId);
    if (!u) return;
    try {
      const res = await fetchWithAuth(`/auth/admin/users/${userId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !u.is_active }),
      });
      if (res.ok) setUsers(prev => prev.map(x => x.id === userId ? { ...x, is_active: !u.is_active } : x));
      else setError('Failed to update user status');
    } catch { setError('Failed to update user status'); }
  };

  const changeUserRole = async (userId, newRole) => {
    try {
      const res = await fetchWithAuth(`/auth/admin/users/${userId}/role`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole }),
      });
      if (res.ok) setUsers(prev => prev.map(x => x.id === userId ? { ...x, role: newRole } : x));
      else setError('Failed to update role');
    } catch { setError('Failed to update role'); }
  };

  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      const res = await fetchWithAuth(`/auth/admin/users/${userId}`, { method: 'DELETE' });
      if (res.ok) setUsers(prev => prev.filter(u => u.id !== userId));
      else setError('Failed to delete user');
    } catch { setError('Failed to delete user'); }
  };

  const createUser = async () => {
    if (!newUser.username || !newUser.email || !newUser.password) {
      setError('All fields are required'); return;
    }
    if (newUser.password.length < 6) {
      setError('Password must be at least 6 characters'); return;
    }
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser),
      });
      if (res.ok) {
        setNewUser({ username: '', email: '', password: '', role: 'analyst' });
        setShowCreateForm(false);
        setError('');
        await loadDashboardData();
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to create user');
      }
    } catch { setError('Failed to create user'); }
  };

  const statusStyle = s => ({
    pending: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30',
    read:    'bg-blue-500/20 text-blue-300 border border-blue-500/30',
    replied: 'bg-green-500/20 text-green-300 border border-green-500/30',
  }[s] ?? 'bg-white/10 text-white/50');

  const unreadCount = messages.filter(m => m.status === 'pending').length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4" />
          <p className="text-white/50">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const TabBtn = ({ id, label, icon: Icon, badge }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap ${
        activeTab === id
          ? 'border-blue-400 text-blue-300 bg-white/5'
          : 'border-transparent text-white/50 hover:text-white hover:bg-white/5'
      }`}
    >
      <Icon className="w-4 h-4" />
      {label}
      {badge > 0 && (
        <span className="ml-1 px-1.5 py-0.5 bg-red-500 text-white text-xs font-bold rounded-full leading-none">
          {badge}
        </span>
      )}
    </button>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="mb-8">
          <div className="inline-block mb-3 px-4 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs font-semibold uppercase tracking-widest">
            Admin Panel
          </div>
          <h1 className="text-3xl font-extrabold text-white mb-1">Admin Dashboard</h1>
          <p className="text-white/40">Manage users, review transactions and reply to contact messages.</p>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-red-300">{error}</span>
            <button onClick={() => setError('')} className="ml-auto text-red-400/60 hover:text-red-300">✕</button>
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-3 gap-6 mb-8">
            {[
              { label: 'Total Transactions', value: stats.total_transactions ?? 0,                        Icon: Activity,    color: 'text-blue-400' },
              { label: 'Fraud Detected',     value: stats.fraudulent_transactions ?? 0,                    Icon: AlertCircle, color: 'text-red-400' },
              { label: 'Fraud Rate',         value: `${((stats.fraud_rate ?? 0) * 100).toFixed(1)}%`,      Icon: BarChart3,   color: 'text-orange-400' },
            ].map(({ label, value, Icon, color }) => (
              <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-6 flex items-center justify-between hover:border-white/20 transition-colors">
                <div>
                  <p className="text-sm font-medium text-white/40">{label}</p>
                  <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
                </div>
                <Icon className={`h-10 w-10 ${color} opacity-60`} />
              </div>
            ))}
          </div>
        )}

        {/* Tab bar */}
        <div className="bg-white/5 border border-white/10 rounded-t-xl flex overflow-x-auto border-b border-white/10">
          <TabBtn id="users"    label="User Management"  icon={Users}         />
          <TabBtn id="history"  label="Test History"     icon={History}       />
          <TabBtn id="messages" label="Contact Messages" icon={MessageSquare} badge={unreadCount} />
        </div>

        {/* ════════════════════════════════════════════
            TAB: User Management
        ════════════════════════════════════════════ */}
        {activeTab === 'users' && (
          <div className="bg-white/5 border border-white/10 border-t-0 rounded-b-xl">
            <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-white/40" />
                <span className="text-lg font-semibold text-white">All Users</span>
              </div>
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors text-sm font-semibold"
              >
                <UserPlus className="w-4 h-4" />
                Create User
              </button>
            </div>

            {showCreateForm && (
              <div className="px-6 py-4 bg-blue-500/10 border-b border-blue-500/20">
                <h3 className="text-sm font-semibold text-blue-300 mb-3">Create New User</h3>
                <div className="grid grid-cols-5 gap-3">
                  {[
                    { placeholder: 'Username', key: 'username', type: 'text' },
                    { placeholder: 'Email', key: 'email', type: 'email' },
                    { placeholder: 'Password (min 6)', key: 'password', type: 'password' },
                  ].map(f => (
                    <input
                      key={f.key} type={f.type} placeholder={f.placeholder}
                      value={newUser[f.key]}
                      onChange={e => setNewUser({ ...newUser, [f.key]: e.target.value })}
                      className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/30 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  ))}
                  <select
                    value={newUser.role}
                    onChange={e => setNewUser({ ...newUser, role: e.target.value })}
                    className="px-3 py-2 bg-slate-800 border border-white/20 rounded-lg text-white text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="analyst">Analyst</option>
                    <option value="admin">Admin</option>
                  </select>
                  <button onClick={createUser} className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg text-sm font-semibold transition-colors">
                    Create
                  </button>
                </div>
              </div>
            )}

            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    {['User', 'Email', 'Role', 'Status', 'Created', 'Actions'].map(h => (
                      <th key={h} className="px-6 py-3 text-left text-xs font-medium text-white/30 uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {users.map(u => (
                    <tr key={u.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-full ${u.role === 'admin' ? 'bg-orange-500/20' : 'bg-blue-500/20'}`}>
                            {u.role === 'admin'
                              ? <Shield className="h-4 w-4 text-orange-400" />
                              : <User className="h-4 w-4 text-blue-400" />
                            }
                          </div>
                          <span className="text-sm font-medium text-white">{u.username}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white/50">{u.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <select
                          value={u.role}
                          onChange={e => changeUserRole(u.id, e.target.value)}
                          disabled={u.id === user?.id}
                          className="text-sm rounded-md px-2 py-1 bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-40 disabled:cursor-not-allowed"
                        >
                          <option value="analyst">Analyst</option>
                          <option value="admin">Admin</option>
                        </select>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => toggleUserStatus(u.id)}
                          disabled={u.id === user?.id}
                          className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold transition-opacity ${
                            u.is_active
                              ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                              : 'bg-red-500/20 text-red-300 border border-red-500/30'
                          } ${u.id === user?.id ? 'opacity-40 cursor-not-allowed' : 'hover:opacity-75'}`}
                        >
                          {u.is_active
                            ? <><CheckCircle className="w-3 h-3" /> Active</>
                            : <><AlertCircle className="w-3 h-3" /> Disabled</>
                          }
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white/30">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => deleteUser(u.id)}
                          disabled={u.id === user?.id}
                          className="text-red-400 hover:text-red-300 text-sm font-medium disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════
            TAB: Test History
        ════════════════════════════════════════════ */}
        {activeTab === 'history' && (
          <div className="bg-white/5 border border-white/10 border-t-0 rounded-b-xl overflow-x-auto">
            {transactions.length === 0 ? (
              <div className="py-16 text-center">
                <CreditCard className="h-12 w-12 text-white/20 mx-auto mb-3" />
                <p className="text-white/30">No transactions yet</p>
              </div>
            ) : (
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    {['ID','Card','Amount','Merchant','Location','Result','Risk','Tested By','Date'].map(h => (
                      <th key={h} className="px-5 py-3 text-left text-xs font-medium text-white/30 uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {transactions.map(tx => (
                    <tr key={tx.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-5 py-4 text-sm font-medium text-white">#{tx.id}</td>
                      <td className="px-5 py-4 text-sm text-white/50">
                        <div className="flex items-center gap-1">
                          <CreditCard className="h-4 w-4 text-white/20" />
                          {tx.card_type} ****{tx.card_number}
                        </div>
                      </td>
                      <td className="px-5 py-4 text-sm font-semibold text-white">${tx.transaction_amount.toFixed(2)}</td>
                      <td className="px-5 py-4 text-sm text-white/50">
                        <div className="max-w-xs truncate">{tx.merchant_name}</div>
                        <div className="text-xs text-white/30">{tx.merchant_category}</div>
                      </td>
                      <td className="px-5 py-4 text-sm text-white/50">{tx.location_city}, {tx.location_country}</td>
                      <td className="px-5 py-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${
                          tx.is_fraud
                            ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                            : 'bg-green-500/20 text-green-300 border border-green-500/30'
                        }`}>
                          {tx.is_fraud
                            ? <><AlertCircle className="w-3 h-3" />FRAUD</>
                            : <><CheckCircle className="w-3 h-3" />SAFE</>
                          }
                        </span>
                      </td>
                      <td className="px-5 py-4 text-sm">
                        <div className="flex items-center gap-1">
                          <TrendingUp className={`h-4 w-4 ${tx.risk_score >= 70 ? 'text-red-400' : tx.risk_score >= 40 ? 'text-orange-400' : 'text-green-400'}`} />
                          <span className="font-medium text-white">{tx.risk_score?.toFixed(1)}</span>
                          <span className="text-white/30 text-xs">({(tx.fraud_probability * 100).toFixed(1)}%)</span>
                        </div>
                      </td>
                      <td className="px-5 py-4 text-sm">
                        <div className="flex items-center gap-1">
                          <UserCheck className="h-4 w-4 text-white/20" />
                          <span className="text-white/70 font-medium">{tx.created_by_username || 'Unknown'}</span>
                        </div>
                      </td>
                      <td className="px-5 py-4 text-xs text-white/30">{new Date(tx.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* ════════════════════════════════════════════
            TAB: Contact Messages
        ════════════════════════════════════════════ */}
        {activeTab === 'messages' && (
          <div className="bg-white/5 border border-white/10 border-t-0 rounded-b-xl">
            <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-white/40" />
                <span className="text-lg font-semibold text-white">Contact Messages</span>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 bg-red-500/20 text-red-300 border border-red-500/30 text-xs font-bold rounded-full">
                    {unreadCount} new
                  </span>
                )}
              </div>
              <button
                onClick={loadMessages}
                className="flex items-center gap-2 px-3 py-2 border border-white/20 rounded-lg text-sm text-white/60 hover:bg-white/10 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            </div>

            {loadingMsgs ? (
              <div className="py-16 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto mb-3" />
                <p className="text-white/30 text-sm">Loading messages...</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="py-16 text-center">
                <MessageSquare className="h-12 w-12 text-white/20 mx-auto mb-3" />
                <p className="text-white/30">No messages yet</p>
                <p className="text-white/20 text-sm mt-1">Messages sent via the Contact page will appear here.</p>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {messages.map(msg => (
                  <div key={msg.id} className={`p-6 ${msg.status === 'pending' ? 'bg-yellow-500/5' : ''}`}>

                    {/* Message header */}
                    <div className="flex items-start justify-between gap-4 mb-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 flex-wrap mb-2">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-300 font-bold text-sm uppercase flex-shrink-0">
                              {(msg.username || msg.name || '?')[0]}
                            </div>
                            <div>
                              <span className="text-sm font-semibold text-white">
                                {msg.username || msg.name || 'Guest'}
                              </span>
                              {msg.email && (
                                <span className="text-xs text-white/30 ml-2">{msg.email}</span>
                              )}
                            </div>
                          </div>

                          <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs font-semibold rounded-md uppercase tracking-wide">
                            {msg.subject}
                          </span>

                          <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${statusStyle(msg.status)}`}>
                            {msg.status === 'pending' ? '⏳ Pending' : msg.status === 'read' ? '👁 Read' : '✅ Replied'}
                          </span>
                        </div>

                        <p className="text-white/70 text-sm leading-relaxed">{msg.message}</p>

                        <div className="flex items-center gap-1 mt-2 text-white/25 text-xs">
                          <Clock className="w-3 h-3" />
                          {new Date(msg.created_at).toLocaleString()}
                          {msg.status === 'pending' && (
                            <button
                              onClick={() => markAsRead(msg.id)}
                              className="ml-3 text-blue-400 hover:text-blue-300 font-medium transition-colors"
                            >
                              Mark as read
                            </button>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Existing reply */}
                    {msg.reply && (
                      <div className="mb-4 ml-4 pl-4 border-l-2 border-green-500/40 bg-green-500/10 rounded-r-lg py-3 pr-4">
                        <div className="flex items-center gap-2 mb-1">
                          <CheckCircle2 className="w-4 h-4 text-green-400" />
                          <span className="text-xs font-semibold text-green-400">Your Reply</span>
                          {msg.replied_at && (
                            <span className="text-xs text-white/25">· {new Date(msg.replied_at).toLocaleString()}</span>
                          )}
                        </div>
                        <p className="text-white/60 text-sm leading-relaxed">{msg.reply}</p>
                      </div>
                    )}

                    {/* Reply input */}
                    <div className="mt-3 flex gap-3">
                      <textarea
                        rows={2}
                        value={replies[msg.id] || ''}
                        onChange={e => setReplies(prev => ({ ...prev, [msg.id]: e.target.value }))}
                        placeholder={msg.reply ? 'Update your reply...' : 'Write a reply to this message...'}
                        className="flex-1 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/30 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                      />
                      <button
                        onClick={() => sendReply(msg.id)}
                        disabled={!replies[msg.id]?.trim() || sendingReply === msg.id}
                        className="self-end px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-white/10 disabled:text-white/20 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg transition-colors flex items-center gap-2"
                      >
                        <Send className="w-4 h-4" />
                        {sendingReply === msg.id ? 'Sending...' : msg.reply ? 'Update' : 'Reply'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
};

export default AdminDashboard;