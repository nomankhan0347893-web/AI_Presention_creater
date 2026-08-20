import React, { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';

export default function AgentLogsConsole({ logs = [] }) {
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-3 font-mono">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
          <Terminal className="w-4 h-4 text-blue-400" /> Real-time Agent Reasoning Logs
        </span>
        <span className="text-[10px] text-slate-500">{logs.length} events logged</span>
      </div>

      <div className="h-44 overflow-y-auto space-y-1.5 text-xs pr-2 scrollbar-thin scrollbar-thumb-slate-700">
        {logs.length === 0 ? (
          <p className="text-slate-600 italic">Waiting for prompt submission...</p>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="text-slate-300 flex items-start space-x-2">
              <span className="text-blue-500 font-bold select-none">&gt;</span>
              <span>{log}</span>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
