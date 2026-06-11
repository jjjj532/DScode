# CScode Web UI Configuration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three-column layout with settings panel to configure LLM models through UI

**Architecture:** React frontend with FastAPI backend, SQLite storage for config and sessions

**Tech Stack:** React + Vite, FastAPI, SQLite, Pydantic

---

## File Structure

### Backend (FastAPI)
- Modify: `src/cscode/server/app.py` - Add config endpoints
- Modify: `src/cscode/core/config.py` - Add config persistence methods
- Test: `tests/` - Add API tests

### Frontend (React)
- Create: `src/cscode/web/src/components/Sidebar.tsx` - Session list
- Create: `src/cscode/web/src/components/SettingsPanel.tsx` - Settings panel
- Create: `src/cscode/web/src/context/ConfigContext.tsx` - Config state
- Create: `src/cscode/web/src/types.ts` - TypeScript types
- Modify: `src/cscode/web/src/App.tsx` - Three-column layout
- Modify: `src/cscode/web/src/main.tsx` - Add ConfigProvider

---

### Task 1: Backend - Add Config Persistence

**Files:**
- Modify: `src/cscode/core/config.py`
- Test: `tests/test_config.py` (extend existing)

- [ ] **Step 1: Add ConfigStore class for SQLite persistence**

Add to `src/cscode/core/config.py`:

```python
class ConfigStore:
    """Store and retrieve config from SQLite."""

    def __init__(self, db: Database):
        self.db = db

    async def get(self) -> dict[str, Any] | None:
        row = await self.db.fetchone(
            "SELECT data FROM config WHERE key = 'user_config'"
        )
        if row and row["data"]:
            import json
            return json.loads(row["data"])
        return None

    async def save(self, data: dict[str, Any]) -> None:
        import json
        data_json = json.dumps(data, default=str)
        await self.db.execute(
            """
            INSERT INTO config (key, data) VALUES ('user_config', ?)
            ON CONFLICT(key) DO UPDATE SET data = excluded.data
            """,
            (data_json,),
        )
```

- [ ] **Step 2: Ensure config table exists in Database**

Check `src/cscode/storage/db.py` for existing schema and add migration if needed.

- [ ] **Step 3: Run test to verify it compiles**

Run: `python -c "from cscode.core.config import ConfigStore; print('OK')"`
Expected: OK (no import errors)

- [ ] **Step 4: Commit**

```bash
git add src/cscode/core/config.py src/cscode/storage/db.py
git commit -m "feat: add ConfigStore for SQLite config persistence"
```

---

### Task 2: Backend - Add Config API Endpoints

**Files:**
- Modify: `src/cscode/server/app.py:1-180`
- Test: `tests/test_api.py` (create)

- [ ] **Step 1: Add Config model and endpoints**

Add to `src/cscode/server/app.py`:

```python
class ConfigRequest(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o"
    api_base: str | None = None
    api_key: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    system_prompt: str | None = None


class SessionCreateRequest(BaseModel):
    title: str = "New Session"


@app.get("/api/config")
async def get_config() -> dict[str, Any]:
    config = load_config()
    return config.to_dict()


@app.post("/api/config")
async def save_config(request: ConfigRequest) -> dict[str, Any]:
    config_data = request.model_dump(exclude_none=True)
    config_data.pop("api_key", None)  # Don't save API key

    # Save to database
    if _db is not None:
        from cscode.core.config import ConfigStore
        store = ConfigStore(_db)
        await store.save(config_data)

    return {"status": "saved", "config": config_data}


@app.post("/api/sessions", response_model=dict[str, Any])
async def create_session(request: SessionCreateRequest) -> dict[str, Any]:
    if _session_store is None:
        raise HTTPException(status_code=503, detail="Server not initialized")

    session = await _session_store.create(title=request.title)
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at.isoformat() if session.created_at else "",
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    if _session_store is None:
        raise HTTPException(status_code=503, detail="Server not initialized")

    await _session_store.delete(session_id)
    return {"status": "deleted", "id": session_id}
```

- [ ] **Step 2: Run test to verify it compiles**

Run: `python -c "from cscode.server.app import app; print('OK')"`
Expected: OK (no import errors)

