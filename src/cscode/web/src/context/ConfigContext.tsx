import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Config, Session, SessionMessage } from '../types';

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
  loadSessionMessages: (sessionId: string) => Promise<SessionMessage[]>;
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
    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      if (!res.ok) {
        console.error('Failed to create session:', res.status);
        throw new Error('Failed to create session');
      }
      const data = await res.json();
      await loadSessions();
      return data.id;
    } catch (err) {
      console.error('Error creating session:', err);
      throw err;
    }
  };

  const deleteSession = async (id: string) => {
    try {
      const res = await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        console.error('Failed to delete session:', res.status);
        throw new Error('Failed to delete session');
      }
      await loadSessions();
    } catch (err) {
      console.error('Error deleting session:', err);
      throw err;
    }
  };

  const loadSessionMessages = async (sessionId: string): Promise<SessionMessage[]> => {
    try {
      const res = await fetch(`/api/sessions/${sessionId}/messages`);
      if (!res.ok) {
        console.error('Failed to load messages:', res.status);
        return [];
      }
      return await res.json();
    } catch (err) {
      console.error('Error loading messages:', err);
      return [];
    }
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
        loadSessionMessages,
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
