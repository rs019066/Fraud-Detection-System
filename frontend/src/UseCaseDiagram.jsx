import React, { useState } from 'react';
import { User, Shield, Bot, Circle, ArrowRight } from 'lucide-react';

const UseCaseDiagram = () => {
  const [hoveredUseCase, setHoveredUseCase] = useState(null);
  const [selectedActor, setSelectedActor] = useState('all');

  // Actor definitions
  const actors = {
    regular: {
      id: 'regular',
      name: 'Regular User',
      subtitle: '(Fraud Analyst)',
      icon: User,
      color: 'blue',
      position: { x: 50, y: 200 }
    },
    admin: {
      id: 'admin',
      name: 'Admin User',
      subtitle: '(System Admin)',
      icon: Shield,
      color: 'orange',
      position: { x: 50, y: 400 }
    },
    system: {
      id: 'system',
      name: 'ML Model',
      subtitle: '(Fraud Detection)',
      icon: Bot,
      color: 'purple',
      position: { x: 900, y: 300 }
    }
  };

  // Use case definitions
  const useCases = [
    { id: 1, name: 'Login to\nSystem', category: 'auth', actors: ['regular', 'admin'], x: 300, y: 80 },
    { id: 2, name: 'Logout from\nSystem', category: 'auth', actors: ['regular', 'admin'], x: 450, y: 80 },
    { id: 3, name: 'Submit Transaction\nfor Analysis', category: 'regular', actors: ['regular', 'admin'], x: 300, y: 180 },
    { id: 4, name: 'View Fraud\nDetection Result', category: 'regular', actors: ['regular', 'admin'], x: 480, y: 180 },
    { id: 5, name: 'View My\nTransaction History', category: 'regular', actors: ['regular', 'admin'], x: 300, y: 280 },
    { id: 6, name: 'Search My\nTransactions', category: 'regular', actors: ['regular', 'admin'], x: 480, y: 280 },
    { id: 7, name: 'View All Transactions\n(System-wide)', category: 'admin', actors: ['admin'], x: 300, y: 400 },
    { id: 8, name: 'Delete\nTransaction', category: 'admin', actors: ['admin'], x: 480, y: 400 },
    { id: 9, name: 'View System\nStatistics', category: 'admin', actors: ['admin'], x: 650, y: 400 },
    { id: 10, name: 'Create New\nUser', category: 'admin', actors: ['admin'], x: 300, y: 500 },
    { id: 11, name: 'Disable/Enable\nUser', category: 'admin', actors: ['admin'], x: 480, y: 500 },
    { id: 12, name: 'Change User\nRole', category: 'admin', actors: ['admin'], x: 650, y: 500 },
    { id: 13, name: 'Analyze Transaction\nwith ML Model', category: 'system', actors: ['system'], x: 700, y: 180 },
    { id: 14, name: 'Calculate\nRisk Score', category: 'system', actors: ['system'], x: 700, y: 280 },
    { id: 15, name: 'Store in\nDatabase', category: 'system', actors: ['system'], x: 700, y: 350 }
  ];

  // Relationships
  const relationships = [
    { from: 'regular-actor', to: 1, type: 'uses' },
    { from: 'regular-actor', to: 2, type: 'uses' },
    { from: 'regular-actor', to: 3, type: 'uses' },
    { from: 'regular-actor', to: 4, type: 'uses' },
    { from: 'regular-actor', to: 5, type: 'uses' },
    { from: 'regular-actor', to: 6, type: 'uses' },
    { from: 'admin-actor', to: 7, type: 'uses' },
    { from: 'admin-actor', to: 8, type: 'uses' },
    { from: 'admin-actor', to: 9, type: 'uses' },
    { from: 'admin-actor', to: 10, type: 'uses' },
    { from: 'admin-actor', to: 11, type: 'uses' },
    { from: 'admin-actor', to: 12, type: 'uses' },
    { from: 3, to: 13, type: 'includes' },
    { from: 13, to: 14, type: 'includes' },
    { from: 3, to: 15, type: 'includes' }
  ];

  const categoryColors = {
    auth: { bg: 'bg-green-100', border: 'border-green-500', text: 'text-green-800' },
    regular: { bg: 'bg-blue-100', border: 'border-blue-500', text: 'text-blue-800' },
    admin: { bg: 'bg-orange-100', border: 'border-orange-500', text: 'text-orange-800' },
    system: { bg: 'bg-purple-100', border: 'border-purple-500', text: 'text-purple-800' }
  };

  const actorColors = {
    blue: { bg: 'bg-blue-50', border: 'border-blue-600', text: 'text-blue-600' },
    orange: { bg: 'bg-orange-50', border: 'border-orange-600', text: 'text-orange-600' },
    purple: { bg: 'bg-purple-50', border: 'border-purple-600', text: 'text-purple-600' }
  };

  const filteredUseCases = selectedActor === 'all'
    ? useCases
    : useCases.filter(uc => uc.actors.includes(selectedActor));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border-t-4 border-indigo-600">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Use Case Diagram - Credit Card Fraud Detection System
          </h1>
          <p className="text-gray-600">Interactive visualization of system actors and use cases</p>
        </div>

        {/* Actor Filter */}
        <div className="bg-white rounded-xl shadow-md p-4 mb-6">
          <div className="flex items-center gap-3">
            <span className="font-semibold text-gray-700">Filter by Actor:</span>
            <button
              onClick={() => setSelectedActor('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                selectedActor === 'all'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setSelectedActor('regular')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                selectedActor === 'regular'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Regular User
            </button>
            <button
              onClick={() => setSelectedActor('admin')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                selectedActor === 'admin'
                  ? 'bg-orange-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Admin User
            </button>
            <button
              onClick={() => setSelectedActor('system')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                selectedActor === 'system'
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              System
            </button>
          </div>
        </div>

        {/* Main Diagram */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
          <div className="relative" style={{ height: '650px' }}>
            <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1 }}>
              {(selectedActor === 'all' || selectedActor === 'admin' || selectedActor === 'regular') && (
                <>
                  <defs>
                    <marker id="inheritance-arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                      <path d="M0,0 L0,6 L9,3 z" fill="none" stroke="#4b5563" strokeWidth="2" />
                    </marker>
                  </defs>
                  <line
                    x1={actors.admin.position.x + 80}
                    y1={actors.admin.position.y}
                    x2={actors.regular.position.x + 80}
                    y2={actors.regular.position.y + 100}
                    stroke="#4b5563"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                    markerEnd="url(#inheritance-arrow)"
                  />
                  <text x={130} y={310} fill="#4b5563" fontSize="12" fontWeight="bold">
                    inherits
                  </text>
                </>
              )}

              {relationships.map((rel, idx) => {
                  const fromActor = typeof rel.from === 'string' && rel.from.includes('actor');

                let x1, y1, x2, y2;

                if (fromActor) {
                  const actorId = rel.from.split('-')[0];
                  const actor = actors[actorId];
                  if (!actor || (selectedActor !== 'all' && selectedActor !== actorId)) return null;
                  x1 = actor.position.x + 160;
                  y1 = actor.position.y + 50;
                  const useCase = useCases.find(uc => uc.id === rel.to);
                  if (!useCase) return null;
                  x2 = useCase.x;
                  y2 = useCase.y + 30;
                } else {
                  const fromUC = useCases.find(uc => uc.id === rel.from);
                  const toUC = useCases.find(uc => uc.id === rel.to);
                  if (!fromUC || !toUC) return null;
                  x1 = fromUC.x + 80;
                  y1 = fromUC.y + 30;
                  x2 = toUC.x;
                  y2 = toUC.y + 30;
                }

                const color = rel.type === 'uses' ? '#3b82f6' : '#9333ea';
                const dash = rel.type === 'includes' ? '5,5' : '0';

                return (
                  <line
                    key={idx}
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke={color}
                    strokeWidth="2"
                    strokeDasharray={dash}
                    opacity="0.4"
                  />
                );
              })}
            </svg>

            {/* Actors */}
            {Object.values(actors).map(actor => {
              const Icon = actor.icon;
              const colors = actorColors[actor.color];
              if (selectedActor !== 'all' && selectedActor !== actor.id) return null;

              return (
                <div
                  key={actor.id}
                  className={`absolute ${colors.bg} ${colors.border} border-2 rounded-xl p-4 shadow-lg transition-all hover:shadow-xl hover:scale-105`}
                  style={{
                    left: `${actor.position.x}px`,
                    top: `${actor.position.y}px`,
                    width: '160px',
                    zIndex: 10
                  }}
                >
                  <div className="flex flex-col items-center">
                    <div className={`${colors.bg} p-3 rounded-full border-2 ${colors.border} mb-2`}>
                      <Icon className={`w-8 h-8 ${colors.text}`} />
                    </div>
                    <h3 className={`font-bold text-sm ${colors.text} text-center`}>
                      {actor.name}
                    </h3>
                    <p className={`text-xs ${colors.text} text-center opacity-75`}>
                      {actor.subtitle}
                    </p>
                  </div>
                </div>
              );
            })}

            {/* Use Cases */}
            {filteredUseCases.map(useCase => {
              const colors = categoryColors[useCase.category];
              const isHovered = hoveredUseCase === useCase.id;

              return (
                <div
                  key={useCase.id}
                  className={`absolute ${colors.bg} ${colors.border} border-2 rounded-full p-4 shadow-md transition-all cursor-pointer ${
                    isHovered ? 'shadow-xl scale-110 z-20' : 'hover:shadow-lg hover:scale-105 z-10'
                  }`}
                  style={{
                    left: `${useCase.x}px`,
                    top: `${useCase.y}px`,
                    width: '140px',
                    height: '80px'
                  }}
                  onMouseEnter={() => setHoveredUseCase(useCase.id)}
                  onMouseLeave={() => setHoveredUseCase(null)}
                >
                  <div className="flex items-center justify-center h-full">
                    <p className={`text-xs font-semibold ${colors.text} text-center leading-tight whitespace-pre-line`}>
                      {useCase.name}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Circle className="w-5 h-5 text-indigo-600" />
              Use Case Categories
            </h3>
            <div className="space-y-3">
              {Object.entries(categoryColors).map(([key, colors]) => (
                <div key={key} className="flex items-center gap-3">
                  <div className={`w-12 h-12 ${colors.bg} ${colors.border} border-2 rounded-full`} />
                  <div>
                    <p className="font-semibold text-gray-700 capitalize">{key}</p>
                    <p className="text-xs text-gray-500">
                      {key === 'auth' && 'Authentication & Authorization'}
                      {key === 'regular' && 'Regular User Features'}
                      {key === 'admin' && 'Admin-Only Features'}
                      {key === 'system' && 'Backend/ML Operations'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
              <ArrowRight className="w-5 h-5 text-indigo-600" />
              Relationship Types
            </h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <svg width="60" height="20">
                  <line x1="0" y1="10" x2="60" y2="10" stroke="#3b82f6" strokeWidth="2" />
                </svg>
                <div>
                  <p className="font-semibold text-gray-700">Uses</p>
                  <p className="text-xs text-gray-500">Actor performs use case</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <svg width="60" height="20">
                  <line x1="0" y1="10" x2="60" y2="10" stroke="#9333ea" strokeWidth="2" strokeDasharray="5,5" />
                </svg>
                <div>
                  <p className="font-semibold text-gray-700">Includes</p>
                  <p className="text-xs text-gray-500">Mandatory dependency</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <svg width="60" height="20">
                  <line x1="0" y1="10" x2="60" y2="10" stroke="#4b5563" strokeWidth="2" strokeDasharray="5,5" />
                </svg>
                <div>
                  <p className="font-semibold text-gray-700">Inherits</p>
                  <p className="text-xs text-gray-500">Role inheritance</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Use Case Details */}
        {hoveredUseCase && (
          <div className="mt-6 bg-indigo-50 border-2 border-indigo-600 rounded-xl p-6 animate-fadeInUp">
            <h3 className="font-bold text-indigo-900 mb-2">
              Use Case Details: {useCases.find(uc => uc.id === hoveredUseCase)?.name.replace('\n', ' ')}
            </h3>
            <p className="text-sm text-indigo-700">
              <span className="font-semibold">Category:</span>{' '}
              {useCases.find(uc => uc.id === hoveredUseCase)?.category.toUpperCase()}
            </p>
            <p className="text-sm text-indigo-700">
              <span className="font-semibold">Available to:</span>{' '}
              {useCases.find(uc => uc.id === hoveredUseCase)?.actors.map(a => 
                actors[a]?.name
              ).join(', ')}
            </p>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeInUp {
          animation: fadeInUp 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default UseCaseDiagram;
