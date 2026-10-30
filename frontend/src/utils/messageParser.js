const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const codeTasks = [
  "generate_python",
  "generate_sql",
  "explain_code",
  "optimize_code",
  "convert_code",
  "debug_code",
];

export const detectLanguageFromTasks = (completedTasks = []) => {
  const tasks = completedTasks.map((task) =>
    String(task).toLowerCase().trim()
  );

  if (tasks.includes("generate_sql")) return "sql";
  if (tasks.includes("generate_python")) return "python";
  return "";
};

export const detectLanguageFromCode = (code) => {
  if (!code || typeof code !== "string") return "text";

  const lowerCode = code.toLowerCase();
  const upperCode = code.toUpperCase();

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

  if (sqlKeywords.some((keyword) => upperCode.includes(keyword))) {
    return "sql";
  }

  if (
    lowerCode.includes("public class") ||
    lowerCode.includes("public static") ||
    lowerCode.includes("system.out.println")
  ) {
    return "java";
  }

  if (
    lowerCode.includes("#include") ||
    lowerCode.includes("using namespace std") ||
    lowerCode.includes("std::")
  ) {
    return "cpp";
  }

  if (
    lowerCode.includes("function ") ||
    lowerCode.includes("const ") ||
    lowerCode.includes("let ")
  ) {
    return "javascript";
  }

  return "python";
};

export const isCodeResponse = (response, completedTasks = []) => {
  const intent = String(response?.intent || "")
    .toLowerCase()
    .trim();

  const capability = String(response?.capability || "")
    .toLowerCase()
    .trim();

  if (codeTasks.includes(intent)) return true;
  if (codeTasks.includes(capability)) return true;

  return completedTasks.some((task) =>
    codeTasks.includes(String(task).toLowerCase().trim())
  );
};

