import { useEffect, useState } from "react";
import { analyzeNews, analyzeUrl } from "./api";
import ResultCard from "./components/ResultCard";

export default function App() {
  const [newsInput, setNewsInput] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [mode, setMode] = useState("text");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  async function handleAnalyze() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = mode === "text" ? await analyzeNews(newsInput) : await analyzeUrl(urlInput);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Request failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const inputValue = mode === "text" ? newsInput : urlInput;

  return (
    <div className="min-h-screen bg-slate-100 px-4 py-8 dark:bg-slate-950">
      <div className="mx-auto max-w-4xl space-y-6">
        <header className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Fake News AI Assistant</h1>
          <button
            onClick={() => setDarkMode((prev) => !prev)}
            className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white"
          >
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </header>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4 flex gap-2">
            <button
              onClick={() => setMode("text")}
              className={`rounded-lg px-3 py-2 text-sm ${mode === "text" ? "bg-indigo-600 text-white" : "bg-slate-200 dark:bg-slate-700 dark:text-slate-100"}`}
            >
              Analyze Text
            </button>
            <button
              onClick={() => setMode("url")}
              className={`rounded-lg px-3 py-2 text-sm ${mode === "url" ? "bg-indigo-600 text-white" : "bg-slate-200 dark:bg-slate-700 dark:text-slate-100"}`}
            >
              Analyze URL
            </button>
          </div>

          {mode === "text" ? (
            <textarea
              value={newsInput}
              onChange={(e) => setNewsInput(e.target.value)}
              rows={6}
              placeholder="Paste suspicious news text here..."
              className="w-full rounded-xl border border-slate-300 bg-slate-50 p-4 text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            />
          ) : (
            <input
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://example.com/article"
              className="w-full rounded-xl border border-slate-300 bg-slate-50 p-4 text-slate-900 outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            />
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading || !inputValue.trim()}
            className="mt-4 w-full rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:bg-indigo-300"
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>
          {loading && <p className="mt-3 text-center text-sm text-slate-600 dark:text-slate-300">Loading model + evidence + explanation...</p>}
          {error && <p className="mt-3 rounded-md bg-rose-100 p-3 text-sm text-rose-700 dark:bg-rose-900/40 dark:text-rose-300">{error}</p>}
        </section>

        {result && <ResultCard data={result} />}
      </div>
    </div>
  );
}
