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