- [ ] **Step 3: Write API tests**

Create `tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from cscode.server.app import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "model" in data
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/cscode/server/app.py tests/test_api.py
git commit -m "feat: add config and session API endpoints"
```

---

### Task 3: Frontend - Create TypeScript Types

**Files:**
- Create: `src/cscode/web/src/types.ts`

- [ ] **Step 1: Write TypeScript types**

Create `src/cscode/web/src/types.ts`:

```typescript
export interface Config {
  provider: 'openai' | 'anthropic' | 'ollama';
  model: string;
  api_base: string | null;
  api_key?: string;
  max_tokens: number;
  temperature: number;
  top_p: number;
  system_prompt: string | null;
}

export interface Session {
  id: string;
  title: string;
  provider?: string;
  model?: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd src/cscode/web && npx tsc --noEmit types.ts 2>&1 | head -20`
Expected: No errors (or simple type warnings)

- [ ] **Step 3: Commit**

```bash
git add src/cscode/web/src/types.ts
git commit -m "feat: add TypeScript types for frontend"
```

---

### Task 4: Frontend - Create Config Context

**Files:**
- Create: `src/cscode/web/src/context/ConfigContext.tsx`

- [ ] **Step 1: Write ConfigContext**

Create `src/cscode/web/src/context/ConfigContext.tsx`:

```typescript
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
```

- [ ] **Step 2: Create context directory and verify**

Run: `mkdir -p src/cscode/web/src/context`

- [ ] **Step 3: Commit**

```bash
git add src/cscode/web/src/context/ConfigContext.tsx
git commit -m "feat: add ConfigContext for state management"
```

---

### Task 5: Frontend - Create Sidebar Component

**Files:**
- Create: `src/cscode/web/src/components/Sidebar.tsx`

- [ ] **Step 1: Write Sidebar component**

Create `src/cscode/web/src/components/Sidebar.tsx`:

```typescript
import { useConfig } from '../context/ConfigContext';

interface SidebarProps {
  onSettingsClick: () => void;
}

export function Sidebar({ onSettingsClick }: SidebarProps) {
  const { sessions, currentSession, setCurrentSession, createSession, deleteSession } = useConfig();

  const handleNewChat = async () => {
    const id = await createSession('New Chat');
    setCurrentSession(id);
  };

  return (
    <div style={{
      width: 240,
      borderRight: '1px solid #e0e0e0',
      display: 'flex',
      flexDirection: 'column',
      background: '#f8f9fa',
      height: '100vh',
    }}>
      <div style={{ padding: 16, borderBottom: '1px solid #e0e0e0' }}>
        <button
          onClick={handleNewChat}
          style={{
            width: '100%',
            padding: '10px 16px',
            borderRadius: 8,
            border: 'none',
            background: '#646cff',
            color: '#fff',
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: 500,
          }}
        >
          + New Chat
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0' }}>
        {sessions.map((session) => (
          <div
            key={session.id}
            style={{
              padding: '10px 16px',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: currentSession === session.id ? '#e8e8e8' : 'transparent',
            }}
            onClick={() => setCurrentSession(session.id)}
          >
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {session.title}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                deleteSession(session.id);
              }}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#999',
                padding: 4,
                fontSize: 12,
              }}
              title="Delete"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <div style={{ padding: 16, borderTop: '1px solid #e0e0e0' }}>
        <button
          onClick={onSettingsClick}
          style={{
            width: '100%',
            padding: '8px',
            borderRadius: 6,
            border: '1px solid #ddd',
            background: '#fff',
            cursor: 'pointer',
            fontSize: 14,
          }}
        >
          ⚙ Settings
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create components directory**

Run: `mkdir -p src/cscode/web/src/components`

- [ ] **Step 3: Commit**

```bash
git add src/cscode/web/src/components/Sidebar.tsx
git commit -m "feat: add Sidebar component for session management"
```

---

### Task 6: Frontend - Create SettingsPanel Component

**Files:**
- Create: `src/cscode/web/src/components/SettingsPanel.tsx`

- [ ] **Step 1: Write SettingsPanel component**

Create `src/cscode/web/src/components/SettingsPanel.tsx`:

```typescript
import { useState, useEffect } from 'react';
import { useConfig } from '../context/ConfigContext';
import { Config } from '../types';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const PROVIDERS = ['openai', 'anthropic', 'ollama'] as const;

