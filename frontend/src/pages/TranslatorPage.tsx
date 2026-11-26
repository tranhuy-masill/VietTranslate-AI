
import { useState } from "react";
import axios from "axios";

import {
  Languages,
  Copy,
  Trash2,
  Cpu,
  Clock,
  SlidersHorizontal,
  LoaderCircle
} from "lucide-react";

import { translateText } from "../services/api";
import type { TranslationResponse } from "../types/translation";

export default function TranslatorPage() {

  const [text, setText] = useState("");
  const [beam, setBeam] = useState(4);
  const [maxTokens, setMaxTokens] = useState(128);

  const [result, setResult] =
    useState<TranslationResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const handleTranslate = async () => {

    if (!text.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);
    setCopied(false);

    try {

      const data = await translateText({
        text,
        beam_size: beam,
        max_new_tokens: maxTokens
      });

      setResult(data);

    } catch (err) {

      const detail = axios.isAxiosError(err)
        ? err.response?.data?.detail
        : null;

      setError(
        typeof detail === "string"
          ? detail
          : "Không thể dịch văn bản. Vui lòng kiểm tra Backend."
      );

    } finally {

      setLoading(false);

    }
  };

  const handleClear = () => {
    setText("");
    setResult(null);
    setError("");
    setCopied(false);
  };

  const handleCopy = async () => {
    if (!result) return;

    try {
      await navigator.clipboard.writeText(
        result.translated_text
      );
      setCopied(true);
    } catch {
      setError("Không thể sao chép bản dịch.");
    }
  };

  return (

    <main className="max-w-7xl mx-auto px-6 py-10">

      <h2 className="text-3xl font-bold mb-2">
        Translation Workspace
      </h2>

      <p className="text-slate-400 mb-8">
        MarianMT English–Vietnamese · SwitchOut p = 0.02
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* English Input */}

        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-5">

          <div className="flex justify-between items-center mb-4">

            <h3 className="font-semibold text-lg">
              English
            </h3>

            <button
              onClick={handleClear}
              disabled={loading}
              title="Xóa văn bản"
              className="text-slate-400 hover:text-red-400"
            >
              <Trash2 size={20} />
            </button>

          </div>

          <textarea
            value={text}
            disabled={loading}
            maxLength={5000}
            onChange={(e) => {
              setText(e.target.value);
              setResult(null);
              setCopied(false);
              setError("");
            }}
            placeholder="Enter English text..."
            className="w-full h-64 bg-slate-950 border border-slate-800 rounded-xl p-4 outline-none focus:border-blue-500 resize-y"
          />

          <p className="text-sm text-slate-500 mt-3">
            {text.length} characters
          </p>

        </section>

        {/* Vietnamese Output */}

        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-5">

          <div className="flex justify-between items-center mb-4">

            <h3 className="font-semibold text-lg">
              Tiếng Việt
            </h3>

            <button
              onClick={handleCopy}
              disabled={!result}
              title="Sao chép bản dịch"
              className="text-slate-400 hover:text-blue-400"
            >
              {copied ? "Đã sao chép" : <Copy size={20} />}
            </button>

          </div>

          <textarea
            readOnly
            value={result?.translated_text || ""}
            placeholder="Bản dịch sẽ xuất hiện ở đây..."
            className="w-full h-64 bg-slate-950 border border-slate-800 rounded-xl p-4 outline-none resize-y"
          />

          <p className="text-sm text-slate-500 mt-3">
            {result?.output_tokens || 0} output tokens
          </p>

        </section>

      </div>

      {/* Model Settings */}

      <section className="mt-6 bg-slate-900 border border-slate-800 rounded-2xl p-6">

        <div className="flex items-center gap-2 mb-6">

          <SlidersHorizontal
            className="text-blue-400"
            size={22}
          />

          <h3 className="text-xl font-semibold">
            Model Settings
          </h3>

        </div>

        <div className="grid md:grid-cols-2 gap-8">

          <div>

            <label className="flex justify-between mb-3">
              <span>Beam Size</span>
              <span className="text-blue-400">{beam}</span>
            </label>

            <input
              type="range"
              min={1}
              max={8}
              value={beam}
              disabled={loading}
              onChange={(e) => setBeam(Number(e.target.value))}
              className="w-full accent-blue-500"
            />

            <p className="text-sm text-slate-500 mt-2">
              1 = Greedy Search · 4 = Default Beam Search
            </p>

          </div>

          <div>

            <label className="flex justify-between mb-3">
              <span>Max New Tokens</span>
              <span className="text-blue-400">{maxTokens}</span>
            </label>

            <input
              type="range"
              min={32}
              max={256}
              step={16}
              value={maxTokens}
              disabled={loading}
              onChange={(e) =>
                setMaxTokens(Number(e.target.value))
              }
              className="w-full accent-blue-500"
            />

          </div>

        </div>

      </section>

      {/* Translate Button */}

      <button
        onClick={handleTranslate}
        disabled={loading || !text.trim()}
        className="mt-6 w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-xl py-4 font-semibold flex items-center justify-center gap-3 transition"
      >

        {loading ? (
          <>
            <LoaderCircle className="animate-spin" />
            Translating...
          </>
        ) : (
          <>
            <Languages size={22} />
            Translate Now
          </>
        )}

      </button>

      {error && (

        <div className="mt-4 text-red-400 bg-red-950/40 border border-red-900 p-4 rounded-xl">
          {error}
        </div>

      )}

      {/* Performance Statistics */}

      {result && (

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-6">

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">

            <Clock className="text-blue-400 mb-3" />

            <p className="text-slate-400 text-sm">
              Inference Latency
            </p>

            <h3 className="text-2xl font-bold mt-2">
              {result.latency_ms} ms
            </h3>

          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">

            <p className="text-slate-400 text-sm">
              Input Tokens
            </p>

            <h3 className="text-2xl font-bold mt-2">
              {result.input_tokens}
            </h3>

          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">

            <p className="text-slate-400 text-sm">
              Output Tokens
            </p>

            <h3 className="text-2xl font-bold mt-2">
              {result.output_tokens}
            </h3>

          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">

            <Cpu className="text-blue-400 mb-3" />

            <p className="text-slate-400 text-sm">
              Device
            </p>

            <h3 className="text-2xl font-bold mt-2">
              {result.device.toUpperCase()}
            </h3>

          </div>

        </div>

      )}

    </main>

  );
}
