import { useState } from "react";

import {
  Copy,
  Check,
  Code2,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";


export default function CodeCard({ data }) {

  const [copied, setCopied] =
    useState(false);


  // =====================================================
  // GET CODE
  // =====================================================

  const code =

    data?.code ||

    data?.generated_code ||

    data?.content ||

    data?.output ||

    "";


  // =====================================================
  // GET EXPLANATION
  // =====================================================

  let explanation =
    data?.explanation ||
    "";


  // Remove unnecessary markdown wrapper labels
  explanation = explanation
    .replace(/^Explanation\s*:?\s*/i, "")
    .trim();


  // =====================================================
  // DETECT LANGUAGE
  // =====================================================

  let language =

    data?.language ||

    data?.code_language ||

    "";


  // Detect language if backend does not send it

  if (
    !language &&
    typeof code === "string"
  ) {

    const sqlKeywords = [

      "SELECT",

      "INSERT",

      "UPDATE",

      "DELETE",

      "CREATE TABLE",

      "DROP TABLE",

      "ALTER TABLE",

      "FROM ",

      "WHERE ",

      "JOIN ",

    ];


    const upperCode =
      code.trim().toUpperCase();


    const isSQL =
      sqlKeywords.some(
        (keyword) =>
          upperCode.includes(keyword)
      );


    language =
      isSQL
        ? "sql"
        : "python";

  }


  // Final fallback

  language =
    language || "python";


  // =====================================================
  // COPY CODE
  // =====================================================

  const handleCopy =
    async () => {

      if (!code) {
        return;
      }


      try {

        await navigator.clipboard.writeText(
          code
        );


        setCopied(true);


        setTimeout(() => {

          setCopied(false);

        }, 2000);


      } catch (error) {

        console.error(
          "Failed to copy code:",
          error
        );

      }

    };


  // =====================================================
  // NO CODE
  // =====================================================

  if (!code) {

    return (

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">

        <div className="flex items-center gap-3">

          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400">

            <Code2 size={20} />

          </div>


          <div>

            <h3 className="font-semibold text-slate-800 dark:text-slate-100">

              Generated Code

            </h3>


            <p className="text-sm text-slate-500 dark:text-slate-400">

              No code content was returned.

            </p>

          </div>

        </div>

      </div>

    );

  }


  // =====================================================
  // CODE CARD
  // =====================================================

  return (

    <div className="w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">


      {/* HEADER */}

      <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-800 dark:bg-slate-900/60">


        <div className="flex items-center gap-3">

          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400">

            <Code2 size={20} />

          </div>


          <div>

            <h3 className="font-semibold text-slate-800 dark:text-slate-100">

              Generated Code

            </h3>


            <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">

              {language}

            </p>

          </div>

        </div>


        {/* COPY BUTTON */}

        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
        >

          {copied ? (

            <>

              <Check size={16} />

              Copied

            </>

          ) : (

            <>

              <Copy size={16} />

              Copy

            </>

          )}

        </button>

      </div>


      {/* CODE */}

      <div className="max-h-[480px] overflow-auto bg-slate-950 p-4 font-mono">

        <pre className="min-w-full whitespace-pre text-xs leading-5 text-slate-100 sm:text-sm sm:leading-6">

          <code>{code}</code>

        </pre>

      </div>


      {/* EXPLANATION */}

      {explanation && (

        <div className="border-t border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-900/40 dark:text-slate-300">

          <p className="mb-2 font-semibold text-slate-700 dark:text-slate-200">

            Explanation

          </p>


          <ReactMarkdown
            remarkPlugins={[
              remarkGfm,
            ]}
            components={{

              p: ({
                children,
              }) => (

                <p className="mb-3 last:mb-0">

                  {children}

                </p>

              ),


              ul: ({
                children,
              }) => (

                <ul className="mb-3 list-disc space-y-1 pl-5">

                  {children}

                </ul>

              ),


              ol: ({
                children,
              }) => (

                <ol className="mb-3 list-decimal space-y-1 pl-5">

                  {children}

                </ol>

              ),


              strong: ({
                children,
              }) => (

                <strong className="font-semibold text-slate-900 dark:text-slate-100">

                  {children}

                </strong>

              ),


              code: ({
                children,
              }) => (

                <code className="rounded border border-transparent bg-slate-200 px-1.5 py-0.5 font-mono text-xs text-slate-800 dark:border-slate-700/60 dark:bg-slate-800 dark:text-blue-300">

                  {children}

                </code>

              ),

            }}
          >

            {explanation}

          </ReactMarkdown>

        </div>

      )}

    </div>

  );

}