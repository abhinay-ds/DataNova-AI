import {
  BarChart3,
  BrainCircuit,
  Database,
  FileSpreadsheet,
  Sparkles,
} from "lucide-react";

import { useChat } from "../../context/ChatContext";
import ChatMessages from "../chat/ChatMessages";


const suggestions = [
  {
    icon: FileSpreadsheet,
    title: "Analyze a dataset",
    description:
      "Upload CSV, Excel or JSON and get an instant profile.",
    prompt: "Give me an overview of my dataset",
  },
  {
    icon: BarChart3,
    title: "Create a visualization",
    description:
      "Ask for charts, distributions, trends or relationships.",
    prompt: "Create a useful visualization of my dataset",
  },
  {
    icon: BrainCircuit,
    title: "Train a model",
    description:
      "Build, evaluate and compare machine learning models.",
    prompt: "Train a suitable machine learning model on my dataset",
  },
  {
    icon: Database,
    title: "Query your data",
    description:
      "Ask natural-language questions about any loaded dataset.",
    prompt: "Give me some useful insights from my dataset",
  },
];


function sendPrompt(prompt) {
  window.dispatchEvent(
    new CustomEvent("datanova:prompt", {
      detail: prompt,
    })
  );
}


function isInitialMessage(message) {
  if (!message) return false;

  const text = String(
    message.text ||
    message.content ||
    ""
  ).toLowerCase();

  return (
    text.includes("hello! i'm datanova") ||
    text.includes("upload a dataset") ||
    text.includes("uploaded successfully") ||
    text.includes("dataset is ready")
  );
}


export default function ChatArea() {
  const { messages = [] } = useChat();

  /*
   * Keep the polished welcome workspace visible when the only
   * messages are the automatic welcome/upload messages.
   *
   * Once the user actually asks a question, ChatMessages takes over.
   */

  const hasRealConversation = messages.some(
    (message) =>
      !isInitialMessage(message) &&
      message?.sender !== "system"
  );


  if (hasRealConversation) {
    return (
      <div className="chat-area chat-area-conversation">
        <ChatMessages />
      </div>
    );
  }


  return (
    <div className="chat-area">

      <div className="workspace-welcome">

        {/* ================================================
            WELCOME HEADER
            ================================================ */}

        <div className="workspace-welcome-header">

          <div className="workspace-ai-pill">
            <Sparkles size={15} />
            <span>DataNova AI</span>
          </div>


          <h1>
            What will you
            <br />
            <span>discover today?</span>
          </h1>


          <p>
            Analyze, visualize and predict from your data
            <br className="desktop-break" />
            using natural language.
          </p>

        </div>


        {/* ================================================
            QUICK ACTION CARDS
            ================================================ */}

        <div className="workspace-suggestion-grid">

          {suggestions.map(
            ({
              icon: Icon,
              title,
              description,
              prompt,
            }) => (

              <button
                key={title}
                type="button"
                className="workspace-suggestion-card"
                onClick={() => sendPrompt(prompt)}
              >

                <div className="workspace-suggestion-icon">
                  <Icon size={21} />
                </div>


                <div className="workspace-suggestion-content">

                  <h3>
                    {title}
                  </h3>

                  <p>
                    {description}
                  </p>

                </div>

              </button>

            )
          )}

        </div>

      </div>

    </div>
  );
}