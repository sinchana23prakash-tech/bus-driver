import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[Application ErrorBoundary Caught Error]:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleSafeReload = () => {
    window.location.reload();
  };

  handleResetSession = () => {
    localStorage.removeItem('college_fuel_token');
    localStorage.removeItem('college_fuel_user');
    localStorage.removeItem('college_fuel_policies');
    window.location.href = '/login';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center justify-center p-6">
          <div className="max-w-xl w-full bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-2xl space-y-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center shrink-0">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Application Render Notice</h1>
                <p className="text-xs text-slate-400 mt-0.5">
                  An interface component encountered an unexpected error.
                </p>
              </div>
            </div>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs font-mono text-rose-300 overflow-x-auto max-h-40">
              {this.state.error?.toString() || 'Unknown runtime error'}
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <button
                type="button"
                onClick={this.handleSafeReload}
                className="flex-1 py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md transition"
              >
                Reload Page (Preserves Session)
              </button>
              <button
                type="button"
                onClick={this.handleResetSession}
                className="py-2.5 px-4 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 font-medium text-xs border border-slate-600 transition"
              >
                Clear Session &amp; Sign In
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
