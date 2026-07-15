import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import BriefCard from '../components/BriefCard';
import StatusCard from '../components/StatusCard';
import ExecutionLogs from '../components/ExecutionLogs';
import ServiceHealth from '../components/ServiceHealth';
import Header from '../components/Header';

export default function Dashboard({ onLogout }) {
  const [brief, setBrief] = useState(null);
  const [status, setStatus] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);

  const fetchData = async () => {
    try {
      const [briefRes, statusRes, execRes, healthRes] = await Promise.allSettled([
        api.getLatestBrief(),
        api.getStatus(),
        api.getExecutions(10),
        api.getHealth(),
      ]);

      if (briefRes.status === 'fulfilled') setBrief(briefRes.value?.brief);
      if (statusRes.status === 'fulfilled') setStatus(statusRes.value);
      if (execRes.status === 'fulfilled') setExecutions(execRes.value?.executions || []);
      if (healthRes.status === 'fulfilled') setHealth(healthRes.value);
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
      setTimeout(fetchData, 3000);
    } catch (err) {
      console.error('Trigger failed:', err);
    } finally {
      setTriggering(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-pulse-600/20 mb-4">
            <svg className="animate-spin w-6 h-6 text-pulse-400" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <p className="text-gray-400">Loading PULSE...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Header onLogout={onLogout} onTrigger={handleTrigger} triggering={triggering} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatusCard
            title="Agent Status"
            value={status?.status || 'active'}
            icon="⚡"
            type="status"
          />
          <StatusCard
            title="Next Run"
            value={status?.schedule || '7:00 AM'}
            icon="⏰"
            type="schedule"
          />
          <StatusCard
            title="Last Execution"
            value={status?.last_execution?.status || 'N/A'}
            icon="✅"
            type="execution"
          />
          <StatusCard
            title="AI Model"
            value="Nova Micro"
            icon="🧠"
            type="model"
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Brief - Takes 2 columns */}
          <div className="lg:col-span-2">
            <BriefCard brief={brief} />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <ServiceHealth health={health} />
            <ExecutionLogs executions={executions} />
          </div>
        </div>
      </main>
    </div>
  );
}
