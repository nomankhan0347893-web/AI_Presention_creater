import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

const AGENTS = [
  { id: 'CONTENT_DRAFT', name: '1. Content Agent', desc: 'Drafts outline & strips jargon' },
  { id: 'DIAGRAMS', name: '2. Diagram Agent', desc: 'Renders Mermaid visuals to PNG' },
  { id: 'IMAGES', name: '3. Image Agent', desc: 'Sources context stock photos' },
  { id: 'DESIGN', name: '4. Design Agent', desc: 'Builds HTML grid & JSON spec' },
  { id: 'REFINEMENT', name: '5. Refinement Agent', desc: 'Performs visual QA audit' },
  { id: 'EXPORT', name: '6. Export Agent', desc: 'Builds native .pptx shapes' }
];

export default function AgentStepper({ currentStep }) {
  const getStepIndex = (step) => AGENTS.findIndex(a => a.id === step);
  const activeIndex = getStepIndex(currentStep);

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
      <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
        Live LangGraph Agent Execution Pipeline
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {AGENTS.map((agent, index) => {
          const isDone = currentStep === 'COMPLETE' || (activeIndex > -1 && index < activeIndex);
          const isActive = currentStep !== 'COMPLETE' && activeIndex === index;

          return (
            <div
              key={agent.id}
              className={`p-3.5 rounded-xl border transition ${
                isDone
                  ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                  : isActive
                  ? 'bg-blue-950/50 border-blue-500 text-blue-200 ring-2 ring-blue-500/20'
                  : 'bg-slate-900/50 border-slate-800 text-slate-500'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : isActive ? (
                  <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-600" />
                )}
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/80">
                  {isDone ? 'DONE' : isActive ? 'ACTIVE' : 'WAITING'}
                </span>
              </div>
              <p className="text-xs font-semibold">{agent.name}</p>
              <p className="text-[10px] text-slate-400 mt-1 leading-tight">{agent.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
