import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Config, Session } from '../types';

interface ConfigContextType {
  config: Config | null;
  sessions: Session[];
  currentSession: string | null;
  setConfig: (config: Config) => Promise<void>;
  loadConfig: () => Promise<void>;
  loadSessions: () => Promise<void>;
  createSession: (title: string) => Promise<string>;
  deleteSession: (id: string) => Promise<void>;
  setCurrentSession: (id: string | null) => void;
}

const ConfigContext = createContext<ConfigContextType | null>(null);

export function ConfigProvider({ children }: { children: ReactNode }) {
  const [config, setConfigState] = useState<Config | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);

  const loadConfig = async () => {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      setConfigState(data);
    } catch (err) {
      console.error('Failed to load config:', err);
    }
  };

  const setConfig = async (newConfig: Config) => {
    const res = await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newConfig),
    });
    if (res.ok) {
      setConfigState(newConfig);
    }
  };

  const loadSessions = async () => {
    try {
      const res = await fetch('/api/sessions');
      const data = await res.json();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const createSession = async (title: string): Promise<string> => {
    const res = await fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    const data = await res.json();
    await loadSessions();
    return data.id;
  };

  const deleteSession = async (id: string) => {
    await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
    await loadSessions();
  };

  useEffect(() => {
    loadConfig();
    loadSessions();
  }, []);

  return (
    <ConfigContext.Provider
      value={{
        config,
        sessions,
        currentSession,
        setConfig,
        loadConfig,
        loadSessions,
        createSession,
        deleteSession,
        setCurrentSession,
      }}
    >
      {children}
    </ConfigContext.Provider>
  );
}

export function useConfig() {
  const ctx = useContext(ConfigContext);
  if (!ctx) throw new Error('useConfig must be used within ConfigProvider');
  return ctx;
}
