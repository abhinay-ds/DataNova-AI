import {
  ArrowUpRight,
  BarChart3,
  Bot,
  Database,
  FileCode2,
  MessageSquareText,
  Sparkles,
  Table2,
  User,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import AnalysisCard from "./AnalysisCard";
import ModelCard from "./ModelCard";
import ChartCard from "./ChartCard";
import CodeCard from "./CodeCard";

import { useChat } from "../../context/ChatContext";

// =========================================================
// SUGGESTED QUESTIONS
// =========================================================

const suggestions = [
  {
    icon: Table2,
    title: "Explore my dataset",
    prompt: "Give me an overview of my dataset",
  },
  {
    icon: BarChart3,
    title: "Find patterns",
    prompt: "What are the most important patterns in my dataset?",
  },
  {
    icon: Database,
    title: "Check data quality",
    prompt: "Show me the missing values in my dataset",
  },
  {
    icon: FileCode2,
    title: "Generate Python",
    prompt: "Show me the Python code for this analysis",
  },
];

// =========================================================
// QUICK PROMPTS AFTER DATASET IS LOADED
// =========================================================

const analysisPrompts = [
  "What is the average age?",
  "Show me the distribution of the numeric columns",
  "Show me a correlation heatmap",
  "Find the most important patterns",
];

// =========================================================
// PROMPT EVENT
// =========================================================

function sendPromptToComposer(prompt) {
  window.dispatchEvent(
    new CustomEvent("datanova:prompt", {
      detail: {
        prompt,
      },
    })
  );
}

// =========================================================
// MAIN COMPONENT
// =========================================================

export default function ChatMessages() {
  const { messages } = useChat();

  // =======================================================
  // EMPTY STATE
  // =======================================================

  if (!messages || messages.length === 0) {
    return (
      <div className="flex h-full min-h-0 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-4xl flex-col justify-center px-4 py-8 sm:px-5 sm:py-10">

          {/* =================================================
              HERO
          ================================================= */}

          <div className="mx-auto w-full max-w-2xl text-center">

            {/* AI ICON */}

            <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 ring-1 ring-blue-100 dark:bg-blue-950/50 dark:ring-blue-900">
              <Sparkles
                size={25}
                className="text-blue-600 dark:text-blue-400"
              />
            </div>

            {/* EYEBROW */}

            <div className="mb-3 inline-flex items-center gap-1.5 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 dark:border-blue-900 dark:bg-blue-950/50">
              <Bot
                size={12}
                className="text-blue-600 dark:text-blue-400"
              />

              <span className="text-[10px] font-bold uppercase tracking-[0.1em] text-blue-600 dark:text-blue-400">
                AI Data Analyst
              </span>
            </div>

            {/* HEADING */}

            <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl dark:text-slate-100">
              Ask anything about{" "}
              <span className="text-blue-600 dark:text-blue-400">
                your data
              </span>
            </h1>

            {/* DESCRIPTION */}

            <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500 dark:text-slate-400">
              Upload your dataset and let DataNova AI analyze,
              visualize and explain your data using natural language.
            </p>
          </div>

          {/* =================================================
              QUICK START
          ================================================= */}

          <div className="mx-auto mt-9 w-full max-w-3xl">

            <div className="mb-3 flex items-center gap-2">
              <MessageSquareText
                size={14}
                className="text-slate-400"
              />

              <span className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-400">
                Quick start
              </span>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">

              {suggestions.map(
                ({
                  icon: Icon,
                  title,
                  prompt,
                }) => (
                  <button
                    key={title}
                    type="button"
                    onClick={() =>
                      sendPromptToComposer(prompt)
                    }
                    className="group flex min-h-[88px] items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-blue-200 hover:bg-blue-50/30 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-blue-900 dark:hover:bg-blue-950/20"
                  >

                    {/* ICON */}

                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-50 text-slate-500 transition-colors group-hover:bg-blue-50 group-hover:text-blue-600 dark:bg-slate-800 dark:text-slate-400 dark:group-hover:bg-blue-950/50 dark:group-hover:text-blue-400">
                      <Icon size={18} />
                    </div>

                    {/* TEXT */}

                    <div className="min-w-0 flex-1">

                      <p className="text-xs font-bold text-slate-800 dark:text-slate-200">
                        {title}
                      </p>

                      <p className="mt-1 line-clamp-2 text-[11px] leading-5 text-slate-400">
                        {prompt}
                      </p>

                    </div>

                    {/* ARROW */}

                    <ArrowUpRight
                      size={15}
                      className="shrink-0 text-slate-300 transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-blue-500"
                    />

                  </button>
                )
              )}

            </div>
          </div>

          {/* =================================================
              CAPABILITIES
          ================================================= */}

          <div className="mx-auto mt-8 flex max-w-3xl flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[10px] text-slate-400">

            <span className="flex items-center gap-1.5">
              <Database size={12} />
              Analyze datasets
            </span>

            <span className="hidden h-3 w-px bg-slate-200 sm:block dark:bg-slate-700" />

            <span className="flex items-center gap-1.5">
              <BarChart3 size={12} />
              Create charts
            </span>

            <span className="hidden h-3 w-px bg-slate-200 sm:block dark:bg-slate-700" />

            <span className="flex items-center gap-1.5">
              <FileCode2 size={12} />
              Generate Python
            </span>

          </div>

        </div>
      </div>
    );
  }

  // =======================================================
  // MESSAGE AREA
  // =======================================================

  return (
    <div className="h-full min-h-0 overflow-y-auto">

      <div className="mx-auto w-full max-w-4xl space-y-5 px-3 py-5 pb-36 sm:space-y-6 sm:px-4 sm:py-6">

        {messages.map((message, index) => (
          <Message
            key={message.id || index}
            message={message}
          />
        ))}

      </div>

    </div>
  );
}

// =========================================================
// MARKDOWN CONTENT
// =========================================================

function MarkdownContent({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{

        h1: ({ children }) => (
          <h1 className="mb-4 mt-2 text-2xl font-bold text-slate-900 dark:text-slate-100">
            {children}
          </h1>
        ),

        h2: ({ children }) => (
          <h2 className="mb-3 mt-5 text-xl font-bold text-slate-900 dark:text-slate-100">
            {children}
          </h2>
        ),

        h3: ({ children }) => (
          <h3 className="mb-2 mt-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
            {children}
          </h3>
        ),

        p: ({ children }) => (
          <p className="mb-3 last:mb-0">
            {children}
          </p>
        ),

        ul: ({ children }) => (
          <ul className="mb-3 list-disc space-y-1 pl-5">
            {children}
          </ul>
        ),

        ol: ({ children }) => (
          <ol className="mb-3 list-decimal space-y-1 pl-5">
            {children}
          </ol>
        ),

        li: ({ children }) => (
          <li>{children}</li>
        ),

        strong: ({ children }) => (
          <strong className="font-semibold text-slate-900 dark:text-slate-100">
            {children}
          </strong>
        ),

        blockquote: ({ children }) => (
          <blockquote className="my-3 border-l-4 border-blue-400 pl-4 text-slate-600 dark:text-slate-300">
            {children}
          </blockquote>
        ),

        hr: () => (
          <hr className="my-4 border-slate-200 dark:border-slate-700" />
        ),

        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            {children}
          </a>
        ),

        table: ({ children }) => (
          <div className="my-4 overflow-x-auto">
            <table className="w-full border-collapse border border-slate-200 text-sm dark:border-slate-700">
              {children}
            </table>
          </div>
        ),

        thead: ({ children }) => (
          <thead className="bg-slate-100 dark:bg-slate-800">
            {children}
          </thead>
        ),

        th: ({ children }) => (
          <th className="border border-slate-200 px-3 py-2 text-left font-semibold dark:border-slate-700">
            {children}
          </th>
        ),

        td: ({ children }) => (
          <td className="border border-slate-200 px-3 py-2 dark:border-slate-700">
            {children}
          </td>
        ),

        code: ({
          className,
          children,
          ...props
        }) => {
          const isInline = !className;

          if (isInline) {
            return (
              <code
                className="rounded bg-slate-200 px-1.5 py-0.5 font-mono text-xs text-slate-800 dark:bg-slate-700 dark:text-slate-200"
                {...props}
              >
                {children}
              </code>
            );
          }

          return (
            <code
              className="block overflow-x-auto rounded-lg bg-slate-950 p-4 font-mono text-xs leading-6 text-slate-100"
              {...props}
            >
              {children}
            </code>
          );
        },

        pre: ({ children }) => (
          <pre className="my-4 overflow-x-auto rounded-xl bg-slate-950">
            {children}
          </pre>
        ),

      }}
    >
      {content || ""}
    </ReactMarkdown>
  );
}

