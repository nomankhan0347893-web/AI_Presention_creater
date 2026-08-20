import React from 'react';
import { Download, CheckCircle, Sparkles } from 'lucide-react';

export default function DownloadCard({ downloadUrl }) {
  if (!downloadUrl) return null;

  return (
    <div className="bg-gradient-to-r from-emerald-950/80 to-slate-900 border border-emerald-500/40 rounded-2xl p-6 shadow-2xl space-y-4">
      <div className="flex items-center space-x-4">
        <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
          <CheckCircle className="w-7 h-7" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-emerald-300 flex items-center gap-2">
            Presentation Ready! <Sparkles className="w-4 h-4 text-emerald-400" />
          </h3>
          <p className="text-xs text-slate-300">
            All 7 AI Agents completed layout, formatting, and design standard checks.
          </p>
        </div>
      </div>

      <a
        href={downloadUrl}
        download="AI_Presentation_Deck.pptx"
        className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition"
      >
        <Download className="w-5 h-5" />
        <span>Download Editable PowerPoint (.PPTX)</span>
      </a>
    </div>
  );
}