const MODEL_OPTIONS: Record<string, string[]> = {
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo'],
  anthropic: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
  ollama: ['llama3.2', 'llama3.1', 'qwen2.5', 'mistral'],
};

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const { config, setConfig } = useConfig();
  const [localConfig, setLocalConfig] = useState<Partial<Config>>({});

  useEffect(() => {
    if (config) {
      setLocalConfig({ ...config });
    }
  }, [config]);

  const handleSave = async () => {
    if (localConfig.provider && localConfig.model) {
      await setConfig(localConfig as Config);
      onClose();
    }
  };

  const handleProviderChange = (provider: string) => {
    const models = MODEL_OPTIONS[provider] || [];
    setLocalConfig({
      ...localConfig,
      provider: provider as Config['provider'],
      model: models[0] || '',
      api_base: provider === 'ollama' ? 'http://localhost:11434' : '',
    });
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      width: 360,
      height: '100vh',
      background: '#fff',
      boxShadow: '-2px 0 10px rgba(0,0,0,0.1)',
      padding: 24,
      overflowY: 'auto',
      zIndex: 1000,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ margin: 0, fontSize: 20 }}>Settings</h2>
        <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 24, cursor: 'pointer' }}>
          ✕
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>Provider</label>
          <select
            value={localConfig.provider || 'openai'}
            onChange={(e) => handleProviderChange(e.target.value)}
            style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14 }}
          >
            {PROVIDERS.map((p) => (
              <option key={p} value={p}>{p.toUpperCase()}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>Model</label>
          <select
            value={localConfig.model || ''}
            onChange={(e) => setLocalConfig({ ...localConfig, model: e.target.value })}
            style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14 }}
          >
            {(MODEL_OPTIONS[localConfig.provider || 'openai'] || []).map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>API Base URL</label>
          <input
            type="text"
            value={localConfig.api_base || ''}
            onChange={(e) => setLocalConfig({ ...localConfig, api_base: e.target.value })}
            placeholder={localConfig.provider === 'ollama' ? 'http://localhost:11434' : 'https://api.openai.com/v1'}
            style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14 }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>API Key</label>
          <input
            type="password"
            value={localConfig.api_key || ''}
            onChange={(e) => setLocalConfig({ ...localConfig, api_key: e.target.value })}
            placeholder="Enter API key"
            style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14 }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>
            Temperature: {localConfig.temperature ?? 0.7}
          </label>
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={localConfig.temperature ?? 0.7}
            onChange={(e) => setLocalConfig({ ...localConfig, temperature: parseFloat(e.target.value) })}
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>Max Tokens</label>
          <input
            type="number"
            value={localConfig.max_tokens ?? 4096}
            onChange={(e) => setLocalConfig({ ...localConfig, max_tokens: parseInt(e.target.value) })}
            min={1}
            max={128000}
            style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14 }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>System Prompt</label>
          <textarea
            value={localConfig.system_prompt || ''}
            onChange={(e) => setLocalConfig({ ...localConfig, system_prompt: e.target.value })}
            placeholder="You are CScode, an AI coding assistant..."
            rows={4}
            style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14, resize: 'vertical' }}
          />
        </div>

        <button
          onClick={handleSave}
          style={{
            padding: '12px 24px',
            borderRadius: 8,
            border: 'none',
            background: '#646cff',
            color: '#fff',
            fontSize: 14,
            fontWeight: 500,
            cursor: 'pointer',
            marginTop: 16,
          }}
        >
          Save Settings
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/cscode/web/src/components/SettingsPanel.tsx
git commit -m "feat: add SettingsPanel component for model configuration"
```

---

### Task 7: Frontend - Update App.tsx with Three-Column Layout

**Files:**
- Modify: `src/cscode/web/src/App.tsx:1-200`

- [ ] **Step 1: Replace App.tsx with three-column layout**

Replace `src/cscode/web/src/App.tsx` content:

```typescript
import { useState, useRef, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { SettingsPanel } from './components/SettingsPanel';
import { useConfig } from './context/ConfigContext';
import { Message } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const { currentSession, setCurrentSession } = useConfig();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg.content,
          session_id: currentSession,
        }),
      });
      const data = await res.json();
      setCurrentSession(data.session_id);
      const assistantMsg: Message = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg: Message = { role: 'assistant', content: 'Error: ' + String(err) };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar onSettingsClick={() => setSettingsOpen(true)} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', maxWidth: 800, margin: '0 auto', padding: 20 }}>
        <h1 style={{ borderBottom: '2px solid #646cff', paddingBottom: 10, marginBottom: 16 }}>
          CScode
          <span style={{ fontSize: 14, color: '#666', marginLeft: 10 }}>
            AI Coding Assistant
          </span>
        </h1>

        <div style={{
          flex: 1,
          overflowY: 'auto',
          border: '1px solid #e0e0e0',
          borderRadius: 8,
          padding: 16,
          marginBottom: 16,
          background: '#fafafa',
        }}>
          {messages.length === 0 && (
            <p style={{ color: '#999', textAlign: 'center', marginTop: 40 }}>
              Start a conversation with CScode...
            </p>
          )}
          {messages.map((msg, i) => (
            <div key={i} style={{
              marginBottom: 12,
              textAlign: msg.role === 'user' ? 'right' : 'left',
            }}>
              <div style={{
                display: 'inline-block',
                padding: '8px 16px',
                borderRadius: 12,
                background: msg.role === 'user' ? '#646cff' : '#e0e0e0',
                color: msg.role === 'user' ? '#fff' : '#000',
                maxWidth: '80%',
                whiteSpace: 'pre-wrap',
              }}>
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={endRef} />
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            disabled={loading}
            style={{
              flex: 1,
              padding: '10px 16px',
              borderRadius: 8,
              border: '1px solid #ccc',
              fontSize: 16,
            }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={{
              padding: '10px 24px',
              borderRadius: 8,
              border: 'none',
              background: loading ? '#ccc' : '#646cff',
              color: '#fff',
              fontSize: 16,
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
      </div>

      <SettingsPanel isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}

export default App;
```

- [ ] **Step 2: Verify build**

Run: `cd src/cscode/web && npm run build`
Expected: Build completes without errors

- [ ] **Step 3: Commit**

```bash
git add src/cscode/web/src/App.tsx
git commit -m "feat: implement three-column layout with sidebar and settings panel"
```

---

### Task 8: Frontend - Update main.tsx with ConfigProvider

**Files:**
- Modify: `src/cscode/web/src/main.tsx`

- [ ] **Step 1: Add ConfigProvider to main.tsx**

Replace `src/cscode/web/src/main.tsx`:

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ConfigProvider } from './context/ConfigContext';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider>
      <App />
    </ConfigProvider>
  </React.StrictMode>
);
```

- [ ] **Step 2: Verify build**

Run: `cd src/cscode/web && npm run build`
Expected: Build completes without errors

- [ ] **Step 3: Commit**

```bash
git add src/cscode/web/src/main.tsx
git commit -m "feat: wrap App with ConfigProvider"
```

---

### Task 9: Integration Test - Full Flow

**Files:**
- Test: Manual testing

- [ ] **Step 1: Build the app**

Run: `cd desktop && npx tauri build`

- [ ] **Step 2: Test the app**
- Launch the desktop app
- Verify three-column layout
- Click Settings → verify panel slides in
- Change provider/model → save
- Create new session → verify appears in sidebar
- Delete session → verify removed

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: integrate full web UI with config and sessions"
```

---

## Spec Coverage Check

- [x] Three-column layout (sidebar, chat, settings)
- [x] Settings panel slides from right
- [x] Provider selection (OpenAI/Anthropic/Ollama)
- [x] Model dropdown updates per provider
- [x] Custom api_base for enterprise models
- [x] Settings persist in backend SQLite
- [x] Create new chat sessions
- [x] Delete chat sessions
- [x] Chat messages persist via sessions API