// =========================================================
// MESSAGE
// =========================================================

function Message({ message }) {
  const isUser = message.sender === "user";

  return (
    <div
      className={
        isUser
          ? "flex justify-end"
          : "flex justify-start"
      }
    >

      <div
        className={
          isUser
            ? "flex max-w-[90%] flex-row-reverse items-start gap-2.5 sm:max-w-[80%] sm:gap-3"
            : "flex w-full items-start gap-2.5 sm:gap-3"
        }
      >

        {/* =================================================
            AVATAR
        ================================================= */}

        <div
          className={
            isUser
              ? "flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm sm:h-9 sm:w-9"
              : "flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 sm:h-9 sm:w-9"
          }
        >
          {isUser ? (
            <User size={17} />
          ) : (
            <Bot size={17} />
          )}
        </div>

        {/* =================================================
            CONTENT
        ================================================= */}

        <div
          className={
            isUser
              ? "min-w-0"
              : "min-w-0 flex-1"
          }
        >

          {/* =================================================
              USER
          ================================================= */}

          {isUser && (
            <div className="rounded-2xl rounded-tr-md bg-blue-600 px-3.5 py-2.5 text-sm leading-6 text-white shadow-sm sm:px-4 sm:py-3">
              {message.text}
            </div>
          )}

          {/* =================================================
              ASSISTANT
          ================================================= */}

          {!isUser && (
            <div className="w-full min-w-0">

              {/* =================================================
                  TEXT
              ================================================= */}

              {message.type === "text" && (
                <div className="rounded-2xl rounded-tl-md border border-slate-100 bg-white px-3.5 py-3 text-sm leading-6 text-slate-700 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 sm:px-4">
                  <MarkdownContent
                    content={message.text}
                  />
                </div>
              )}

              {/* =================================================
                  ANALYSIS
              ================================================= */}

              {message.type === "analysis" && (
                <div className="w-full min-w-0">

                  {message.text && (
                    <div className="mb-3 rounded-2xl rounded-tl-md border border-slate-100 bg-white px-3.5 py-3 text-sm leading-6 text-slate-700 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 sm:px-4">
                      <MarkdownContent
                        content={message.text}
                      />
                    </div>
                  )}

                  <AnalysisCard
                    data={message.data}
                  />

                </div>
              )}

              {/* =================================================
                  MODEL
              ================================================= */}

              {message.type === "model" && (
                <div className="w-full min-w-0">

                  {message.text && (
                    <div className="mb-3 rounded-2xl rounded-tl-md border border-slate-100 bg-white px-3.5 py-3 text-sm leading-6 text-slate-700 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 sm:px-4">
                      <MarkdownContent
                        content={message.text}
                      />
                    </div>
                  )}

                  <ModelCard
                    data={message.data}
                  />

                </div>
              )}

              {/* =================================================
                  CHART
              ================================================= */}

              {message.type === "chart" && (
                <div className="w-full min-w-0">

                  {message.text && (
                    <div className="mb-3 rounded-2xl rounded-tl-md border border-slate-100 bg-white px-3.5 py-3 text-sm leading-6 text-slate-700 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 sm:px-4">
                      <MarkdownContent
                        content={message.text}
                      />
                    </div>
                  )}

                  <ChartCard
                    data={message.data}
                  />

                </div>
              )}

              {/* =================================================
                  CODE
              ================================================= */}

              {message.type === "code" && (
                <div className="w-full min-w-0">

                  {message.text && (
                    <div className="mb-3 rounded-2xl rounded-tl-md border border-slate-100 bg-white px-3.5 py-3 text-sm leading-6 text-slate-700 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 sm:px-4">
                      <MarkdownContent
                        content={message.text}
                      />
                    </div>
                  )}

                  <CodeCard
                    data={message.data}
                  />

                </div>
              )}

              {/* =================================================
                  LOADING
              ================================================= */}

              {message.type === "loading" && (
                <LoadingMessage />
              )}

              {/* =================================================
                  ERROR
              ================================================= */}

              {message.type === "error" && (
                <ErrorMessage
                  message={message.text}
                />
              )}

              {/* =================================================
                  FALLBACK
              ================================================= */}

              {![
                "text",
                "analysis",
                "model",
                "chart",
                "code",
                "loading",
                "error",
              ].includes(message.type) && (
                <div className="rounded-2xl rounded-tl-md border border-slate-100 bg-white px-3.5 py-3 text-sm leading-6 text-slate-700 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 sm:px-4">
                  <MarkdownContent
                    content={
                      message.text ||
                      message.message ||
                      "Response received."
                    }
                  />
                </div>
              )}

            </div>
          )}

        </div>
      </div>
    </div>
  );
}

