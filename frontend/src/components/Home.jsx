import { Link } from 'react-router-dom';
import { Shield, Zap, BarChart2, Lock, Clock, Database } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white">

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 py-24 text-center">
        <div className="inline-block mb-4 px-4 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs font-semibold uppercase tracking-widest">
          Project · KNN Algorithm
        </div>
        <h1 className="text-5xl font-extrabold leading-tight mb-6">
          Detect Credit Card Fraud
          <br />
          <span className="text-blue-400">with Machine Learning</span>
        </h1>
        <p className="text-lg text-white/60 max-w-xl mx-auto mb-10 leading-relaxed">
          A K-Nearest Neighbors based fraud detection system that analyzes transaction
          patterns to identify suspicious credit card activity in real time.
        </p>
        <div className="flex justify-center gap-4 flex-wrap">
          <Link
            to="/login"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-bold transition-colors shadow-lg"
          >
            Get Started →
          </Link>
          <Link
            to="/about"
            className="px-6 py-3 border border-white/20 hover:border-blue-400 hover:text-blue-300 rounded-lg font-semibold transition-colors"
          >
            Learn More
          </Link>
        </div>
      </section>

      {/* Stats Bar */}
      <div className="border-y border-white/10 bg-white/5">
        <div className="max-w-4xl mx-auto grid grid-cols-4 divide-x divide-white/10">
          {[
            { value: 'KNN',       label: 'Algorithm' },
            { value: '284K+',     label: 'Transactions Trained' },
            { value: '~99%',      label: 'Accuracy' },
            { value: 'Real-Time', label: 'Detection Speed' },
          ].map(s => (
            <div key={s.label} className="text-center py-8 px-4">
              <div className="text-2xl font-extrabold text-blue-400">{s.value}</div>
              <div className="text-xs text-white/40 uppercase tracking-widest mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Feature Cards */}
      <section className="max-w-5xl mx-auto px-6 py-20">
        <div className="text-center mb-12">
          <p className="text-xs text-blue-400 uppercase tracking-widest font-semibold mb-2">Core Features</p>
          <h2 className="text-3xl font-extrabold">How It Works</h2>
          <p className="text-white/50 mt-3 max-w-md mx-auto text-sm leading-relaxed">
            Our system uses KNN to classify transactions as fraudulent or legitimate based on historical patterns.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-5">
          {[
            { icon: <Zap className="w-5 h-5 text-blue-400" />,       title: 'KNN Classification',  desc: 'Compares each transaction with K nearest neighbors to determine fraud likelihood.' },
            { icon: <BarChart2 className="w-5 h-5 text-blue-400" />, title: 'Feature Analysis',     desc: 'Analyzes PCA-transformed features including Amount, Time, and V1–V28 variables.' },
            { icon: <Clock className="w-5 h-5 text-blue-400" />,     title: 'Real-Time Scoring',    desc: 'Each transaction receives a fraud score instantly for immediate action.' },
            { icon: <Lock className="w-5 h-5 text-blue-400" />,      title: 'Secure & Reliable',    desc: 'JWT authentication and role-based access control protect all endpoints.' },
            { icon: <BarChart2 className="w-5 h-5 text-blue-400" />, title: 'Model Insights',       desc: 'Admin dashboard shows precision, recall, and confusion matrix metrics.' },
            { icon: <Database className="w-5 h-5 text-blue-400" />,  title: 'Transaction History',  desc: 'Full audit trail of every analyzed transaction stored in the database.' },
          ].map(f => (
            <div
              key={f.title}
              className="bg-white/5 border border-white/10 rounded-xl p-5 hover:border-blue-500/40 hover:bg-blue-500/5 transition-all"
            >
              <div className="w-10 h-10 rounded-lg bg-blue-500/15 border border-blue-500/20 flex items-center justify-center mb-4">
                {f.icon}
              </div>
              <h3 className="font-bold text-sm mb-2 text-white">{f.title}</h3>
              <p className="text-white/45 text-xs leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="text-center py-16 border-t border-white/10">
        <h2 className="text-2xl font-extrabold mb-3">Ready to Detect Fraud?</h2>
        <p className="text-white/50 text-sm mb-6">Log in to access the dashboard and start analyzing transactions.</p>
        <Link
          to="/login"
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-bold transition-colors"
        >
          Login to Dashboard →
        </Link>
      </section>

      {/* Footer */}
      <footer className="text-center py-6 border-t border-white/10 text-white/30 text-xs">
        Credit Card Fraud Detection · KNN Algorithm · Project
      </footer>
    </div>
  );
}