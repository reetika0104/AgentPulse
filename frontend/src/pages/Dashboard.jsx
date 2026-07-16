import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import BriefCard from '../components/BriefCard';
import StatusCard from '../components/StatusCard';
import ExecutionLogs from '../components/ExecutionLogs';
import ServiceHealth from '../components/ServiceHealth';
import AgentWorkflow from '../components/AgentWorkflow';
import Header from '../components/Header';
import MetricsPanel from '../components/MetricsPanel';

export default function Dashboard({ onLogout }) {
  const [brief, setBrief] = useState(null);
  const [status, setStatus] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);

  const fetchData = async () => {
    try {
      const [briefRes, statusRes, execRes, healthRes, metricsRes] = await Promise.allSettled([
        api.getLatestBrief(),
        api.getStatus(),
        api.getExecutions(10),
        api.getHealth(),
        api.getMetrics(),
      ]);

      if (briefRes.status === 'fulfilled') setBrief(briefRes.value?.brief);
      if (statusRes.status === 'fulfilled') setStatus(statusRes.value);
      if (execRes.status === 'fulfilled') setExecutions(execRes.value?.executions || []);
      if (healthRes.status === 'fulfilled') setHealth(healthRes.value);
      if (metricsRes.status === 'fulfilled') setMetrics(metricsRes.value);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleTrigger = async () => {
    setTriggering(true);
    try {
      await api.triggerBrief();
      setTimeout(fetchData, 5000);
    } catch (err) {
      console.error('Trigger failed:', err);
    } finally {
      setTimeout(() => setTriggering(false), 3000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 mb-4 animate-float shadow-[0_0_40px_rgba(99,102,241,0.3)]">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold gradient-text mb-2">PULSE</h2>
          <p className="text-gray-500 text-sm">Initializing agent systems...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header onLogout={onLogout} onTrigger={handleTrigger} triggering={triggering} status={status} />

      <main className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Cards Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="animate-fade-in-up stagger-1">
            <StatusCard
              title="Agent Status"
              value={status?.status || 'active'}
              subtitle="Always-On • Autonomous"
              icon="⚡"
              type="status"
            />
          </div>
          <div className="animate-fade-in-up stagger-2">
            <StatusCard
              title="Next Scheduled Run"
              value={_formatNextRun(status?.next_run)}
              subtitle={`Schedule: ${status?.schedule || '0 7 * * *'}`}
              icon="⏰"
              type="schedule"
            />
          </div>
          <div className="animate-fade-in-up stagger-3">
            <StatusCard
              title="Last Execution"
              value={status?.last_execution?.status || 'Awaiting first run'}
              subtitle={status?.last_execution?.duration_seconds ? `${status.last_execution.duration_seconds}s` : ''}
              icon="✅"
              type="execution"
            />
          </div>
          <div className="animate-fade-in-up stagger-4">
            <StatusCard
              title="AI Model"
              value="Amazon Nova"
              subtitle={status?.model || 'amazon.nova-micro-v1:0'}
              icon="🧠"
              type="model"
            />
          </div>
        </div>

        {/* Agent Workflow Pipeline */}
        <div className="mb-8 animate-fade-in-up stagger-5">
          <AgentWorkflow triggering={triggering} />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Brief - Takes 7 columns */}
          <div className="lg:col-span-7 space-y-6">
            <div className="animate-fade-in-up stagger-5">
              <BriefCard brief={brief} />
            </div>
            <div className="animate-fade-in-up stagger-6">
              <ExecutionLogs executions={executions} />
            </div>
          </div>

          {/* Right Sidebar - 5 columns */}
          <div className="lg:col-span-5 space-y-6">
            <div className="animate-fade-in-up stagger-3">
              <MetricsPanel metrics={metrics} executions={executions} />
            </div>
            <div className="animate-fade-in-up stagger-4">
              <ServiceHealth health={health} />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.04] mt-12 py-6">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-gray-600">
            <span>PULSE v1.0.0 • Powered by Amazon Bedrock & AWS</span>
            <span>Built for AWS Builder Center Weekend Challenge 2026</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

function _formatNextRun(isoString) {
  if (!isoString) return '7:00 AM';
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  } catch {
    return '7:00 AM';
  }
}