export const extractCodeData = (response, completedTasks = []) => {
  const rawData = response?.data;

  if (rawData && typeof rawData === "object") {
    let code =
      rawData.code ||
      rawData.generated_code ||
      rawData.content ||
      rawData.output ||
      "";

    let explanation = rawData.explanation || "";

    if (typeof code === "string" && code.includes("```")) {
      const match = code.match(/```([a-zA-Z0-9+#.-]*)\s*\n?([\s\S]*?)```/i);
      if (match) {
        const beforeCode = code.slice(0, match.index || 0).trim();
        const afterCode = code.slice((match.index || 0) + match[0].length).trim();
        code = match[2]?.trim() || "";

        if (!explanation) {
          explanation = [beforeCode, afterCode]
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
        detectLanguageFromTasks(completedTasks) ||
        detectLanguageFromCode(code),
      explanation,
    };
  }

  const content = typeof rawData === "string" ? rawData.trim() : "";
  let code = "";
  let explanation = "";
  let language = detectLanguageFromTasks(completedTasks);

  const match = content.match(/```([a-zA-Z0-9+#.-]*)\s*\n?([\s\S]*?)```/i);

  if (match) {
    const detectedLanguage = match[1]?.trim().toLowerCase();
    code = match[2]?.trim() || "";
    if (detectedLanguage) language = detectedLanguage;

    const beforeCode = content.slice(0, match.index || 0).trim();
    const afterCode = content.slice((match.index || 0) + match[0].length).trim();
    explanation = [beforeCode, afterCode].filter(Boolean).join("\n\n").trim();
  } else {
    explanation = content;
  }

  return {
    code,
    language: language || detectLanguageFromCode(code),
    explanation,
  };
};

export const extractChartUrl = (data) => {
  if (!data || typeof data !== "object") return null;

  if (data.url) {
    if (data.url.startsWith("http://") || data.url.startsWith("https://")) {
      return data.url;
    }
    const cleanUrl = data.url.startsWith("/") ? data.url : `/${data.url}`;
    return `${API_BASE_URL}${cleanUrl}`;
  }

  if (!data.chart_path) return null;

  const filename = data.chart_path
    .replace(/\\/g, "/")
    .split("/")
    .pop();

  if (!filename) return null;

  return `${API_BASE_URL}/charts/${filename}`;
};

export const isAnalysisResponse = (data) => {
  if (!data || typeof data !== "object") return false;

  return Boolean(
    data.overview &&
      data.quality &&
      Array.isArray(data.insights) &&
      Array.isArray(data.recommendations)
  );
};

export const isTrainingResponse = (response) => {
  const data = response?.data;
  return Boolean(
    data &&
      typeof data === "object" &&
      (data.best_model || data.model_path || Array.isArray(data.results))
  );
};

export const isEvaluationResponse = (response) => {
  const data = response?.data;
  return Boolean(
    data &&
      typeof data === "object" &&
      (data.accuracy !== undefined ||
        data.precision !== undefined ||
        data.recall !== undefined ||
        data.f1_score !== undefined ||
        data.confusion_matrix)
  );
};

export const formatAssistantResponses = (
  backendResponses = [],
  completedTasks = [],
  baseId = Date.now()
) => {
  const results = [];

  if (!Array.isArray(backendResponses) || backendResponses.length === 0) {
    return results;
  }

  // ML Training + Evaluation combined card
  const trainingResponse = backendResponses.find(isTrainingResponse);
  const evaluationResponse = backendResponses.find(isEvaluationResponse);

  if (trainingResponse && evaluationResponse) {
    const trainingData = trainingResponse.data || {};
    const evaluationData = evaluationResponse.data || {};

    const combinedData = {
      problem_type:
        trainingData.problem_type ||
        evaluationData.problem_type ||
        "classification",
      best_model: trainingData.best_model || "Model",
      model_path: trainingData.model_path || null,
      training_score: trainingData.score ?? null,
      training_time: trainingData.training_time ?? null,
      rows: trainingData.rows ?? null,
      features: trainingData.features || [],
      target: trainingData.target || null,
      results: Array.isArray(trainingData.results) ? trainingData.results : [],
      accuracy: evaluationData.accuracy ?? null,
      precision: evaluationData.precision ?? null,
      recall: evaluationData.recall ?? null,
      f1_score: evaluationData.f1_score ?? null,
      confusion_matrix: Array.isArray(evaluationData.confusion_matrix)
        ? evaluationData.confusion_matrix
        : [],
    };

    results.push({
      id: `${baseId}_model`,
      sender: "assistant",
      type: "model",
      text: "Machine learning model trained and evaluated successfully.",
      data: combinedData,
    });

    return results;
  }

  // Process individual responses
  backendResponses.forEach((response, index) => {
    const data = response?.data;
    const msgId = `${baseId}_${index}`;

    if (isCodeResponse(response, completedTasks)) {
      const codeData = extractCodeData(response, completedTasks);

      if (codeData.code) {
        results.push({
          id: `${msgId}_code`,
          sender: "assistant",
          type: "code",
          text: "",
          data: codeData,
        });
      } else {
        results.push({
          id: `${msgId}_text`,
          sender: "assistant",
          type: "text",
          text:
            codeData.explanation ||
            (typeof data === "string" ? data : "No response received."),
          data: null,
        });
      }
      return;
    }

    const chartUrl = extractChartUrl(data);
    const analysis = isAnalysisResponse(data);

    let type = "text";
    if (analysis) {
      type = "analysis";
    } else if (chartUrl) {
      type = "chart";
    }

    let responseText = "";
    if (typeof data === "string") {
      responseText = data;
    } else {
      responseText = response?.message || "";
    }

    results.push({
      id: `${msgId}_${type}`,
      sender: "assistant",
      type,
      text: responseText,
      url: chartUrl,
      chartType: data?.chart_type || null,
      data: data || null,
    });
  });

  return results;
};

export const formatDbMessageToUi = (dbMessage) => {
  if (!dbMessage) return [];

  const role = dbMessage.role;
  const content = dbMessage.content || "";
  const messageData = dbMessage.message_data;
  const baseId = dbMessage.id;

  if (role === "user") {
    return [
      {
        id: baseId,
        sender: "user",
        type: "text",
        text: content,
        data: null,
      },
    ];
  }

  if (
    messageData &&
    typeof messageData === "object" &&
    Array.isArray(messageData.responses) &&
    messageData.responses.length > 0
  ) {
    const formatted = formatAssistantResponses(
      messageData.responses,
      messageData.completed_tasks || [],
      baseId
    );

    if (formatted.length > 0) {
      return formatted;
    }
  }

  return [
    {
      id: baseId,
      sender: "assistant",
      type: "text",
      text: content || "Response generated.",
      data: messageData || null,
    },
  ];
};
