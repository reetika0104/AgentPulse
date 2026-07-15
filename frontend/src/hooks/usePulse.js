/**
 * PULSE Custom Hooks
 * Reusable React hooks for the PULSE dashboard.
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';

/**
 * Hook for periodic data fetching with auto-refresh.
 */
export function usePolling(fetchFn, intervalMs = 30000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const result = await fetchFn();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, intervalMs);
    return () => clearInterval(interval);
  }, [fetchData, intervalMs]);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook for agent status tracking.
 */
export function useAgentStatus() {
  return usePolling(() => api.getStatus(), 30000);
}

/**
 * Hook for execution history.
 */
export function useExecutions(limit = 10) {
  return usePolling(() => api.getExecutions(limit), 15000);
}

/**
 * Hook for triggering a brief with loading state.
 */
export function useTriggerBrief() {
  const [triggering, setTriggering] = useState(false);
  const [result, setResult] = useState(null);

  const trigger = async () => {
    setTriggering(true);
    try {
      const res = await api.triggerBrief();
      setResult(res);
      return res;
    } catch (err) {
      setResult({ error: err.message });
      throw err;
    } finally {
      setTriggering(false);
    }
  };

  return { trigger, triggering, result };
}
