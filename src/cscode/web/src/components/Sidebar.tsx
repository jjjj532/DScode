import { useConfig } from '../context/ConfigContext';
import { useState } from 'react';

interface SidebarProps {
  onSettingsClick: () => void;
  onNewChat: () => void;
}

export function Sidebar({ onSettingsClick, onNewChat }: SidebarProps) {
  const { sessions, currentSession, setCurrentSession, createSession, deleteSession } = useConfig();
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const handleNewChat = async () => {
    const id = await createSession('New Chat');
    setCurrentSession(id);
    onNewChat();
  };

  const handleSessionClick = (sessionId: string) => {
    setCurrentSession(sessionId);
  };

  const handleDeleteClick = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (deleteConfirmId === sessionId) {
      deleteSession(sessionId);
      setDeleteConfirmId(null);
    } else {
      setDeleteConfirmId(sessionId);
      setTimeout(() => setDeleteConfirmId(null), 3000);
    }
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
              borderRadius: 6,
              margin: '4px 8px',
              transition: 'background 0.15s',
            }}
            onClick={() => handleSessionClick(session.id)}
          >
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {session.title}
            </span>
            {deleteConfirmId === session.id ? (
              <span style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                    setDeleteConfirmId(null);
                  }}
                  style={{
                    background: '#ff4444',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '2px 8px',
                    fontSize: 11,
                    cursor: 'pointer',
                  }}
                >
                  确认删除
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteConfirmId(null);
                  }}
                  style={{
                    background: '#999',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '2px 8px',
                    fontSize: 11,
                    cursor: 'pointer',
                  }}
                >
                  取消
                </button>
              </span>
            ) : (
              <button
                onClick={(e) => handleDeleteClick(e, session.id)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#999',
                  padding: '4px 8px',
                  fontSize: 12,
                  borderRadius: '4px',
                  opacity: 0.6,
                  transition: 'opacity 0.15s',
                }}
                title="Delete session"
              >
                ✕
              </button>
            )}
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