// =========================================================
// LOADING MESSAGE
// =========================================================

function LoadingMessage() {
  return (
    <div className="rounded-2xl rounded-tl-md border border-slate-100 bg-white px-4 py-3.5 shadow-sm dark:border-slate-800 dark:bg-slate-900">

      <div className="flex items-center gap-3">

        <div className="flex items-center gap-1.5">

          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />

          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500 [animation-delay:150ms]" />

          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500 [animation-delay:300ms]" />

        </div>

        <div>

          <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
            DataNova is analyzing...
          </p>

          <p className="mt-0.5 text-[11px] text-slate-400">
            Processing your request
          </p>

        </div>

      </div>
    </div>
  );
}

// =========================================================
// ERROR MESSAGE
// =========================================================

function ErrorMessage({ message }) {
  return (
    <div className="rounded-2xl rounded-tl-md border border-red-200 bg-red-50 px-4 py-3.5 dark:border-red-900/60 dark:bg-red-950/20">

      <div className="flex items-start gap-3">

        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-100 text-red-600 dark:bg-red-900/50 dark:text-red-400">
          !
        </div>

        <div className="min-w-0">

          <p className="text-sm font-semibold text-red-800 dark:text-red-300">
            Something went wrong
          </p>

          <p className="mt-1 text-sm leading-6 text-red-700 dark:text-red-400">
            {message || "DataNova couldn't complete this request."}
          </p>

        </div>

      </div>
    </div>
  );
}