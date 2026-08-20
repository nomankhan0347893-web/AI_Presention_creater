import React, { useState } from 'react';
import { Send, FileText, Palette, Sparkles } from 'lucide-react';

export default function PromptForm({ onSubmit, isLoading }) {
  const [prompt, setPrompt] = useState('Build an executive overview presentation on AI Agents in Healthcare, focusing on diagnostics, workflow automation, and patient care outcomes.');
  const [notes, setNotes] = useState('');
  const [theme, setTheme] = useState('#0D6EFD');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    onSubmit({ prompt, background_notes: notes, theme_color: theme });
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-6 shadow-2xl border border-slate-800 space-y-5">
      <div>
        <label className="block text-sm font-semibold text-slate-200 mb-2 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-400" /> What presentation would you like to build?
        </label>
        <textarea
          rows={3}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your presentation topic, audience, and goals..."
          className="w-full bg-slate-900 border border-slate-700 rounded-xl p-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
          required
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-slate-400" /> Background Notes / Material (Optional)
          </label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Paste raw notes, data points, or guidelines..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
            <Palette className="w-3.5 h-3.5 text-slate-400" /> Accent Brand Theme Color
          </label>
          <div className="flex items-center space-x-3">
            {['#0D6EFD', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444'].map((color) => (
              <button
                key={color}
                type="button"
                onClick={() => setTheme(color)}
                style={{ backgroundColor: color }}
                className={`w-7 h-7 rounded-full border-2 transition ${theme === color ? 'border-white scale-110 shadow-lg' : 'border-transparent opacity-70 hover:opacity-100'}`}
              />
            ))}
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-3.5 px-6 rounded-xl shadow-lg shadow-blue-500/25 flex items-center justify-center space-x-2 transition disabled:opacity-50"
      >
        {isLoading ? (
          <span>Agents Processing...</span>
        ) : (
          <>
            <span>Generate Presentation with AI Team</span>
            <Send className="w-4 h-4" />
          </>
        )}
      </button>
    </form>
  );
}
