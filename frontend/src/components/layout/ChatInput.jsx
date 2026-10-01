import {
  Paperclip,
  Mic,
  SendHorizontal,
  FileSpreadsheet,
  Database,
  CheckCircle2,
  LoaderCircle,
  Sparkles,
} from "lucide-react";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  uploadDataset,
  sendMessage,
} from "../../services/api";

import { useDataset } from "../../context/DatasetContext";
import { useChat } from "../../context/ChatContext";
import { useProject } from "../../context/ProjectContext";


export default function ChatInput() {

  // =====================================================
  // REFS
  // =====================================================

  const fileInputRef = useRef(null);


  // =====================================================
  // CONTEXT
  // =====================================================

  const { setDataset } = useDataset();
  const { setMessages } = useChat();
  const { activeProject } = useProject();

  // =====================================================
  // STATE
  // =====================================================

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // Dataset preparation state
  const [uploadStage, setUploadStage] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);


  // =====================================================
  // SESSION ID
  // =====================================================

  const [sessionId] = useState(() => {

    const existingSessionId =
      localStorage.getItem(
        "datanova_session_id"
      );

    if (existingSessionId) {
      return existingSessionId;
    }

    const newSessionId =
      crypto.randomUUID();

    localStorage.setItem(
      "datanova_session_id",
      newSessionId
    );

    return newSessionId;
  });


  // =====================================================
  // CODE TASKS
  // =====================================================

  const codeTasks = [
    "generate_python",
    "generate_sql",
    "explain_code",
    "optimize_code",
    "convert_code",
    "debug_code",
  ];


  // =====================================================
  // DATASET UPLOAD
  // =====================================================

  const handleUpload = async (event) => {

    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    try {

      setLoading(true);
      setUploadProgress(8);
      setUploadStage("Uploading dataset...");

      // =================================================
      // Visual preparation stages
      // These do NOT change the real upload logic.
      // =================================================

      const stageTimers = [];

      stageTimers.push(
        setTimeout(() => {
          setUploadProgress(28);
          setUploadStage("Reading dataset...");
        }, 700)
      );

      stageTimers.push(
        setTimeout(() => {
          setUploadProgress(52);
          setUploadStage("Profiling rows and columns...");
        }, 1500)
      );

      stageTimers.push(
        setTimeout(() => {
          setUploadProgress(76);
          setUploadStage("Preparing AI analysis...");
        }, 2300)
      );

      // =================================================
      // Upload with SAME session ID
      // =================================================

      if (!activeProject?.id) {
  throw new Error(
    "Please select or create a project before uploading a dataset."
  );
}

const result = await uploadDataset(
  file,
  sessionId,
  activeProject.id
);

      stageTimers.forEach(clearTimeout);

      setUploadProgress(90);
      setUploadStage("Finalizing dataset...");

      // =================================================
      // Store Dataset In Frontend State
      // =================================================

      if (result?.dataset) {

        setDataset({

          ...result.dataset,

          filename:
            result.dataset.filename ||
            file.name,

        });

      }

      // =================================================
      // Dataset Ready
      // =================================================

      setUploadProgress(100);
      setUploadStage("Dataset ready");

      // Small delay so user can actually see Ready state
      await new Promise((resolve) =>
        setTimeout(resolve, 450)
      );

      // =================================================
      // Show Upload Message
      // =================================================

      setMessages((prev) => [

        ...prev,

        {
          id:
            Date.now() +
            Math.random(),

          sender: "assistant",

          type: "text",

          text:
            `Dataset "${file.name}" uploaded successfully. Your dataset is ready for analysis.`,

          data: null,
        },

      ]);

    } catch (error) {

      console.error(
        "Dataset upload failed:",
        error
      );

      setUploadProgress(0);
      setUploadStage("");

      setMessages((prev) => [

        ...prev,

        {
          id:
            Date.now() +
            Math.random(),

          sender: "assistant",

          type: "error",

          text:
            error?.message ||
            "Something went wrong while uploading the dataset.",

          data: null,
        },

      ]);

    } finally {

      setLoading(false);

      // Keep stage briefly reset after completion
      setTimeout(() => {
        setUploadStage("");
        setUploadProgress(0);
      }, 500);

      event.target.value = "";

    }

  };


  // =====================================================
  // DETECT CODE RESPONSE
  // =====================================================

  const isCodeResponse = (
    response,
    completedTasks = []
  ) => {

    const intent =
      String(
        response?.intent ||
        ""
      )
        .toLowerCase()
        .trim();

    const capability =
      String(
        response?.capability ||
        ""
      )
        .toLowerCase()
        .trim();

    if (
      codeTasks.includes(intent)
    ) {

      return true;

    }

    if (
      codeTasks.includes(capability)
    ) {

      return true;

    }

    return completedTasks.some(
      (task) =>
        codeTasks.includes(
          String(task)
            .toLowerCase()
            .trim()
        )
    );

  };


  // =====================================================
  // DETECT LANGUAGE FROM TASKS
  // =====================================================

  const detectLanguageFromTasks = (
    completedTasks = []
  ) => {

    const tasks =
      completedTasks.map(
        (task) =>
          String(task)
            .toLowerCase()
            .trim()
      );

    if (
      tasks.includes(
        "generate_sql"
      )
    ) {

      return "sql";

    }

    if (
      tasks.includes(
        "generate_python"
      )
    ) {

      return "python";

    }

    return "";

  };


  // =====================================================
  // DETECT LANGUAGE FROM CODE
  // =====================================================

  const detectLanguageFromCode = (
    code
  ) => {

    if (
      !code ||
      typeof code !== "string"
    ) {

      return "text";

    }

    const lowerCode =
      code.toLowerCase();

    const upperCode =
      code.toUpperCase();

    const sqlKeywords = [

      "SELECT ",
      "INSERT ",
      "UPDATE ",
      "DELETE ",
      "CREATE TABLE",
      "DROP TABLE",
      "ALTER TABLE",
      "FROM ",
      "WHERE ",
      "JOIN ",

    ];

    if (
      sqlKeywords.some(
        (keyword) =>
          upperCode.includes(
            keyword
          )
      )
    ) {

      return "sql";

    }

    if (
      lowerCode.includes(
        "public class"
      ) ||
      lowerCode.includes(
        "public static"
      ) ||
      lowerCode.includes(
        "system.out.println"
      )
    ) {

      return "java";

    }

    if (
      lowerCode.includes(
        "#include"
      ) ||
      lowerCode.includes(
        "using namespace std"
      ) ||
      lowerCode.includes(
        "std::"
      )
    ) {

      return "cpp";

    }

    if (
      lowerCode.includes(
        "function "
      ) ||
      lowerCode.includes(
        "const "
      ) ||
      lowerCode.includes(
        "let "
      )
    ) {

      return "javascript";

    }

    return "python";

  };


  // =====================================================
  // EXTRACT CODE DATA
  // =====================================================

  const extractCodeData = (
    response,
    completedTasks = []
  ) => {

    const rawData =
      response?.data;


    // ---------------------------------------------------
    // BACKEND RETURNS OBJECT
    // ---------------------------------------------------

    if (
      rawData &&
      typeof rawData === "object"
    ) {

      let code =
        rawData.code ||
        rawData.generated_code ||
        rawData.content ||
        rawData.output ||
        "";

      let explanation =
        rawData.explanation ||
        "";

      if (
        typeof code === "string" &&
        code.includes("```")
      ) {

        const match =
          code.match(
            /```([a-zA-Z0-9+#.-]*)\s*\n?([\s\S]*?)```/i
          );

        if (match) {

          const beforeCode =
            code
              .slice(
                0,
                match.index || 0
              )
              .trim();

          const afterCode =
            code
              .slice(
                (match.index || 0) +
                match[0].length
              )
              .trim();

          code =
            match[2]?.trim() ||
            "";

          if (!explanation) {

            explanation =
              [
                beforeCode,
                afterCode,
              ]
                .filter(Boolean)
                .join("\n\n")
                .trim();

          }

        }

      }

      return {

        ...rawData,

        code,

        language:
          rawData.language ||
          rawData.code_language ||
          detectLanguageFromTasks(
            completedTasks
          ) ||
          detectLanguageFromCode(
            code
          ),

        explanation,

      };

    }


    // ---------------------------------------------------
    // BACKEND RETURNS STRING
    // ---------------------------------------------------

    const content =
      typeof rawData === "string"
        ? rawData.trim()
        : "";

    let code = "";

    let explanation = "";

    let language =
      detectLanguageFromTasks(
        completedTasks
      );


    // ---------------------------------------------------
    // FIND MARKDOWN CODE BLOCK
    // ---------------------------------------------------

    const match =
      content.match(
        /```([a-zA-Z0-9+#.-]*)\s*\n?([\s\S]*?)```/i
      );

    if (match) {

      const detectedLanguage =
        match[1]
          ?.trim()
          .toLowerCase();

      code =
        match[2]?.trim() ||
        "";

      if (detectedLanguage) {

        language =
          detectedLanguage;

      }

      const beforeCode =
        content
          .slice(
            0,
            match.index || 0
          )
          .trim();

      const afterCode =
        content
          .slice(
            (match.index || 0) +
            match[0].length
          )
          .trim();

      explanation =
        [
          beforeCode,
          afterCode,
        ]
          .filter(Boolean)
          .join("\n\n")
          .trim();

    } else {

      explanation =
        content;

    }

    return {

      code,

      language:
        language ||
        detectLanguageFromCode(
          code
        ),

      explanation,

    };

  };


  // =====================================================
  // DETECT ANALYSIS RESPONSE
  // =====================================================

  const isAnalysisResponse = (
    data
  ) => {

    if (
      !data ||
      typeof data !== "object"
    ) {

      return false;

    }

    return Boolean(

      data.overview &&

      data.quality &&

      Array.isArray(
        data.insights
      ) &&

      Array.isArray(
        data.recommendations
      )

    );

  };


  // =====================================================
  // DETECT TRAINING RESPONSE
  // =====================================================

  const isTrainingResponse = (
    response
  ) => {

    const data =
      response?.data;

    return Boolean(

      data &&

      typeof data === "object" &&

      (
        data.best_model ||
        data.model_path ||
        Array.isArray(
          data.results
        )
      )

    );

  };


  // =====================================================
  // DETECT EVALUATION RESPONSE
  // =====================================================

  const isEvaluationResponse = (
    response
  ) => {

    const data =
      response?.data;

    return Boolean(

      data &&

      typeof data === "object" &&

      (
        data.accuracy !== undefined ||
        data.precision !== undefined ||
        data.recall !== undefined ||
        data.f1_score !== undefined ||
        data.confusion_matrix
      )

    );

  };


  // =====================================================
  // EXTRACT CHART URL
  // =====================================================

  const extractChartUrl = (
    data
  ) => {

    if (
      !data ||
      typeof data !== "object" ||
      !data.chart_path
    ) {

      return null;

    }

    const filename =
      data.chart_path
        .replace(
          /\\/g,
          "/"
        )
        .split("/")
        .pop();

    if (!filename) {

      return null;

    }

    return (
      `http://127.0.0.1:8000/charts/${filename}`
    );

  };


  // =====================================================
  // SEND MESSAGE
  // =====================================================

  const handleSend = async () => {

    if (
      !message.trim() ||
      loading
    ) {

      return;

    }

    const currentMessage =
      message.trim();

    setMessage("");

    // ===================================================
    // ADD USER MESSAGE TO FRONTEND
    // ===================================================

    setMessages((prev) => [

      ...prev,

      {
        id:
          Date.now() +
          Math.random(),

        sender: "user",

        type: "text",

        text:
          currentMessage,

        data: null,
      },

    ]);

    setLoading(true);

    try {

      // =================================================
      // Send message WITH SAME SESSION ID
      // =================================================

      const result =
        await sendMessage(
          currentMessage,
          sessionId
        );

      const backendResponses =
        Array.isArray(
          result?.responses
        )
          ? result.responses
          : [];

      const completedTasks =
        Array.isArray(
          result?.completed_tasks
        )
          ? result.completed_tasks
          : [];


      // =================================================
      // NO RESPONSE
      // =================================================

      if (
        backendResponses.length === 0
      ) {

        setMessages((prev) => [

          ...prev,

          {
            id:
              Date.now() +
              Math.random(),

            sender: "assistant",

            type: "text",

            text:
              result?.message ||
              "No response received.",

            data: null,
          },

        ]);

        return;

      }


      // =================================================
      // ML WORKFLOW
      // =================================================

      const trainingResponse =
        backendResponses.find(
          isTrainingResponse
        );

      const evaluationResponse =
        backendResponses.find(
          isEvaluationResponse
        );

      if (
        trainingResponse &&
        evaluationResponse
      ) {

        const trainingData =
          trainingResponse.data ||
          {};

        const evaluationData =
          evaluationResponse.data ||
          {};

        const combinedData = {

          problem_type:
            trainingData.problem_type ||
            evaluationData.problem_type ||
            "classification",

          best_model:
            trainingData.best_model ||
            "Model",

          model_path:
            trainingData.model_path ||
            null,

          training_score:
            trainingData.score ??
            null,

          training_time:
            trainingData.training_time ??
            null,

          rows:
            trainingData.rows ??
            null,

          features:
            trainingData.features ||
            [],

          target:
            trainingData.target ||
            null,

          results:
            Array.isArray(
              trainingData.results
            )
              ? trainingData.results
              : [],

          accuracy:
            evaluationData.accuracy ??
            null,

          precision:
            evaluationData.precision ??
            null,

          recall:
            evaluationData.recall ??
            null,

          f1_score:
            evaluationData.f1_score ??
            null,

          confusion_matrix:
            Array.isArray(
              evaluationData.confusion_matrix
            )
              ? evaluationData.confusion_matrix
              : [],

        };


        setMessages((prev) => [

          ...prev,

          {
            id:
              Date.now() +
              Math.random(),

            sender: "assistant",

            type: "model",

            text:
              "Machine learning model trained and evaluated successfully.",

            data:
              combinedData,

          },

        ]);

        return;

      }


      // =================================================
      // PROCESS RESPONSES
      // =================================================

      for (
        const response
        of backendResponses
      ) {

        const data =
          response?.data;


        // ===============================================
        // CODE RESPONSE
        // ===============================================

        if (
          isCodeResponse(
            response,
            completedTasks
          )
        ) {

          const codeData =
            extractCodeData(
              response,
              completedTasks
            );


          // ---------------------------------------------
          // ACTUAL CODE EXISTS
          // ---------------------------------------------

          if (
            codeData.code
          ) {

            setMessages((prev) => [

              ...prev,

              {
                id:
                  Date.now() +
                  Math.random(),

                sender: "assistant",

                type: "code",

                text: "",

                data:
                  codeData,

              },

            ]);

          } else {

            // -------------------------------------------
            // EXPLANATION ONLY
            // -------------------------------------------

            setMessages((prev) => [

              ...prev,

              {
                id:
                  Date.now() +
                  Math.random(),

                sender: "assistant",

                type: "text",

                text:
                  codeData.explanation ||
                  (
                    typeof data === "string"
                      ? data
                      : "No response received."
                  ),

                data: null,

              },

            ]);

          }

          continue;

        }


        // ===============================================
        // CHART
        // ===============================================

        const chartUrl =
          extractChartUrl(
            data
          );


        // ===============================================
        // ANALYSIS
        // ===============================================

        const analysis =
          isAnalysisResponse(
            data
          );


        let type =
          "text";


        if (analysis) {

          type =
            "analysis";

        } else if (chartUrl) {

          type =
            "chart";

        }


        // ===============================================
        // RESPONSE TEXT
        // ===============================================

        let responseText =
          "";

        if (
          typeof data === "string"
        ) {

          responseText =
            data;

        } else {

          responseText =
            response?.message ||
            "";

        }


        // ===============================================
        // ADD RESPONSE
        // ===============================================

        setMessages((prev) => [

          ...prev,

          {
            id:
              Date.now() +
              Math.random(),

            sender: "assistant",

            type,

            text:
              responseText,

            url:
              chartUrl,

            chartType:
              data?.chart_type ||
              null,

            data:
              data ||
              null,

          },

        ]);

      }

    } catch (error) {

      console.error(
        "Chat request failed:",
        error
      );

      setMessages((prev) => [

        ...prev,

        {
          id:
            Date.now() +
            Math.random(),

          sender: "assistant",

          type: "error",

          text:
            error?.message ||
            "Unable to contact the server.",

          data: null,

        },

      ]);

    } finally {

      setLoading(false);

    }

  };


  // =====================================================
  // QUICK-START PROMPT
  // =====================================================

  const handleSuggestion = (
    prompt
  ) => {

    if (
      !prompt ||
      loading
    ) {
      return;
    }

    setMessage(prompt);

  };


  // =====================================================
  // QUICK-START EVENT
  // =====================================================

  useEffect(() => {

    const handlePromptEvent = (event) => {

      const prompt =
        event?.detail;

      if (
        typeof prompt !== "string" ||
        !prompt.trim() ||
        loading
      ) {
        return;
      }

      handleSuggestion(
        prompt.trim()
      );

    };


    window.addEventListener(
      "datanova:prompt",
      handlePromptEvent
    );


    return () => {

      window.removeEventListener(
        "datanova:prompt",
        handlePromptEvent
      );

    };

  }, [loading]);


  // =====================================================
  // ENTER KEY
  // =====================================================

  const handleKeyDown = (
    event
  ) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      handleSend();

    }

  };


  // =====================================================
  // OPEN FILE PICKER
  // =====================================================

  const openFilePicker = () => {

    if (loading) {
      return;
    }

    fileInputRef.current?.click();

  };


  // =====================================================
  // RENDER
  // =====================================================

  return (

    <div className="border-t border-slate-200 bg-white p-6">

      <div className="mx-auto max-w-4xl">

        {/* =================================================
            DATASET PREPARATION LOADER
        ================================================= */}

        {loading && uploadStage && (

          <div className="mb-4 overflow-hidden rounded-2xl border border-blue-100 bg-gradient-to-br from-blue-50 via-white to-white p-4 shadow-sm">

            <div className="flex items-center gap-3">

              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white">

                {uploadProgress >= 100 ? (
                  <CheckCircle2 size={20} />
                ) : (
                  <LoaderCircle
                    size={20}
                    className="animate-spin"
                  />
                )}

              </div>

              <div className="min-w-0 flex-1">

                <div className="flex items-center justify-between gap-3">

                  <div className="flex items-center gap-2">

                    <Sparkles
                      size={14}
                      className="text-blue-600"
                    />

                    <p className="text-sm font-bold text-slate-800">

                      {uploadStage}

                    </p>

                  </div>

                  <span className="text-[11px] font-bold text-blue-600">

                    {uploadProgress}%

                  </span>

                </div>

                <p className="mt-1 text-[11px] text-slate-500">

                  DataNova AI is preparing your dataset for analysis.

                </p>

              </div>

            </div>


            {/* Progress */}

            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-blue-100">

              <div
                className="h-full rounded-full bg-blue-600 transition-all duration-500"
                style={{
                  width: `${uploadProgress}%`,
                }}
              />

            </div>


            {/* Stages */}

            <div className="mt-4 grid grid-cols-4 gap-2">

              {[
                {
                  label: "Upload",
                  progress: 8,
                },
                {
                  label: "Read",
                  progress: 28,
                },
                {
                  label: "Profile",
                  progress: 52,
                },
                {
                  label: "AI Ready",
                  progress: 76,
                },
              ].map((stage) => {

                const completed =
                  uploadProgress >= stage.progress;

                return (

                  <div
                    key={stage.label}
                    className="flex items-center gap-1.5"
                  >

                    <div
                      className={`flex h-4 w-4 items-center justify-center rounded-full ${
                        completed
                          ? "bg-blue-600 text-white"
                          : "bg-slate-200 text-slate-400"
                      }`}
                    >

                      {completed ? (
                        <CheckCircle2 size={11} />
                      ) : (
                        <span className="text-[8px]">
                          •
                        </span>
                      )}

                    </div>

                    <span
                      className={`text-[9px] font-semibold ${
                        completed
                          ? "text-blue-600"
                          : "text-slate-400"
                      }`}
                    >
                      {stage.label}
                    </span>

                  </div>

                );

              })}

            </div>

          </div>

        )}


        {/* =================================================
            HIDDEN FILE INPUT
        ================================================= */}

        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".csv,.xlsx,.xls,.json"
          onChange={handleUpload}
          disabled={loading}
        />


        {/* =================================================
            CHAT INPUT
        ================================================= */}

        <div className="flex items-center rounded-2xl border border-slate-300 bg-white px-4 py-3 shadow-sm transition-all focus-within:border-blue-300 focus-within:shadow-md">

          {/* Upload */}

          <button
            type="button"
            onClick={openFilePicker}
            disabled={loading}
            className="text-slate-500 transition hover:text-blue-600 disabled:opacity-40"
            title="Upload dataset"
          >

            <Paperclip size={22} />

          </button>


          {/* Text */}

          <input
            type="text"

            placeholder={
              loading
                ? "Preparing your dataset..."
                : "Ask anything about your dataset or code..."
            }

            value={message}

            onChange={(event) =>
              setMessage(
                event.target.value
              )
            }

            onKeyDown={
              handleKeyDown
            }

            disabled={loading}

            className="mx-4 flex-1 bg-transparent text-sm text-slate-800 outline-none placeholder:text-slate-400 disabled:opacity-50"
          />


          {/* Voice */}

          <button
            type="button"
            disabled={loading}
            className="mr-3 text-slate-500 transition hover:text-blue-600 disabled:opacity-40"
            title="Voice input"
          >

            <Mic size={20} />

          </button>


          {/* Send */}

          <button
            type="button"

            onClick={
              handleSend
            }

            disabled={
              loading ||
              !message.trim()
            }

            className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"

            title="Send"
          >

            {loading ? (

              <LoaderCircle
                size={17}
                className="animate-spin"
              />

            ) : (

              <SendHorizontal
                size={18}
              />

            )}

          </button>

        </div>


        {/* =================================================
            QUICK ACTIONS
        ================================================= */}

        <div className="mt-4 flex flex-wrap gap-2">

          <button
            type="button"
            onClick={openFilePicker}
            disabled={loading}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-[11px] font-medium text-slate-500 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-600 disabled:opacity-40"
          >
            CSV
          </button>


          <button
            type="button"
            onClick={openFilePicker}
            disabled={loading}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-[11px] font-medium text-slate-500 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-600 disabled:opacity-40"
          >
            Excel
          </button>


          <button
            type="button"
            onClick={openFilePicker}
            disabled={loading}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-[11px] font-medium text-slate-500 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-600 disabled:opacity-40"
          >
            JSON
          </button>


          <button
            type="button"
            disabled={loading}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-[11px] font-medium text-slate-500 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-600 disabled:opacity-40"
          >

            <Database size={13} />

            SQL

          </button>


          <button
            type="button"
            onClick={openFilePicker}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-[11px] font-medium text-slate-500 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-600 disabled:opacity-40"
          >

            <FileSpreadsheet size={13} />

            Sample Dataset

          </button>

        </div>

      </div>

    </div>

  );

}