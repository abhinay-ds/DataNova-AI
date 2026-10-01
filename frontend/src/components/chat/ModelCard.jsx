import {
  BrainCircuit,
  CheckCircle,
  Target,
  Grid2X2,
  Trophy,
  Clock3,
  Database,
} from "lucide-react";

export default function ModelCard({ data }) {
  if (!data) return null;

  const model =
    data.best_model ||
    data.model ||
    "Trained Model";

  const problemType =
    data.problem_type ||
    "classification";

  const accuracy = data.accuracy;
  const precision = data.precision;
  const recall = data.recall;
  const f1 = data.f1_score;

  const confusionMatrix =
    Array.isArray(data.confusion_matrix)
      ? data.confusion_matrix
      : [];

  const results =
    Array.isArray(data.results)
      ? data.results
      : [];

  return (
    <div className="mt-4 w-full max-w-3xl space-y-4">

      {/* ================================================= */}
      {/* MODEL HEADER */}
      {/* ================================================= */}

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

        <div className="flex items-start justify-between">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-blue-50 p-3">
              <BrainCircuit
                size={24}
                className="text-blue-600"
              />
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900">
                Machine Learning Model
              </h3>

              <p className="text-sm text-slate-500">
                {formatLabel(problemType)}
              </p>
            </div>

          </div>

          <div className="flex items-center gap-1 rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
            <CheckCircle size={14} />
            Completed
          </div>

        </div>


        {/* Best Model */}

        <div className="mt-5 rounded-xl bg-slate-50 p-4">

          <div className="flex items-center gap-3">

            <Trophy
              size={21}
              className="text-blue-600"
            />

            <div>

              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Best Model
              </p>

              <p className="mt-1 text-xl font-bold text-slate-900">
                {model}
              </p>

            </div>

          </div>

        </div>

      </div>


      {/* ================================================= */}
      {/* PERFORMANCE */}
      {/* ================================================= */}

      {problemType === "classification" &&
        accuracy !== undefined && (

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-5 flex items-center gap-2">

            <Target
              size={20}
              className="text-blue-600"
            />

            <h3 className="font-semibold text-slate-900">
              Classification Performance
            </h3>

          </div>


          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">

            <Metric
              label="Accuracy"
              value={formatPercentage(accuracy)}
              highlight
            />

            <Metric
              label="Precision"
              value={formatPercentage(precision)}
            />

            <Metric
              label="Recall"
              value={formatPercentage(recall)}
            />

            <Metric
              label="F1 Score"
              value={formatPercentage(f1)}
            />

          </div>

        </div>
      )}


      {/* ================================================= */}
      {/* CONFUSION MATRIX */}
      {/* ================================================= */}

      {confusionMatrix.length > 0 && (

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-5 flex items-center gap-2">

            <Grid2X2
              size={20}
              className="text-blue-600"
            />

            <div>

              <h3 className="font-semibold text-slate-900">
                Confusion Matrix
              </h3>

              <p className="text-xs text-slate-500">
                Actual vs predicted classifications
              </p>

            </div>

          </div>


          <div className="flex justify-center">

            <table className="border-collapse text-center">

              <tbody>

                {confusionMatrix.map(
                  (row, rowIndex) => (

                    <tr key={rowIndex}>

                      {row.map(
                        (value, columnIndex) => (

                          <td
                            key={columnIndex}
                            className={`
                              min-w-24
                              border
                              border-slate-200
                              px-6
                              py-4
                              text-lg
                              font-bold
                              ${
                                rowIndex ===
                                  columnIndex
                                  ? "bg-blue-50 text-blue-700"
                                  : "bg-slate-50 text-slate-800"
                              }
                            `}
                          >
                            {value}
                          </td>

                        )
                      )}

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        </div>
      )}


      {/* ================================================= */}
      {/* MODEL COMPARISON */}
      {/* ================================================= */}

      {results.length > 0 && (

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-5 flex items-center gap-2">

            <Trophy
              size={20}
              className="text-blue-600"
            />

            <div>

              <h3 className="font-semibold text-slate-900">
                Model Comparison
              </h3>

              <p className="text-xs text-slate-500">
                Performance of trained models
              </p>

            </div>

          </div>


          <div className="overflow-x-auto">

            <table className="min-w-full text-sm">

              <thead>

                <tr className="border-b border-slate-200">

                  <th className="px-3 py-3 text-left font-semibold text-slate-600">
                    Model
                  </th>

                  <th className="px-3 py-3 text-right font-semibold text-slate-600">
                    Accuracy
                  </th>

                  <th className="px-3 py-3 text-right font-semibold text-slate-600">
                    Precision
                  </th>

                  <th className="px-3 py-3 text-right font-semibold text-slate-600">
                    Recall
                  </th>

                  <th className="px-3 py-3 text-right font-semibold text-slate-600">
                    F1
                  </th>

                  <th className="px-3 py-3 text-right font-semibold text-slate-600">
                    CV
                  </th>

                </tr>

              </thead>


              <tbody>

                {results.map(
                  (result, index) => {

                    const isBest =
                      result.model === model;

                    return (

                      <tr
                        key={index}
                        className={`
                          border-b
                          border-slate-100
                          ${
                            isBest
                              ? "bg-blue-50"
                              : "hover:bg-slate-50"
                          }
                        `}
                      >

                        <td className="px-3 py-3">

                          <div className="flex items-center gap-2">

                            {isBest && (
                              <CheckCircle
                                size={15}
                                className="text-green-600"
                              />
                            )}

                            <span className="font-medium text-slate-800">
                              {result.model}
                            </span>

                          </div>

                        </td>


                        <td className="px-3 py-3 text-right font-semibold">
                          {formatPercentage(
                            result.accuracy
                          )}
                        </td>


                        <td className="px-3 py-3 text-right">
                          {formatPercentage(
                            result.precision
                          )}
                        </td>


                        <td className="px-3 py-3 text-right">
                          {formatPercentage(
                            result.recall
                          )}
                        </td>


                        <td className="px-3 py-3 text-right">
                          {formatPercentage(
                            result.f1
                          )}
                        </td>


                        <td className="px-3 py-3 text-right">
                          {formatPercentage(
                            result.cross_validation
                          )}
                        </td>

                      </tr>

                    );
                  }
                )}

              </tbody>

            </table>

          </div>

        </div>
      )}


      {/* ================================================= */}
      {/* TRAINING INFORMATION */}
      {/* ================================================= */}

      {(data.rows ||
        data.training_time ||
        data.target) && (

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <h3 className="mb-4 font-semibold text-slate-900">
            Training Information
          </h3>


          <div className="grid grid-cols-2 gap-3 md:grid-cols-3">

            {data.rows && (
              <Info
                icon={<Database size={17} />}
                label="Training Rows"
                value={data.rows}
              />
            )}


            {data.target && (
              <Info
                icon={<Target size={17} />}
                label="Target"
                value={data.target}
              />
            )}


            {data.training_time !== null &&
              data.training_time !== undefined && (

              <Info
                icon={<Clock3 size={17} />}
                label="Training Time"
                value={`${data.training_time}s`}
              />

            )}

          </div>

        </div>
      )}

    </div>
  );
}


/* ===================================================== */
/* Metric */
/* ===================================================== */

function Metric({
  label,
  value,
  highlight = false,
}) {

  return (

    <div
      className={`
        rounded-xl
        p-4
        ${
          highlight
            ? "bg-blue-50"
            : "bg-slate-50"
        }
      `}
    >

      <p className="text-xs font-medium text-slate-500">
        {label}
      </p>

      <p
        className={`
          mt-1
          text-2xl
          font-bold
          ${
            highlight
              ? "text-blue-700"
              : "text-slate-900"
          }
        `}
      >
        {value}
      </p>

    </div>

  );
}


/* ===================================================== */
/* Info */
/* ===================================================== */

function Info({
  icon,
  label,
  value,
}) {

  return (

    <div className="rounded-xl bg-slate-50 p-3">

      <div className="flex items-center gap-2 text-slate-500">

        {icon}

        <span className="text-xs">
          {label}
        </span>

      </div>

      <p className="mt-1 font-semibold text-slate-900">
        {value}
      </p>

    </div>

  );
}


/* ===================================================== */
/* Formatting */
/* ===================================================== */

function formatPercentage(value) {

  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "-";
  }

  return `${(
    Number(value) * 100
  ).toFixed(2)}%`;
}


function formatLabel(value) {

  return String(value)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}