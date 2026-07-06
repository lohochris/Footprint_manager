import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import {
  useListAiSessionsQuery,
  useListAiMessagesQuery,
  useCreateAiSessionMutation,
  useSendAiMessageMutation,
  AiMessage,
} from '../api/aiAssistantApi';
import { routes } from '@/router/routes';

// ─── Retry Button ─────────────────────────────────────────────────────────────

const RetryButton: React.FC<{ onClick: () => void }> = ({ onClick }) => (
  <button
    onClick={onClick}
    style={{
      background: 'transparent',
      border: '1px solid currentColor',
      color: 'inherit',
      padding: '0.375rem 0.875rem',
      borderRadius: '6px',
      cursor: 'pointer',
      fontSize: '0.875rem',
    }}
  >
    Retry
  </button>
);

// ─── Message Bubble ───────────────────────────────────────────────────────────

const MessageBubble: React.FC<{ message: AiMessage }> = ({ message }) => {
  const isUser = message.role === 'user';
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '0.75rem',
      }}
    >
      <div
        style={{
          maxWidth: '75%',
          padding: '0.75rem 1rem',
          borderRadius: isUser ? '1rem 1rem 0.25rem 1rem' : '1rem 1rem 1rem 0.25rem',
          background: isUser
            ? 'var(--color-primary, #3b82f6)'
            : 'var(--color-bg-subtle, #f3f4f6)',
          color: isUser ? '#fff' : 'var(--color-text, #111827)',
          fontSize: '0.875rem',
          lineHeight: 1.6,
          wordBreak: 'break-word',
        }}
      >
        {message.content}
        <div
          style={{
            marginTop: '0.25rem',
            fontSize: '0.65rem',
            opacity: 0.65,
            textAlign: 'right',
          }}
        >
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

// ─── Session List ─────────────────────────────────────────────────────────────

interface SessionListProps {
  workspaceId: string;
  activeSessionId: string | null;
  onSelect: (id: string) => void;
  onNewSession: () => void;
  isCreating: boolean;
}

const SessionList: React.FC<SessionListProps> = ({
  workspaceId,
  activeSessionId,
  onSelect,
  onNewSession,
  isCreating,
}) => {
  const { data, isLoading, error, refetch } = useListAiSessionsQuery({ workspaceId });
  const sessions = data?.results ?? [];

  return (
    <aside
      style={{
        width: '260px',
        flexShrink: 0,
        borderRight: '1px solid var(--color-border, #e5e7eb)',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--color-bg-canvas, #f9fafb)',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '1rem',
          borderBottom: '1px solid var(--color-border, #e5e7eb)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>Sessions</span>
        <button
          onClick={onNewSession}
          disabled={isCreating}
          style={{
            background: 'var(--color-primary, #3b82f6)',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            padding: '0.375rem 0.75rem',
            cursor: isCreating ? 'wait' : 'pointer',
            fontSize: '0.75rem',
            fontWeight: 500,
            opacity: isCreating ? 0.7 : 1,
          }}
        >
          {isCreating ? 'Creating…' : '+ New'}
        </button>
      </div>

      {/* Body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
        {isLoading && (
          <p style={{ padding: '0.75rem', fontSize: '0.875rem', color: 'var(--color-text-muted, #6b7280)' }}>
            Loading sessions…
          </p>
        )}

        {error && !isLoading && (
          <div style={{ padding: '0.75rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
            <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem' }}>Failed to load sessions</p>
            <RetryButton onClick={refetch} />
          </div>
        )}

        {!isLoading && !error && sessions.length === 0 && (
          <p style={{ padding: '0.75rem', fontSize: '0.875rem', color: 'var(--color-text-muted, #6b7280)' }}>
            No sessions yet. Start a new one above.
          </p>
        )}

        {sessions.map((session) => (
          <button
            key={session.id}
            onClick={() => onSelect(session.id)}
            style={{
              display: 'block',
              width: '100%',
              textAlign: 'left',
              padding: '0.625rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              background: session.id === activeSessionId
                ? 'var(--color-primary-subtle, #eff6ff)'
                : 'transparent',
              color: session.id === activeSessionId
                ? 'var(--color-primary-dark, #1e40af)'
                : 'var(--color-text, #111827)',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: session.id === activeSessionId ? 600 : 400,
              marginBottom: '0.25rem',
              borderLeft: session.id === activeSessionId
                ? '3px solid var(--color-primary, #3b82f6)'
                : '3px solid transparent',
              overflow: 'hidden',
              whiteSpace: 'nowrap',
              textOverflow: 'ellipsis',
            }}
          >
            {session.title}
          </button>
        ))}
      </div>
    </aside>
  );
};

// ─── Conversation Panel ───────────────────────────────────────────────────────

interface ConversationPanelProps {
  sessionId: string;
  workspaceId: string;
}

const ConversationPanel: React.FC<ConversationPanelProps> = ({ sessionId, workspaceId: _workspaceId }) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [draft, setDraft] = useState('');

  const { data, isLoading, error, refetch } = useListAiMessagesQuery({ sessionId });
  const [sendMessage, { isLoading: isSending }] = useSendAiMessageMutation();

  const messages = data?.results ?? [];

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  const handleSend = useCallback(async () => {
    const trimmed = draft.trim();
    if (!trimmed || isSending) return;
    setDraft('');
    try {
      await sendMessage({ sessionId, content: trimmed });
    } catch {
      // error surfaced via RTK Query mutation state
    }
  }, [draft, isSending, sendMessage, sessionId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem' }}>
        {isLoading && (
          <p style={{ color: 'var(--color-text-muted, #6b7280)', fontSize: '0.875rem' }}>
            Loading conversation…
          </p>
        )}

        {error && !isLoading && (
          <div style={{ textAlign: 'center', color: 'var(--color-danger, #ef4444)', padding: '2rem' }}>
            <p style={{ marginBottom: '0.75rem' }}>Failed to load messages</p>
            <RetryButton onClick={refetch} />
          </div>
        )}

        {!isLoading && !error && messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--color-text-muted, #6b7280)', paddingTop: '3rem' }}>
            <p style={{ fontSize: '1.125rem', fontWeight: 500 }}>Session started</p>
            <p style={{ fontSize: '0.875rem' }}>Send your first message below.</p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        <div ref={bottomRef} />
      </div>

      {/* Composer */}
      <div
        style={{
          padding: '1rem 1.25rem',
          borderTop: '1px solid var(--color-border, #e5e7eb)',
          display: 'flex',
          gap: '0.75rem',
          background: 'var(--color-bg-surface, #fff)',
        }}
      >
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
          rows={3}
          disabled={isSending}
          style={{
            flex: 1,
            padding: '0.625rem 0.875rem',
            border: '1px solid var(--color-border, #e5e7eb)',
            borderRadius: '8px',
            fontSize: '0.875rem',
            resize: 'none',
            outline: 'none',
            fontFamily: 'inherit',
            lineHeight: 1.5,
            background: isSending ? 'var(--color-bg-subtle, #f3f4f6)' : '#fff',
          }}
        />
        <button
          onClick={handleSend}
          disabled={!draft.trim() || isSending}
          style={{
            alignSelf: 'flex-end',
            padding: '0.625rem 1.25rem',
            background: draft.trim() && !isSending
              ? 'var(--color-primary, #3b82f6)'
              : 'var(--color-border, #e5e7eb)',
            color: draft.trim() && !isSending ? '#fff' : 'var(--color-text-muted, #6b7280)',
            border: 'none',
            borderRadius: '8px',
            cursor: draft.trim() && !isSending ? 'pointer' : 'not-allowed',
            fontWeight: 600,
            fontSize: '0.875rem',
            transition: 'background 0.15s',
          }}
        >
          {isSending ? 'Sending…' : 'Send'}
        </button>
      </div>
    </div>
  );
};

// ─── Empty State ───────────────────────────────────────────────────────────────

const EmptyState: React.FC<{ onNewSession: () => void; isCreating: boolean }> = ({
  onNewSession,
  isCreating,
}) => (
  <div
    style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '1rem',
      color: 'var(--color-text-muted, #6b7280)',
      padding: '2rem',
    }}
  >
    <div style={{ fontSize: '3rem' }}>🤖</div>
    <h2 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-text, #111827)' }}>
      AI Investigation Assistant
    </h2>
    <p style={{ margin: 0, fontSize: '0.875rem', textAlign: 'center', maxWidth: '360px' }}>
      Start a new session to ask questions, analyze evidence, or get recommendations on your active investigations.
    </p>
    <button
      onClick={onNewSession}
      disabled={isCreating}
      style={{
        background: 'var(--color-primary, #3b82f6)',
        color: '#fff',
        border: 'none',
        borderRadius: '8px',
        padding: '0.75rem 1.5rem',
        cursor: isCreating ? 'wait' : 'pointer',
        fontWeight: 600,
        fontSize: '0.875rem',
        opacity: isCreating ? 0.7 : 1,
      }}
    >
      {isCreating ? 'Creating Session…' : 'Start New Session'}
    </button>
  </div>
);

