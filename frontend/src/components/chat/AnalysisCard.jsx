import { useState } from "react";

import {
  Database,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Lightbulb,
  Table2,
  Hash,
  Type,
  FileText,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Link2,
} from "lucide-react";

export default function AnalysisCard({ data }) {

  const [showAllInsights, setShowAllInsights] =
    useState(false);

  if (!data) return null;

  // =========================================================
  // MAIN DATA
  // =========================================================

  const overview = data.overview || {};

  const quality = data.quality || {};

  const insights = Array.isArray(data.insights)
    ? data.insights
    : [];

  const recommendations = Array.isArray(data.recommendations)
    ? data.recommendations
    : [];
  // =========================================================
  // PROFILE
  // =========================================================

  const profile =
    data.profile ||
    data.dataset_profile ||
    data.detailed_profile ||
    {};

  const profileColumns = Array.isArray(profile.columns)
    ? profile.columns
    : [];

  const numerical =
    profile.numerical ||
    profile.numeric ||
    profile.numeric_summary ||
    profile.statistics?.numeric ||
    {};

  const categorical =
    profile.categorical ||
    profile.categorical_summary ||
    profile.statistics?.categorical ||
    {};

  // =========================================================
  // TABLE DATA
  // =========================================================

  const columnRows = buildColumnRows(
    profile,
    profileColumns,
    data
  );

  const numericalRows = buildNumericalRows(
    numerical
  );

  const categoricalRows = buildCategoricalRows(
    categorical
  );



  const visibleInsights = showAllInsights
    ? insights
    : insights.slice(0, 7);

  // =========================================================
  // QUALITY
  // =========================================================

  const qualityScore =
    Number(quality.score);

  const qualityIsGood =
    !Number.isNaN(qualityScore) &&
    qualityScore >= 80;

  const qualityIsWarning =
    !Number.isNaN(qualityScore) &&
    qualityScore >= 60 &&
    qualityScore < 80;

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="mt-4 w-full space-y-4">

      {/* ================================================= */}
      {/* DATASET OVERVIEW */}
      {/* ================================================= */}

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

        <div className="mb-4 flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
            <Database
              size={20}
              className="text-blue-600"
            />
          </div>

          <div>
            <h3 className="font-semibold text-slate-900">
              Dataset Overview
            </h3>

            <p className="text-xs text-slate-500">
              Summary of the uploaded dataset
            </p>
          </div>

        </div>

        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">

          <Stat
            label="Rows"
            value={
              overview.rows ??
              profile.shape?.rows ??
              "-"
            }
          />

          <Stat
            label="Columns"
            value={
              overview.columns ??
              profile.shape?.columns ??
              "-"
            }
          />

          <Stat
            label="Missing Values"
            value={
              overview.missing_values_total ??
              data.missing_values_total ??
              "-"
            }
            warning={
              Number(
                overview.missing_values_total ??
                data.missing_values_total ??
                0
              ) > 0
            }
          />

          <Stat
            label="Duplicate Rows"
            value={
              overview.duplicate_rows ??
              "-"
            }
          />

        </div>
      </section>

      {/* ================================================= */}
      {/* DATA QUALITY */}
      {/* ================================================= */}

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

        <div className="mb-4 flex items-center gap-3">

          <div
            className={`flex h-10 w-10 items-center justify-center rounded-xl ${
              qualityIsGood
                ? "bg-green-50"
                : qualityIsWarning
                ? "bg-orange-50"
                : "bg-red-50"
            }`}
          >

            {qualityIsGood ? (
              <CheckCircle
                size={20}
                className="text-green-600"
              />
            ) : (
              <AlertTriangle
                size={20}
                className={
                  qualityIsWarning
                    ? "text-orange-500"
                    : "text-red-500"
                }
              />
            )}

          </div>

          <div>
            <h3 className="font-semibold text-slate-900">
              Data Quality
            </h3>

            <p className="text-xs text-slate-500">
              Overall quality assessment
            </p>
          </div>

        </div>

        <div className="flex items-end gap-3">

          <span className="text-4xl font-bold text-slate-900">
            {quality.score ?? "-"}
          </span>

          {quality.score !== undefined && (
            <span className="mb-1 text-sm text-slate-500">
              / 100
            </span>
          )}

        </div>

        {quality.score !== undefined && (
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">

            <div
              className={`h-full rounded-full transition-all ${
                qualityIsGood
                  ? "bg-green-500"
                  : qualityIsWarning
                  ? "bg-orange-500"
                  : "bg-red-500"
              }`}
              style={{
                width: `${Math.min(
                  100,
                  Math.max(
                    0,
                    qualityScore || 0
                  )
                )}%`,
              }}
            />

          </div>
        )}

        {quality.rating && (
          <div className="mt-3 flex items-center gap-2 text-sm">

            <span className="text-slate-500">
              Rating:
            </span>

            <span
              className={`font-semibold ${
                qualityIsGood
                  ? "text-green-600"
                  : qualityIsWarning
                  ? "text-orange-600"
                  : "text-red-600"
              }`}
            >
              {quality.rating}
            </span>

          </div>
        )}

      </section>

      {/* ================================================= */}
      {/* KEY INSIGHTS */}
      {/* ================================================= */}

      {insights.length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-4 flex items-center justify-between">

            <div className="flex items-center gap-3">

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
                <Lightbulb
                  size={20}
                  className="text-blue-600"
                />
              </div>

              <div>
                <h3 className="font-semibold text-slate-900">
                  Key Insights
                </h3>

                <p className="text-xs text-slate-500">
                  Important patterns detected in your dataset
                </p>
              </div>

            </div>

            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
              {insights.length}
            </span>

          </div>

          <div className="space-y-2">

            {visibleInsights.map(
              (insight, index) => (
                <InsightItem
                  key={index}
                  value={insight}
                />
              )
            )}

          </div>

          {insights.length > 7 && (
            <button
              type="button"
              onClick={() =>
                setShowAllInsights(
                  !showAllInsights
                )
              }
              className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl border border-slate-200 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900"
            >

              {showAllInsights ? (
                <>
                  <ChevronUp size={16} />
                  Show fewer insights
                </>
              ) : (
                <>
                  <ChevronDown size={16} />
                  Show {insights.length - 7} more insights
                </>
              )}

            </button>
          )}

        </section>
      )}

      {/* ================================================= */}
      {/* RECOMMENDATIONS */}
      {/* ================================================= */}

      {recommendations.length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-4 flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
              <BarChart3
                size={20}
                className="text-blue-600"
              />
            </div>

            <div>
              <h3 className="font-semibold text-slate-900">
                Recommendations
              </h3>

              <p className="text-xs text-slate-500">
                Suggested next steps for your dataset
              </p>
            </div>

          </div>

          <div className="space-y-2">

            {recommendations.map(
              (recommendation, index) => (
                <RecommendationItem
                  key={index}
                  value={recommendation}
                />
              )
            )}

          </div>

        </section>
      )}

      {/* ================================================= */}
      {/* DETAILED DATASET PROFILE */}
      {/* ================================================= */}

      {columnRows.length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-5 flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
              <Table2
                size={20}
                className="text-blue-600"
              />
            </div>

            <div>
              <h3 className="font-semibold text-slate-900">
                Detailed Dataset Profile
              </h3>

              <p className="text-xs text-slate-500">
                Column structure and data quality
              </p>
            </div>

          </div>

          <div className="max-h-80 overflow-auto rounded-xl border border-slate-200">

            <table className="min-w-full text-sm">

              <thead className="sticky top-0 z-10">

                <tr className="bg-slate-50">

                  <th className="px-4 py-3 text-left font-semibold text-slate-600">
                    Column
                  </th>

                  <th className="px-4 py-3 text-left font-semibold text-slate-600">
                    Type
                  </th>

                  <th className="px-4 py-3 text-right font-semibold text-slate-600">
                    Missing
                  </th>

                  <th className="px-4 py-3 text-right font-semibold text-slate-600">
                    Unique
                  </th>

                </tr>

              </thead>

              <tbody>

                {columnRows.map(
                  (column, index) => {

                    const missing =
                      Number(
                        column.missing ?? 0
                      );

                    return (
                      <tr
                        key={index}
                        className="border-t border-slate-100 transition hover:bg-slate-50"
                      >

                        <td className="px-4 py-3 font-medium text-slate-800">

                          <div className="flex items-center gap-2">

                            {isNumericType(
                              column.type
                            ) ? (
                              <Hash
                                size={15}
                                className="text-blue-500"
                              />
                            ) : (
                              <Type
                                size={15}
                                className="text-slate-400"
                              />
                            )}

                            {column.name}

                          </div>

                        </td>

                        <td className="px-4 py-3 text-slate-500">
                          {column.type || "-"}
                        </td>

                        <td className="px-4 py-3 text-right">

                          <span
                            className={
                              missing > 0
                                ? "rounded-md bg-orange-50 px-2 py-1 font-semibold text-orange-600"
                                : "text-slate-500"
                            }
                          >
                            {column.missing ?? 0}
                          </span>

                        </td>

                        <td className="px-4 py-3 text-right text-slate-500">
                          {column.unique ?? "-"}
                        </td>

                      </tr>
                    );
                  }
                )}

              </tbody>

            </table>

          </div>

        </section>
      )}

      {/* ================================================= */}
      {/* NUMERICAL STATISTICS */}
      {/* ================================================= */}

      {numericalRows.length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-5 flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
              <Hash
                size={20}
                className="text-blue-600"
              />
            </div>

            <div>
              <h3 className="font-semibold text-slate-900">
                Numerical Summary
              </h3>

              <p className="text-xs text-slate-500">
                Statistical summary of numerical columns
              </p>
            </div>

          </div>

          <div className="max-h-80 overflow-auto rounded-xl border border-slate-200">

            <table className="min-w-full text-sm">

              <thead className="sticky top-0 z-10">

                <tr className="bg-slate-50">

                  <th className="px-4 py-3 text-left font-semibold text-slate-600">
                    Column
                  </th>

                  <th className="px-4 py-3 text-right font-semibold text-slate-600">
                    Mean
                  </th>

                  <th className="px-4 py-3 text-right font-semibold text-slate-600">
                    Median
                  </th>

                  <th className="px-4 py-3 text-right font-semibold text-slate-600">
                    Min
                  </th>

                  <th className="px-4 py-3 text-right font-semibold text-slate-600">
                    Max
                  </th>

                </tr>

              </thead>

              <tbody>

                {numericalRows.map(
                  (row, index) => (

                    <tr
                      key={index}
                      className="border-t border-slate-100 transition hover:bg-slate-50"
                    >

                      <td className="px-4 py-3 font-medium text-slate-800">
                        {row.name}
                      </td>

                      <td className="px-4 py-3 text-right text-slate-600">
                        {formatNumber(row.mean)}
                      </td>

                      <td className="px-4 py-3 text-right text-slate-600">
                        {formatNumber(row.median)}
                      </td>

                      <td className="px-4 py-3 text-right text-slate-600">
                        {formatNumber(row.min)}
                      </td>

                      <td className="px-4 py-3 text-right text-slate-600">
                        {formatNumber(row.max)}
                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        </section>
      )}

      {/* ================================================= */}
      {/* CATEGORICAL STATISTICS */}
      {/* ================================================= */}

      {categoricalRows.length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="mb-5 flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
              <Type
                size={20}
                className="text-blue-600"
              />
            </div>

            <div>
              <h3 className="font-semibold text-slate-900">
                Categorical Summary
              </h3>

              <p className="text-xs text-slate-500">
                Overview of categorical columns
              </p>
            </div>

          </div>

          <div className="space-y-2">

            {categoricalRows.map(
              (row, index) => (

                <div
                  key={index}
                  className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3"
                >

                  <div className="flex items-center gap-2">

                    <FileText
                      size={16}
                      className="text-slate-400"
                    />

                    <span className="font-medium text-slate-800">
                      {row.name}
                    </span>

                  </div>

                  <span className="text-sm text-slate-500">

                    {row.unique !== undefined &&
                    row.unique !== null
                      ? `${row.unique} unique`
                      : ""}

                  </span>

                </div>

              )
            )}

          </div>

        </section>
      )}

    </div>
  );
}


