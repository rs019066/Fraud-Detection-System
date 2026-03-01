import { Link } from 'react-router-dom';

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white">

      {/* Hero */}
      <section className="max-w-3xl mx-auto px-6 py-20 text-center">
        <div className="inline-block mb-4 px-4 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs font-semibold uppercase tracking-widest">
          About the Project
        </div>
        <h1 className="text-4xl font-extrabold mb-5">
          Credit Card Fraud Detection
          <br />
          <span className="text-blue-400">Using K-Nearest Neighbors</span>
        </h1>
        <p className="text-white/55 text-base leading-relaxed">
          A machine learning project built to understand how KNN can be applied to real-world
          financial fraud detection, using the popular Kaggle creditcard dataset.
        </p>
      </section>

      {/* Section 1: Algorithm */}
      <section className="max-w-5xl mx-auto px-6 pb-16 grid grid-cols-2 gap-10 items-start">
        <div>
          <p className="text-xs text-blue-400 uppercase tracking-widest font-semibold mb-2">The Algorithm</p>
          <h2 className="text-2xl font-extrabold mb-4">How KNN Detects Fraud</h2>
          <p className="text-white/55 text-sm leading-relaxed mb-3">
            K-Nearest Neighbors (KNN) is a simple yet powerful classification algorithm.
            For each new transaction, the model finds the K most similar historical
            transactions and classifies the new one based on the majority class.
          </p>
          <p className="text-white/55 text-sm leading-relaxed mb-5">
            If most of the K neighbors were fraudulent transactions, the new transaction
            is flagged as fraud. The key is choosing the right K and distance metric.
          </p>
          <div className="flex flex-wrap gap-2">
            {['Python', 'Scikit-learn', 'KNN', 'Pandas', 'NumPy', 'Flask', 'React'].map(t => (
              <span key={t} className="px-3 py-1 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs font-medium">
                {t}
              </span>
            ))}
          </div>
        </div>

        {/* KNN Steps */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <div className="relative border-l-2 border-blue-500/30 ml-4 space-y-6">
            {[
              'Receive new transaction data',
              'Extract & normalize features (V1–V28, Amount, Time)',
              'Calculate distance to all training points',
              'Select K nearest neighbors',
              'Majority vote → Fraud or Legitimate',
            ].map((step, i) => (
              <div key={i} className="flex items-start gap-4 pl-6 relative">
                <div className="absolute -left-4 w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                  {i + 1}
                </div>
                <p className="text-white/65 text-sm leading-snug pt-0.5">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Section 2: Dataset */}
      <section className="max-w-5xl mx-auto px-6 pb-20 grid grid-cols-2 gap-10 items-start">
        {/* Dataset box */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h4 className="text-xs uppercase tracking-widest text-white/50 font-semibold mb-4">Dataset Overview</h4>
          <div className="space-y-3">
            {[
              ['Total Transactions',  '284,807'],
              ['Fraudulent Cases',    '492 (0.172%)'],
              ['Legitimate Cases',    '284,315'],
              ['Features',            '30 (V1–V28, Amount, Time)'],
              ['Feature Type',        'PCA Transformed'],
              ['Source',              'Kaggle'],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between items-center border-b border-white/5 pb-2 last:border-0 last:pb-0">
                <span className="text-white/45 text-sm">{k}</span>
                <span className="text-blue-400 text-sm font-semibold">{v}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs text-blue-400 uppercase tracking-widest font-semibold mb-2">The Dataset</p>
          <h2 className="text-2xl font-extrabold mb-4">Real-World Transaction Data</h2>
          <p className="text-white/55 text-sm leading-relaxed mb-3">
            The project uses the Kaggle Credit Card Fraud Detection dataset — one of the
            most widely used benchmarks for fraud detection research.
          </p>
          <p className="text-white/55 text-sm leading-relaxed">
            The dataset is highly imbalanced, with fraudulent transactions accounting for
            only 0.172% of all transactions, making it a challenging and realistic problem.
          </p>
        </div>
      </section>

      {/* Project meta */}
      <section className="text-center py-12 border-t border-white/10 px-6">
        <div className="text-3xl mb-3">🎓</div>
        <h2 className="text-xl font-extrabold mb-2">Project</h2>
        <p className="text-white/45 text-sm max-w-lg mx-auto leading-relaxed">
          Built as part of a machine learning course to explore supervised classification
          algorithms in a real-world fraud detection context. All model training, evaluation,
          and backend development was done from scratch.
        </p>
        <div className="mt-6 flex justify-center gap-4">
          <Link to="/contact" className="px-5 py-2 border border-white/20 hover:border-blue-400 hover:text-blue-300 rounded-lg text-sm font-semibold transition-colors">
            Contact Me
          </Link>
          <Link to="/login" className="px-5 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition-colors">
            Try the Demo →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-6 border-t border-white/10 text-white/30 text-xs">
        Credit Card Fraud Detection · KNN Algorithm ·Project
      </footer>
    </div>
  );
}