// ─── Main View ────────────────────────────────────────────────────────────────

export const AiAssistantView: React.FC = () => {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [createSession, { isLoading: isCreating, error: createError }] = useCreateAiSessionMutation();

  // Honour ?new=true deep link from dashboard widget
  const shouldStartNew = searchParams.get('new') === 'true';

  const handleNewSession = useCallback(async () => {
    if (!workspaceId) return;
    try {
      const session = await createSession({ workspaceId }).unwrap();
      setActiveSessionId(session.id);
      // Clear the ?new=true query param so refresh doesn't re-trigger
      navigate(routes.ai(workspaceId), { replace: true });
    } catch {
      // error surfaced inline via createError
    }
  }, [createSession, navigate, workspaceId]);

  // Auto-trigger new session on mount when ?new=true
  useEffect(() => {
    if (shouldStartNew && workspaceId && !isCreating && !activeSessionId) {
      handleNewSession();
    }
    // We only want this to fire once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!workspaceId) {
    return (
      <div style={{ padding: '2rem', color: 'var(--color-danger, #ef4444)' }}>
        Error: No workspace selected. Please navigate from the dashboard.
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        height: '100%',
        overflow: 'hidden',
        background: 'var(--color-bg-surface, #fff)',
      }}
    >
      {/* Left: Session list */}
      <SessionList
        workspaceId={workspaceId}
        activeSessionId={activeSessionId}
        onSelect={setActiveSessionId}
        onNewSession={handleNewSession}
        isCreating={isCreating}
      />

      {/* Right: Conversation or empty state */}
      {activeSessionId ? (
        <ConversationPanel sessionId={activeSessionId} workspaceId={workspaceId} />
      ) : (
        <EmptyState onNewSession={handleNewSession} isCreating={isCreating} />
      )}

      {/* Creation error banner */}
      {createError && (
        <div
          style={{
            position: 'fixed',
            bottom: '1.5rem',
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'var(--color-danger, #ef4444)',
            color: '#fff',
            padding: '0.75rem 1.25rem',
            borderRadius: '8px',
            fontSize: '0.875rem',
            zIndex: 1000,
          }}
        >
          Failed to create session. Please try again.
        </div>
      )}
    </div>
  );
};
