import { useState, useEffect } from 'react';
import { useConfig } from '../context/ConfigContext';
import { Config } from '../types';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const PROVIDERS = ['openai', 'anthropic', 'ollama', 'custom'] as const;

const MODEL_OPTIONS: Record<string, string[]> = {
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo'],
  anthropic: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
  ollama: ['llama3.2', 'llama3.1', 'qwen2.5', 'mistral'],
  custom: [],
};

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const { config, setConfig } = useConfig();
  const [localConfig, setLocalConfig] = useState<Partial<Config>>({});
  const [customProvider, setCustomProvider] = useState('');
  const [customModel, setCustomModel] = useState('');

  useEffect(() => {
    if (config) {
      setLocalConfig({ ...config });
      if (config.provider && !PROVIDERS.includes(config.provider as any)) {
        setCustomProvider(config.provider);
        setCustomModel(config.model || '');
      }
    }
  }, [config]);

  const handleSave = async () => {
    const provider = customProvider || localConfig.provider || 'openai';
    const model = customModel || localConfig.model || 'gpt-4o';

    const configToSave: Config = {
      provider: provider as Config['provider'],
      model: model,
      api_base: localConfig.api_base || null,
      api_key: localConfig.api_key,
      max_tokens: localConfig.max_tokens || 4096,
      temperature: localConfig.temperature ?? 0.7,
      top_p: localConfig.top_p ?? 1.0,
      system_prompt: localConfig.system_prompt || null,
    };

    await setConfig(configToSave);
    onClose();
  };

  const handleProviderChange = (provider: string) => {
    if (provider === 'custom') {
      setLocalConfig({ ...localConfig, provider: 'custom' });
    } else {
      const models = MODEL_OPTIONS[provider] || [];
      setLocalConfig({
        ...localConfig,
        provider: provider as Config['provider'],
        model: models[0] || '',
        api_base: provider === 'ollama' ? 'http://localhost:11434' : '',
      });
    }
  };

  if (!isOpen) return null;

  const isCustom = localConfig.provider === 'custom' || customProvider;

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
            value={isCustom ? 'custom' : (localConfig.provider || 'openai')}
            onChange={(e) => handleProviderChange(e.target.value)}
            style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14 }}
          >
            {PROVIDERS.map((p) => (
              <option key={p} value={p}>
                {p === 'custom' ? 'Custom (自定义)' : p.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {isCustom && (
          <>
            <div>
              <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>Custom Provider Name</label>
              <input
                type="text"
                value={customProvider}
                onChange={(e) => setCustomProvider(e.target.value)}
                placeholder="e.g., custom-openai, azure-openai"
                style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14 }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>Custom Model Name</label>
              <input
                type="text"
                value={customModel}
                onChange={(e) => setCustomModel(e.target.value)}
                placeholder="e.g., gpt-4-turbo, llama-3-70b"
                style={{ width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ddd', fontSize: 14 }}
              />
            </div>
          </>
        )}

        {!isCustom && (
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
        )}

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
