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
