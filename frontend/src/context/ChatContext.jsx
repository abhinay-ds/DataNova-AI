import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getConversationMessages,
  getProjectConversations,
} from "../services/api";
import { formatDbMessageToUi } from "../utils/messageParser";
import { useProject } from "./ProjectContext";

const ChatContext = createContext(null);

const DEFAULT_WELCOME_MESSAGE = {
  id: "welcome-message",
  sender: "assistant",
  type: "text",
  text: "Hello! I'm DataNova AI. Upload a dataset and ask me questions about it.",
  data: null,
};

export function ChatProvider({ children }) {
  const { activeProject } = useProject();

  const [messages, setMessages] = useState([DEFAULT_WELCOME_MESSAGE]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Track the current project ID to prevent stale async responses
  const activeProjectIdRef = useRef(activeProject?.id);

  useEffect(() => {
    activeProjectIdRef.current = activeProject?.id;
  }, [activeProject?.id]);

  // =====================================================
  // LOAD CONVERSATION MESSAGES
  // =====================================================
  const loadConversationMessages = useCallback(
    async (projectId, conversationId) => {
      if (!projectId || !conversationId) return;

      try {
        setLoading(true);
        setError(null);

        const dbMessages = await getConversationMessages(
          projectId,
          conversationId
        );

        // Guard against stale response if project changed mid-request
        if (activeProjectIdRef.current !== projectId) return;

        if (Array.isArray(dbMessages) && dbMessages.length > 0) {
          // Sort chronologically just in case
          const sorted = [...dbMessages].sort(
            (a, b) => new Date(a.created_at) - new Date(b.created_at)
          );

          const uiMessages = sorted.flatMap(formatDbMessageToUi);
          setMessages(uiMessages);
        } else {
          setMessages([DEFAULT_WELCOME_MESSAGE]);
        }
      } catch (err) {
        if (activeProjectIdRef.current !== projectId) return;
        console.error("Failed to load conversation messages:", err);
        setError(err?.message || "Failed to load conversation messages.");
        setMessages([DEFAULT_WELCOME_MESSAGE]);
      } finally {
        if (activeProjectIdRef.current === projectId) {
          setLoading(false);
        }
      }
    },
    []
  );

  // =====================================================
  // LOAD PROJECT CONVERSATIONS
  // =====================================================
  const loadProjectConversations = useCallback(
    async (projectId) => {
      if (!projectId) {
        setConversations([]);
        setActiveConversationId(null);
        setMessages([DEFAULT_WELCOME_MESSAGE]);
        setError(null);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const convList = await getProjectConversations(projectId);

        if (activeProjectIdRef.current !== projectId) return;

        const convArray = Array.isArray(convList)
          ? convList
          : convList?.conversations || [];

        setConversations(convArray);

        if (convArray.length > 0) {
          // Latest conversation (ordered by updated_at desc on backend)
          const latest = convArray[0];
          setActiveConversationId(latest.id);
          await loadConversationMessages(projectId, latest.id);
        } else {
          setActiveConversationId(null);
          setMessages([DEFAULT_WELCOME_MESSAGE]);
        }
      } catch (err) {
        if (activeProjectIdRef.current !== projectId) return;
        console.error("Failed to load project conversations:", err);
        setError(err?.message || "Failed to load conversations.");
        setConversations([]);
        setActiveConversationId(null);
        setMessages([DEFAULT_WELCOME_MESSAGE]);
      } finally {
        if (activeProjectIdRef.current === projectId) {
          setLoading(false);
        }
      }
    },
    [loadConversationMessages]
  );

  // Reload conversations when active project changes
  useEffect(() => {
    let isCancelled = false;

    if (!activeProject?.id) {
      setConversations([]);
      setActiveConversationId(null);
      setMessages([DEFAULT_WELCOME_MESSAGE]);
      setError(null);
      return;
    }

    loadProjectConversations(activeProject.id);

    return () => {
      isCancelled = true;
    };
  }, [activeProject?.id, loadProjectConversations]);

  // =====================================================
  // SELECT SPECIFIC CONVERSATION
  // =====================================================
  const selectConversation = useCallback(
    async (conversationId) => {
      if (!activeProject?.id || !conversationId) return;
      setActiveConversationId(conversationId);
      await loadConversationMessages(activeProject.id, conversationId);
    },
    [activeProject?.id, loadConversationMessages]
  );

  // =====================================================
  // MESSAGE MUTATIONS
  // =====================================================
  const addMessage = (message) => {
    setMessages((prev) => [
      ...prev,
      {
        id: message.id || Date.now() + Math.random(),
        ...message,
      },
    ]);
  };

  const removeMessage = (id) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== id));
  };

  const updateMessage = (id, updatedData) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === id ? { ...msg, ...updatedData } : msg))
    );
  };

  const clearMessages = () => {
    setActiveConversationId(null);
    setMessages([DEFAULT_WELCOME_MESSAGE]);
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        setMessages,
        conversations,
        setConversations,
        activeConversationId,
        setActiveConversationId,
        loading,
        error,
        loadProjectConversations,
        loadConversationMessages,
        selectConversation,
        addMessage,
        removeMessage,
        updateMessage,
        clearMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);

  if (!context) {
    throw new Error("useChat must be used inside ChatProvider");
  }

  return context;
}