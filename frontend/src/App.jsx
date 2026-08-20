import React, { useState } from 'react';
import Header from './components/Header';
import PromptForm from './components/PromptForm';
import AgentStepper from './components/AgentStepper';
import AgentLogsConsole from './components/AgentLogsConsole';
import SlideGallery from './components/SlideGallery';
import DownloadCard from './components/DownloadCard';

export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState('INITIATED');
  const [logs, setLogs] = useState([]);
  const [slides, setSlides] = useState([]);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const handleStartGeneration = async (payload) => {
    setIsLoading(true);
    setCurrentStep('CONTENT_DRAFT');
    setLogs(['Submitting job to FastAPI backend...']);
    setSlides([]);
    setDownloadUrl(null);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      const taskId = data.task_id;

      setLogs((prev) => [...prev, `Task ${taskId} initiated. Connecting WebSocket...`]);

      // Connect to WebSocket
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/status/${taskId}`;
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.step) setCurrentStep(msg.step);
        if (msg.message) setLogs((prev) => [...prev, `[${msg.step || 'INFO'}] ${msg.message}`]);

        if (msg.data?.slides) setSlides(msg.data.slides);
        if (msg.data?.download_url) {
          setDownloadUrl(msg.data.download_url);
          setIsLoading(false);
          ws.close();
        }
      };

      ws.onerror = () => {
        setLogs((prev) => [...prev, 'WebSocket fallback polling active...']);
        // Polling fallback
        const interval = setInterval(async () => {
          const res = await fetch(`/api/status/${taskId}`);
          const statusData = await res.json();
          if (statusData.current_step) setCurrentStep(statusData.current_step);
          if (statusData.logs) setLogs(statusData.logs);
          if (statusData.data?.download_url) {
            setDownloadUrl(statusData.data.download_url);
            if (statusData.data.slides) setSlides(statusData.data.slides);
            setIsLoading(false);
            clearInterval(interval);
          }
        }, 2000);
      };

    } catch (err) {
      setLogs((prev) => [...prev, `Error: ${err.message}`]);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header />

      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 space-y-8 w-full">
        <PromptForm onSubmit={handleStartGeneration} isLoading={isLoading} />
        
        <AgentStepper currentStep={currentStep} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <SlideGallery slides={slides} />
          </div>
          <div className="space-y-6">
            <DownloadCard downloadUrl={downloadUrl} />
            <AgentLogsConsole logs={logs} />
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-900 py-4 text-center text-xs text-slate-500">
        AI Presentation Designer Agent — Phase 4 Mentorship Project
      </footer>
    </div>
  );
}
