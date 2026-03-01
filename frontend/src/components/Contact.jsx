import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Github, Code2, BookOpen, Send, MessageSquare, Clock, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const API_URL = 'http://localhost:8000';

export default function Contact() {
  const { user, token } = useAuth();

  const [form, setForm]               = useState({ name: '', email: '', subject: '', message: '' });
  const [loading, setLoading]         = useState(false);
  const [sent, setSent]               = useState(false);
  const [error, setError]             = useState('');
  const [myMessages, setMyMessages]   = useState([]);
  const [loadingMsgs, setLoadingMsgs] = useState(false);

  useEffect(() => {
    if (user) {
      setForm(f => ({ ...f, name: user.username }));
      loadMyMessages();
    }
  }, [user]);

  const loadMyMessages = async () => {
    if (!token) return;
    setLoadingMsgs(true);
    try {
      const res = await fetch(`${API_URL}/api/messages/my`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setMyMessages(await res.json());
    } catch (err) {
      console.error('Failed to load messages:', err);
    } finally {
      setLoadingMsgs(false);
    }
  };

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_URL}/api/messages`, {
        method: 'POST',
        headers,
        body: JSON.stringify(form),
      });

      if (res.ok) {
        setSent(true);
        setForm({ name: user?.username || '', email: '', subject: '', message: '' });
        if (user) loadMyMessages();
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || 'Failed to send. Please try again.');
      }
    } catch {
      // Backend not running — optimistic UI for demo
      setSent(true);
    } finally {
      setLoading(false);
    }
  }

  const statusStyle = s => ({
    pending: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/25',
    read:    'text-blue-400 bg-blue-400/10 border-blue-400/25',
    replied: 'text-green-400 bg-green-400/10 border-green-400/25',
  }[s] ?? 'text-white/40 bg-white/5 border-white/10');

  const statusLabel = s => ({ pending: '⏳ Pending', read: '👁 Read', replied: '✅ Replied' }[s] ?? s);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white">

      {/* Hero */}
      <section className="max-w-2xl mx-auto px-6 py-16 text-center">
        <div className="inline-block mb-4 px-4 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs font-semibold uppercase tracking-widest">
          Get in Touch
        </div>
        <h1 className="text-4xl font-extrabold mb-4">
          Have a <span className="text-blue-400">Question?</span>
        </h1>
        <p className="text-white/55 text-base leading-relaxed">
          Curious about the project, found a bug, or want to connect?{' '}
          {user
            ? <span className="text-blue-300">You're logged in — your replies will appear below the form.</span>
            : 'Drop a message below.'}
        </p>
      </section>

      {/* Layout */}
      <div className="max-w-5xl mx-auto px-6 pb-20 grid grid-cols-5 gap-8 items-start">

        {/* Info sidebar */}
        <div className="col-span-2 space-y-4">
          {[
            { icon: <BookOpen className="w-5 h-5 text-blue-400" />, title: 'Project',  text: 'Academic ML project demonstrating KNN-based fraud detection.' },
            { icon: <Github   className="w-5 h-5 text-blue-400" />, title: 'GitHub',           text: 'Source code available on GitHub for review and feedback.' },
            { icon: <Mail     className="w-5 h-5 text-blue-400" />, title: 'Email',            text: 'test@example.com' },
            { icon: <Code2    className="w-5 h-5 text-blue-400" />, title: 'Tech Stack',       text: 'Python · FASTApi · React · SQLite' },
          ].map(item => (
            <div key={item.title} className="bg-white/5 border border-white/10 rounded-xl p-4 hover:border-blue-500/30 transition-all">
              <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-3">
                {item.icon}
              </div>
              <h3 className="font-bold text-sm mb-1">{item.title}</h3>
              <p className="text-white/45 text-xs leading-relaxed">{item.text}</p>
            </div>
          ))}
        </div>

        {/* Right column: form + history */}
        <div className="col-span-3 space-y-5">

          {/* ── Contact Form ── */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-7 relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-t-xl" />

            {sent ? (
              <div className="text-center py-8">
                <div className="text-5xl mb-4">✅</div>
                <h3 className="text-xl font-extrabold mb-2">Message Sent!</h3>
                <p className="text-white/45 text-sm mb-5">
                  Thanks for reaching out. I'll get back to you as soon as possible.
                </p>
                <button
                  onClick={() => setSent(false)}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition-colors"
                >
                  Send Another
                </button>
              </div>
            ) : (
              <>
                <h2 className="text-lg font-extrabold mb-1">Send a Message</h2>
                <p className="text-white/40 text-sm mb-5">Fill out the form and I'll respond as soon as I can.</p>

                {error && (
                  <div className="mb-4 px-4 py-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300 text-sm">
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-white/50 uppercase tracking-widest mb-1.5 font-semibold">Name</label>
                      <input
                        name="name" value={form.name} onChange={handleChange}
                        required readOnly={!!user}
                        placeholder="Your name"
                        className={`w-full px-3 py-2.5 rounded-lg border text-white text-sm placeholder-white/25 focus:outline-none focus:border-blue-500/60 transition-colors ${
                          user ? 'bg-white/3 border-white/5 opacity-60 cursor-not-allowed' : 'bg-white/5 border-white/10'
                        }`}
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-white/50 uppercase tracking-widest mb-1.5 font-semibold">
                        Email {user && <span className="normal-case text-white/25">(optional)</span>}
                      </label>
                      <input
                        name="email" type="email" value={form.email} onChange={handleChange}
                        required={!user}
                        placeholder={user ? 'optional' : 'your@email.com'}
                        className="w-full px-3 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-white/25 focus:outline-none focus:border-blue-500/60 transition-colors"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs text-white/50 uppercase tracking-widest mb-1.5 font-semibold">Subject</label>
                    <select
                      name="subject" value={form.subject} onChange={handleChange} required
                      className="w-full px-3 py-2.5 rounded-lg bg-slate-800 border border-white/10 text-white text-sm focus:outline-none focus:border-blue-500/60 transition-colors"
                    >
                      <option value="" disabled>Choose a topic</option>
                      <option value="general">General Question</option>
                      <option value="bug">Bug / Issue</option>
                      <option value="collab">Collaboration</option>
                      <option value="feedback">Feedback</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs text-white/50 uppercase tracking-widest mb-1.5 font-semibold">Message</label>
                    <textarea
                      name="message" value={form.message} onChange={handleChange} required
                      placeholder="Write your message here..." rows={5}
                      className="w-full px-3 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-white/25 focus:outline-none focus:border-blue-500/60 transition-colors resize-none"
                    />
                  </div>

                  <button
                    type="submit" disabled={loading}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed rounded-lg font-bold text-sm transition-colors flex items-center justify-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    {loading ? 'Sending...' : 'Send Message'}
                  </button>
                </form>
              </>
            )}
          </div>

          {/* ── My Messages & Replies (logged-in users only) ── */}
          {user && (
            <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
              <div className="px-6 py-4 border-b border-white/10 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-400" />
                <h3 className="font-bold text-sm">My Messages & Admin Replies</h3>
                <button
                  onClick={loadMyMessages}
                  className="ml-auto text-xs text-white/35 hover:text-blue-300 transition-colors px-2 py-1 rounded hover:bg-white/5"
                >
                  ↻ Refresh
                </button>
              </div>

              {loadingMsgs ? (
                <div className="px-6 py-10 text-center text-white/40 text-sm">Loading messages...</div>
              ) : myMessages.length === 0 ? (
                <div className="px-6 py-10 text-center">
                  <MessageSquare className="w-8 h-8 text-white/15 mx-auto mb-2" />
                  <p className="text-white/35 text-sm">No messages yet — send one above!</p>
                </div>
              ) : (
                <div className="divide-y divide-white/5">
                  {myMessages.map(msg => (
                    <div key={msg.id} className="p-5">
                      {/* User message */}
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <span className="text-xs font-semibold text-white/60 uppercase tracking-widest">
                              {msg.subject}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${statusStyle(msg.status)}`}>
                              {statusLabel(msg.status)}
                            </span>
                          </div>
                          <p className="text-white/65 text-sm leading-relaxed">{msg.message}</p>
                          <div className="flex items-center gap-1 mt-2 text-white/25 text-xs">
                            <Clock className="w-3 h-3" />
                            {new Date(msg.created_at).toLocaleString()}
                          </div>
                        </div>
                      </div>

                      {/* Admin reply */}
                      {msg.reply ? (
                        <div className="mt-3 ml-3 pl-4 border-l-2 border-green-500/40 bg-green-500/5 rounded-r-lg py-3 pr-3">
                          <div className="flex items-center gap-2 mb-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-green-400 flex-shrink-0" />
                            <span className="text-xs font-semibold text-green-400">Admin Reply</span>
                            {msg.replied_at && (
                              <span className="text-xs text-white/25">
                                · {new Date(msg.replied_at).toLocaleString()}
                              </span>
                            )}
                          </div>
                          <p className="text-white/70 text-sm leading-relaxed">{msg.reply}</p>
                        </div>
                      ) : (
                        <div className="mt-2 ml-3 pl-4 border-l-2 border-white/10 py-2">
                          <p className="text-white/25 text-xs italic">Waiting for admin reply...</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Login prompt for guests */}
          {!user && (
            <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl px-5 py-4 text-center">
              <p className="text-blue-300 text-sm">
                <Link to="/login" className="underline font-semibold hover:text-white transition-colors">Log in</Link>
                {' '}to track your messages and receive admin replies.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center py-6 border-t border-white/10 text-white/30 text-xs">
        Credit Card Fraud Detection · KNN Algorithm ·Project
      </footer>
    </div>
  );
}