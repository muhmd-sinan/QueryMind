import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
  currentPage: string;
  onNavigate: (page: string) => void;
  status: {
    db_connected: boolean;
    api_connected: boolean;
    db_name?: string;
    model?: string;
  };
  onShowHistory: () => void;
}

export function Layout({ children, currentPage, onNavigate, status, onShowHistory }: LayoutProps) {
  const navItems = [
    { id: 'db', label: 'Database Connect', icon: '◈', disabled: false },
    { id: 'api', label: 'API Configuration', icon: '◆', disabled: false },
    { id: 'query', label: 'Query Interface', icon: '◉', disabled: !status.db_connected || !status.api_connected },
  ];

  return (
    <div className="min-h-screen gradient-bg">
      <div className="flex min-h-screen">
        <aside className="fixed left-0 top-0 h-[calc(100vh-2rem)] w-72 glass-card m-4 rounded-2xl p-6 flex flex-col overflow-y-auto scrollbar-thin">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gradient tracking-tight">AskSQL</h1>
            <p className="text-slate-400 text-sm mt-1 tracking-wide uppercase">Natural Language to SQL</p>
          </div>

          <nav className="flex-1">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">Navigation</p>
            <div className="space-y-2">
              {navItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => !item.disabled && onNavigate(item.id)}
                  disabled={item.disabled}
                  className={`w-full text-left px-4 py-3 rounded-xl transition-all duration-200 ${
                    item.disabled
                      ? 'opacity-40 cursor-not-allowed text-slate-600'
                      : currentPage === item.id
                      ? 'bg-sky-500/20 text-sky-400 border border-sky-500/40'
                      : 'hover:bg-slate-700/50 text-slate-300'
                  }`}
                >
                  <span className="mr-3 text-slate-400">{item.icon}</span>
                  {item.label}
                  {item.disabled && <span className="ml-2 text-xs text-slate-600">🔒</span>}
                </button>
              ))}
            </div>
          </nav>

          <div className="mt-6 pt-6 border-t border-slate-700/50">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">Status</p>
            <div className="space-y-2 text-sm">
              <div className="flex items-center">
                <span
                  className={`w-2 h-2 rounded-full mr-2 ${
                    status.db_connected ? 'bg-emerald-500' : 'bg-red-500'
                  }`}
                />
                <span className="text-slate-300">
                  {status.db_connected ? status.db_name || 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex items-center">
                <span
                  className={`w-2 h-2 rounded-full mr-2 ${
                    status.api_connected ? 'bg-emerald-500' : 'bg-red-500'
                  }`}
                />
                <span className="text-slate-300">
                  {status.api_connected ? status.model || 'API Ready' : 'Not configured'}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6">
            <button
              onClick={onShowHistory}
              className="w-full px-4 py-2 rounded-xl glass-button text-sm text-slate-300"
            >
              📋 View History
            </button>
          </div>
        </aside>

        <main className="flex-1 ml-80 p-4 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
