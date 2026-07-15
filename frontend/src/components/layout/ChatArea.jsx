import {
  BarChart3,
  Database,
  BrainCircuit,
  FileSpreadsheet,
  Sparkles,
} from "lucide-react";

const suggestions = [
  {
    icon: <FileSpreadsheet size={22} />,
    title: "Analyze CSV / Excel",
    description: "Upload your dataset and explore it instantly.",
  },
  {
    icon: <BarChart3 size={22} />,
    title: "Generate Visualizations",
    description: "Create charts and graphs automatically.",
  },
  {
    icon: <BrainCircuit size={22} />,
    title: "Train Machine Learning Models",
    description: "Build predictive models with one click.",
  },
  {
    icon: <Database size={22} />,
    title: "Connect SQL Database",
    description: "Analyze live database tables using AI.",
  },
];

export default function ChatArea() {
  return (
    <div className="flex-1 overflow-auto bg-slate-50 px-16 py-12">

      <div className="mx-auto max-w-4xl">

        <div className="text-center">

          <Sparkles
            className="mx-auto mb-4 text-blue-600"
            size={42}
          />

          <h1 className="text-5xl font-bold text-slate-900">
            DataNova AI
          </h1>

          <p className="mt-3 text-lg text-slate-500">
            Analyze • Visualize • Predict
          </p>

          <p className="mt-8 text-2xl font-semibold text-slate-700">
            What would you like to analyze today?
          </p>

        </div>

        <div className="mt-14 grid grid-cols-2 gap-6">

          {suggestions.map((item) => (
            <button
              key={item.title}
              className="rounded-2xl border border-slate-200 bg-white p-6 text-left shadow-sm transition hover:-translate-y-1 hover:border-blue-400 hover:shadow-lg"
            >
              <div className="mb-4 text-blue-600">
                {item.icon}
              </div>

              <h3 className="font-semibold text-lg">
                {item.title}
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                {item.description}
              </p>
            </button>
          ))}

        </div>

      </div>

    </div>
  );
}