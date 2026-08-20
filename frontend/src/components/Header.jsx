import React from 'react';
import { Presentation, Sparkles, ShieldCheck } from 'lucide-react';

export default function Header() {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Presentation className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              AI Presentation Designer
              <span className="text-xs bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded-full font-semibold">
                Phase 4 Agent
              </span>
            </h1>
            <p className="text-xs text-slate-400">Powered by LangGraph Multi-Agent Engine</p>
          </div>
        </div>

        <div className="flex items-center space-x-4 text-xs text-slate-400">
          <span className="flex items-center gap-1 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" /> Self-Reflection Loops
          </span>
          <span className="flex items-center gap-1 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Native Editable .PPTX
          </span>
        </div>
      </div>
    </header>
  );
}
