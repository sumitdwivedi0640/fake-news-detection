function getPredictionClasses(prediction) {
  return prediction === "REAL"
    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
    : "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300";
}

function confidencePct(confidence) {
  return Math.max(0, Math.min(100, Math.round((confidence || 0) * 100)));
}

function highlightText(sourceText, importantWords) {
  if (!sourceText || !importantWords?.length) return sourceText;
  const escaped = importantWords.map((word) => word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const regex = new RegExp(`\\b(${escaped.join("|")})\\b`, "gi");
  return sourceText.split(regex).map((part, idx) => {
    const matched = importantWords.some((word) => word.toLowerCase() === part.toLowerCase());
    if (matched) {
      return (
        <mark key={idx} className="rounded bg-amber-200 px-1 text-slate-900">
          {part}
        </mark>
      );
    }
    return <span key={idx}>{part}</span>;
  });
}

export default function ResultCard({ data }) {
  const percentage = confidencePct(data.confidence);

  return (
    <section className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Analysis Result</h2>
        <span className={`rounded-full px-4 py-1 text-sm font-semibold ${getPredictionClasses(data.prediction)}`}>
          {data.prediction}
        </span>
      </div>

      <div>
        <p className="mb-2 text-sm text-slate-600 dark:text-slate-300">Confidence: {percentage}%</p>
        <div className="h-3 w-full rounded-full bg-slate-200 dark:bg-slate-700">
          <div className="h-3 rounded-full bg-indigo-500 transition-all" style={{ width: `${percentage}%` }} />
        </div>
      </div>

      <div>
        <h3 className="mb-2 font-medium text-slate-900 dark:text-slate-100">Evidence</h3>
        <ul className="list-disc space-y-1 pl-5 text-slate-700 dark:text-slate-300">
          {(data.evidence || []).length ? (
            data.evidence.map((item, idx) => <li key={idx}>{item}</li>)
          ) : (
            <li>No external evidence found.</li>
          )}
        </ul>
      </div>

      <div>
        <h3 className="mb-2 font-medium text-slate-900 dark:text-slate-100">Explanation</h3>
        <p className="whitespace-pre-wrap text-slate-700 dark:text-slate-300">{data.explanation}</p>
      </div>

      <div>
        <h3 className="mb-2 font-medium text-slate-900 dark:text-slate-100">SHAP Important Words</h3>
        <div className="flex flex-wrap gap-2">
          {(data.shap?.important_words || []).map((word, idx) => (
            <span
              key={`${word}-${idx}`}
              className="rounded-md border border-slate-300 bg-slate-100 px-2 py-1 text-xs text-slate-800 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
            >
              {word}: {(data.shap?.weights?.[idx] || 0).toFixed(4)}
            </span>
          ))}
        </div>
      </div>

      <div>
        <h3 className="mb-2 font-medium text-slate-900 dark:text-slate-100">Highlighted Source Text</h3>
        <p className="rounded-xl bg-slate-50 p-4 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
          {highlightText(data.source_text, data.shap?.important_words || [])}
        </p>
      </div>
    </section>
  );
}