/* =========================================================
   STAT
========================================================= */

function Stat({
  label,
  value,
  warning = false,
}) {
  return (
    <div
      className={`rounded-xl p-3 ${
        warning
          ? "bg-orange-50"
          : "bg-slate-50"
      }`}
    >

      <p
        className={`text-xs ${
          warning
            ? "text-orange-600"
            : "text-slate-500"
        }`}
      >
        {label}
      </p>

      <p
        className={`mt-1 text-xl font-bold ${
          warning
            ? "text-orange-700"
            : "text-slate-900"
        }`}
      >
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   INSIGHT
========================================================= */

function InsightItem({ value }) {

  const text =
    typeof value === "string"
      ? value
      : value?.message ||
        value?.text ||
        JSON.stringify(value);

  const lower =
    text.toLowerCase();

  const isWarning =
    lower.includes("missing") ||
    lower.includes("outlier") ||
    lower.includes("skewed");

  const isRelationship =
    lower.includes("correlation") ||
    lower.includes("relationship");

  const isBinary =
    lower.includes("binary") ||
    lower.includes("categories");

  let containerClass =
    "border-slate-100 bg-slate-50";

  let dotClass =
    "bg-blue-600";

  let Icon = Lightbulb;

  let iconClass =
    "text-blue-600";

  if (isWarning) {

    containerClass =
      "border-orange-100 bg-orange-50/60";

    dotClass =
      "bg-orange-500";

    Icon = AlertCircle;

    iconClass =
      "text-orange-500";

  } else if (isRelationship) {

    containerClass =
      "border-purple-100 bg-purple-50/60";

    dotClass =
      "bg-purple-500";

    Icon = Link2;

    iconClass =
      "text-purple-500";

  } else if (isBinary) {

    containerClass =
      "border-blue-100 bg-blue-50/60";

    dotClass =
      "bg-blue-500";
  }

  return (
    <div
      className={`flex gap-3 rounded-xl border p-3 ${containerClass}`}
    >

      <div className="mt-0.5 shrink-0">

        <Icon
          size={15}
          className={iconClass}
        />

      </div>

      <p className="text-sm leading-5 text-slate-700">
        {text}
      </p>

    </div>
  );
}


/* =========================================================
   RECOMMENDATION
========================================================= */

function RecommendationItem({
  value,
}) {

  const text =
    typeof value === "string"
      ? value
      : value?.message ||
        value?.text ||
        JSON.stringify(value);

  return (
    <div className="flex gap-3 rounded-xl border border-green-100 bg-green-50/50 p-3">

      <div className="mt-0.5 shrink-0">

        <CheckCircle
          size={16}
          className="text-green-600"
        />

      </div>

      <p className="text-sm leading-5 text-slate-700">
        {text}
      </p>

    </div>
  );
}


/* =========================================================
   BUILD COLUMN ROWS
========================================================= */

function buildColumnRows(
  profile,
  profileColumns,
  data
) {

  const missingValues =
    data?.overview?.missing_values ||
    data?.missing_values ||
    profile?.missing_values ||
    {};

  // -------------------------------------------------------
  // Backend returns detailed objects
  // -------------------------------------------------------

  if (
    profileColumns.length > 0 &&
    typeof profileColumns[0] === "object"
  ) {

    return profileColumns.map(
      (column) => ({

        name:
          column.name ||
          column.column ||
          column.column_name ||
          "-",

        type:
          column.type ||
          column.dtype ||
          column.data_type ||
          "-",

        missing:
          column.missing ??
          column.missing_values ??
          0,

        unique:
          column.unique ??
          column.unique_values ??
          column.nunique ??
          "-",

      })
    );
  }

  // -------------------------------------------------------
  // Backend returns column names
  // -------------------------------------------------------

  if (
    profileColumns.length > 0
  ) {

    return profileColumns.map(
      (column) => ({

        name: String(column),

        type:
          profile?.dtypes?.[column] ||
          profile?.data_types?.[column] ||
          "-",

        missing:
          missingValues?.[column] ??
          0,

        unique:
          profile?.unique_values?.[column] ??
          profile?.nunique?.[column] ??
          "-",

      })
    );
  }

  // -------------------------------------------------------
  // Fallback
  // -------------------------------------------------------

  const names =
    Array.isArray(
      data?.column_names
    )
      ? data.column_names
      : [];

  return names.map(
    (column) => ({

      name: String(column),

      type:
        profile?.dtypes?.[column] ||
        "-",

      missing:
        missingValues?.[column] ??
        0,

      unique:
        profile?.unique_values?.[column] ??
        "-",

    })
  );
}


/* =========================================================
   BUILD NUMERICAL ROWS
========================================================= */

function buildNumericalRows(
  numerical
) {

  if (!numerical) {
    return [];
  }

  // -------------------------------------------------------
  // Array format
  // -------------------------------------------------------

  if (
    Array.isArray(numerical)
  ) {

    return numerical.map(
      (item) => ({

        name:
          item.name ||
          item.column ||
          "-",

        mean:
          item.mean,

        median:
          item.median ??
          item["50%"],

        min:
          item.min ??
          item.minimum,

        max:
          item.max ??
          item.maximum,

      })
    );
  }

  // -------------------------------------------------------
  // Object format
  // -------------------------------------------------------

  if (
    typeof numerical === "object"
  ) {

    return Object.entries(
      numerical
    ).map(
      ([name, values]) => {

        if (
          typeof values !== "object" ||
          values === null
        ) {

          return {
            name,
            mean: values,
            median: undefined,
            min: undefined,
            max: undefined,
          };
        }

        return {

          name,

          mean:
            values.mean ??
            values["mean"],

          median:
            values.median ??
            values["50%"],

          min:
            values.min ??
            values.minimum,

          max:
            values.max ??
            values.maximum,

        };
      }
    );
  }

  return [];
}


/* =========================================================
   BUILD CATEGORICAL ROWS
========================================================= */

function buildCategoricalRows(
  categorical
) {

  if (!categorical) {
    return [];
  }

  // -------------------------------------------------------
  // Array format
  // -------------------------------------------------------

  if (
    Array.isArray(categorical)
  ) {

    return categorical.map(
      (item) => ({

        name:
          item.name ||
          item.column ||
          "-",

        unique:
          item.unique ??
          item.unique_values ??
          item.nunique,

      })
    );
  }

  // -------------------------------------------------------
  // Object format
  // -------------------------------------------------------

  if (
    typeof categorical === "object"
  ) {

    return Object.entries(
      categorical
    ).map(
      ([name, values]) => ({

        name,

        unique:
          typeof values === "object" &&
          values !== null
            ? (
                values.unique ??
                values.unique_values ??
                values.nunique
              )
            : values,

      })
    );
  }

  return [];
}


/* =========================================================
   NUMBER FORMAT
========================================================= */

function formatNumber(
  value
) {

  if (
    value === null ||
    value === undefined ||
    value === "-"
  ) {
    return "-";
  }

  const number =
    Number(value);

  if (
    Number.isNaN(number)
  ) {
    return value;
  }

  return number.toLocaleString(
    undefined,
    {
      maximumFractionDigits: 2,
    }
  );
}


/* =========================================================
   NUMERIC TYPE
========================================================= */

function isNumericType(
  type
) {

  if (!type) {
    return false;
  }

  const value =
    String(type)
      .toLowerCase();

  return (
    value.includes("int") ||
    value.includes("float") ||
    value.includes("double") ||
    value.includes("number")
  );
}