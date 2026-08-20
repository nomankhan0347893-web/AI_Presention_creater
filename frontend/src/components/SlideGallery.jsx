import React from 'react';
import { Layers, Eye } from 'lucide-react';

export default function SlideGallery({ slides = [] }) {
  if (slides.length === 0) return null;

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-400" /> Generated Widescreen Slide Previews ({slides.length})
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {slides.map((slide) => (
          <div key={slide.slide_number} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3 hover:border-slate-700 transition">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-blue-400">Slide {slide.slide_number}</span>
              <span className="bg-slate-800 px-2 py-0.5 rounded text-[10px]">{slide.layout_type}</span>
            </div>
            
            <h4 className="text-sm font-bold text-slate-100 line-clamp-1">{slide.title}</h4>
            
            <div className="aspect-video bg-slate-950 rounded-lg border border-slate-800 flex items-center justify-center overflow-hidden relative group">
              {slide.preview_url ? (
                <>
                  <img 
                    src={`http://localhost:8000${slide.preview_url}`} 
                    alt={`Slide ${slide.slide_number}`}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    onError={(e) => {
                      e.target.onerror = null; 
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <a 
                      href={`http://localhost:8000${slide.preview_url}`} 
                      download={`slide_${slide.slide_number}_preview.png`}
                      target="_blank"
                      rel="noreferrer"
                      className="bg-blue-600 hover:bg-blue-500 text-white p-2 rounded-full shadow-lg transform translate-y-4 group-hover:translate-y-0 transition-all"
                      title="Download Preview Image"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                    </a>
                  </div>
                </>
              ) : null}
              <div className="absolute inset-0 flex items-center justify-center text-center p-3" style={{ display: slide.preview_url ? 'none' : 'flex' }}>
                <p className="text-xs text-slate-400 italic flex flex-col items-center gap-1.5">
                  <Eye className="w-4 h-4 text-slate-500 mb-1" /> Generating Preview...
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
