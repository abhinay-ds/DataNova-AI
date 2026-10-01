import {
  createContext,
  useContext,
  useState,
} from "react";

const ChatContext = createContext();


export function ChatProvider({ children }) {

  const [messages, setMessages] = useState([
    {
      id: Date.now(),
      sender: "assistant",
      type: "text",
      text:
        "Hello! I'm DataNova AI. Upload a dataset and ask me questions about it.",
    },
  ]);


  // =====================================================
  // ADD MESSAGE
  // =====================================================

  const addMessage = (message) => {

    setMessages((previousMessages) => [

      ...previousMessages,

      {
        id:
          message.id ||
          Date.now() +
            Math.random(),

        ...message,
      },

    ]);

  };


  // =====================================================
  // REMOVE MESSAGE
  // =====================================================

  const removeMessage = (id) => {

    setMessages((previousMessages) =>
      previousMessages.filter(
        (message) =>
          message.id !== id
      )
    );

  };


  // =====================================================
  // UPDATE MESSAGE
  // =====================================================

  const updateMessage = (
    id,
    updatedData
  ) => {

    setMessages((previousMessages) =>
      previousMessages.map(
        (message) =>

          message.id === id
            ? {
                ...message,
                ...updatedData,
              }
            : message
      )
    );

  };


  // =====================================================
  // CLEAR CHAT
  // =====================================================

  const clearMessages = () => {

    setMessages([
      {
        id: Date.now(),

        sender: "assistant",

        type: "text",

        text:
          "Hello! I'm DataNova AI. Upload a dataset and ask me questions about it.",
      },
    ]);

  };


  // =====================================================
  // CONTEXT PROVIDER
  // =====================================================

  return (

    <ChatContext.Provider
      value={{
        messages,
        setMessages,

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


// =====================================================
// CUSTOM HOOK
// =====================================================

export function useChat() {

  const context =
    useContext(ChatContext);


  if (!context) {

    throw new Error(
      "useChat must be used inside ChatProvider"
    );

  }


  return context;

}