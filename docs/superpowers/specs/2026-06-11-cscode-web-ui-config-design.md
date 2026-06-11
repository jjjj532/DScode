# CScode Web UI Configuration Design

## Overview
Add a three-column layout with settings panel to the CScode desktop app web interface, allowing users to configure LLM models through the UI.

## Layout Structure

```
┌──────────┬─────────────────────────────┬──────────────────┐
│ 会话列表  │        聊天区域              │  设置面板        │
│          │                             │  (右侧滑出)       │
│ + 新建   │  [消息列表]                 │                  │
│          │                             │  Provider: [▼]   │
│ • 会话1  │  ─────────────────────     │  Model: [▼]      │
│ • 会话2  │                             │  API Base: [•••] │
│ • 会话3  │  [输入框] [发送]            │  API Key: [•••]  │
│          │                             │  Temperature:    │
│          │                             │  Max Tokens:    │
│          │                             │  System Prompt   │
└──────────┴─────────────────────────────┴──────────────────┘
```

## Data Flow

1. **Settings Panel** → React component in frontend
2. **Save Settings** → POST `/api/config` → Backend writes to SQLite
3. **Load Settings** → GET `/api/config` → Frontend renders
4. **Session Management** → POST/GET `/api/sessions` → SQLite

## Configuration Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| provider | dropdown | openai / anthropic / ollama | openai |
| model | dropdown | Model name (dynamic per provider) | gpt-4o |
| api_base | text | Custom API endpoint | empty (use official) |
| api_key | password | API key (not persisted in frontend) | empty |
| max_tokens | number | 1-128000 | 4096 |
| temperature | slider | 0.0 - 2.0 | 0.7 |
| system_prompt | textarea | Custom system prompt | empty |

## Model Selection Logic

**OpenAI:**
- Default model: gpt-4o
- api_base empty → use OpenAI official
- api_base set → use custom endpoint + OpenAI compatible

**Anthropic:**
- Default model: claude-3-5-sonnet-20241022
- api_base empty → use Anthropic official
- api_base set → use custom endpoint

**Ollama:**
- Default model: llama3.2
- Default api_base: http://localhost:11434
- User can customize Ollama server address

## Components

### Frontend (React)

1. **App.tsx** - Main layout with three columns
2. **Sidebar.tsx** - Session list with new/delete
3. **SettingsPanel.tsx** - Right slide-out settings panel
4. **ConfigContext.tsx** - Global config state management

### Backend (FastAPI)

1. **GET /api/config** - Return current config (mask api_key)
2. **POST /api/config** - Save config to database
3. **GET /api/sessions** - List sessions
4. **POST /api/sessions** - Create session
5. **DELETE /api/sessions/{id}** - Delete session

### Storage (SQLite)

- Extend existing `config` table or create new table for user settings
- Sessions already stored in `sessions` table

## Acceptance Criteria

1. User can see three-column layout (sidebar, chat, settings panel)
2. Settings panel slides in/out from right when gear icon clicked
3. User can select provider (OpenAI/Anthropic/Ollama)
4. Model dropdown updates based on selected provider
5. User can enter custom api_base for enterprise models
6. Settings are persisted in backend SQLite
7. User can create new chat sessions
8. User can delete chat sessions
9. Chat messages persist across page refreshes
