
import { useState } from "react";

import {
  FileText,
  Download,
  LoaderCircle,
  CheckCircle2,
  Clock,
  AlertCircle,
  Languages
} from "lucide-react";

import FileUpload from "../components/FileUpload";
import { translateDocument } from "../services/documentApi";

export default function DocumentPage() {

  const [file, setFile] = useState<File | null>(null);

  const [beamSize, setBeamSize] = useState(4);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [result, setResult] = useState<Blob | null>(null);

  const [outputName, setOutputName] = useState("");

  const [processingTime, setProcessingTime] = useState(0);

  const handleFileChange = (newFile: File | null) => {

    setFile(newFile);
    setResult(null);
    setOutputName("");
    setError("");
    setProcessingTime(0);
  };

  const handleTranslate = async () => {

    if (!file || loading) return;

    setLoading(true);
    setError("");
    setResult(null);
    setOutputName("");
    setProcessingTime(0);

    const startTime = performance.now();

    try {

      const translatedFile = await translateDocument(
        file,
        beamSize
      );

      const filename = file.name.replace(
        /\.docx$/i,
        "_VI.docx"
      );

      setResult(translatedFile);

      setOutputName(filename);

      setProcessingTime(
        (performance.now() - startTime) / 1000
      );

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Không thể dịch tài liệu."
      );

    } finally {

      setLoading(false);
    }
  };

  const handleDownload = () => {

    if (!result) return;

    const url = URL.createObjectURL(result);

    const link = document.createElement("a");

    link.href = url;
    link.download = outputName;

    document.body.appendChild(link);

    link.click();

    link.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  return (

    <main className="max-w-5xl mx-auto px-6 py-10">

      {/* Header */}

      <div className="flex items-center gap-4 mb-3">

        <div className="p-3 rounded-xl bg-blue-600">
          <FileText size={28} />
        </div>

        <h2 className="text-3xl font-bold">
          Document Translation
        </h2>

      </div>

      <p className="text-slate-400 mb-8">
        Translate Word documents using MarianMT
        SwitchOut p = 0.02
      </p>

      {/* Languages */}

      <div className="grid grid-cols-2 gap-4 mb-6">

        <div className="
          bg-slate-900 border border-slate-800
          rounded-xl p-5
        ">

          <p className="text-sm text-slate-400 mb-2">
            Source Language
          </p>

          <h3 className="text-xl font-semibold">
            English
          </h3>

        </div>

        <div className="
          bg-slate-900 border border-slate-800
          rounded-xl p-5
        ">

          <p className="text-sm text-slate-400 mb-2">
            Target Language
          </p>

          <h3 className="text-xl font-semibold">
            Tiếng Việt
          </h3>

        </div>

      </div>

      {/* File Upload */}

      <FileUpload
        file={file}
        disabled={loading}
        onFileChange={handleFileChange}
        onError={setError}
      />

      {/* Model Settings */}

      <div className="
        mt-6 bg-slate-900 border border-slate-800
        rounded-xl p-6
      ">

        <div className="flex justify-between mb-4">

          <span className="font-medium">
            Beam Size
          </span>

          <span className="text-blue-400 font-bold">
            {beamSize}
          </span>

        </div>

        <input
          type="range"
          min={1}
          max={8}
          value={beamSize}
          disabled={loading}
          onChange={(e) =>
            setBeamSize(Number(e.target.value))
          }
          className="w-full accent-blue-500"
        />

        <div className="
          flex justify-between
          text-sm text-slate-500 mt-2
        ">

          <span>Fastest</span>
          <span>Default: 4</span>
          <span>Wider search</span>

        </div>

      </div>

      {/* Translate Button */}

      <button

        disabled={!file || loading}

        onClick={handleTranslate}

        className="
          w-full mt-6 py-4 rounded-xl
          bg-blue-600 hover:bg-blue-500
          disabled:opacity-50
          flex items-center justify-center gap-3
          font-semibold transition
        "
      >

        {loading ? (

          <>
            <LoaderCircle className="animate-spin" />
            Translating Document...
          </>

        ) : (

          <>
            <Languages size={22} />
            Translate Document
          </>

        )}

      </button>

      {/* Processing Status */}

      {loading && (

        <div className="
          mt-6 p-6 rounded-xl
          bg-blue-950/30 border border-blue-900
        ">

          <div className="flex items-center gap-3 mb-4">

            <LoaderCircle
              className="animate-spin text-blue-400"
            />

            <p className="font-medium">
              AI is processing your document...
            </p>

          </div>

          <div className="
            w-full h-2 bg-slate-800
            rounded-full overflow-hidden
          ">

            <div className="
              w-1/3 h-full bg-blue-500
              rounded-full animate-pulse
            " />

          </div>

          <p className="text-sm text-slate-400 mt-4">
            Hệ thống đang đọc và dịch nội dung tài liệu.
            Vui lòng giữ trang này mở.
          </p>

        </div>

      )}

      {/* Error */}

      {error && (

        <div className="
          mt-5 flex items-start gap-3
          bg-red-950/40 border border-red-900
          text-red-400 p-4 rounded-xl
        ">

          <AlertCircle className="shrink-0" />

          <p>{error}</p>

        </div>

      )}

      {/* Translation Result */}

      {result && (

        <section className="
          mt-8 bg-slate-900 border border-green-900
          rounded-2xl p-6
        ">

          <div className="
            flex items-center gap-3
            text-green-400 mb-5
          ">

            <CheckCircle2 size={26} />

            <h3 className="text-xl font-semibold">
              Translation Completed
            </h3>

          </div>

          <div className="
            flex items-center gap-4
            bg-slate-950 rounded-xl p-5
          ">

            <FileText
              size={42}
              className="text-blue-400 shrink-0"
            />

            <div className="flex-1 min-w-0">

              <p className="font-semibold break-all">
                {outputName}
              </p>

              <p className="text-sm text-slate-400 mt-1">
                Vietnamese Word Document
              </p>

            </div>

          </div>

          <div className="
            flex items-center gap-2
            text-slate-400 mt-5
          ">

            <Clock size={18} />

            Processing time:
            {processingTime.toFixed(2)} seconds

          </div>

          <button

            onClick={handleDownload}

            className="
              w-full mt-6 py-4
              bg-green-600 hover:bg-green-500
              rounded-xl font-semibold
              flex items-center justify-center gap-3
            "
          >

            <Download size={22} />

            Download Translated Document

          </button>

        </section>

      )}

      {/* Information */}

      <div className="
        mt-8 p-5 rounded-xl
        border border-slate-800
        text-sm text-slate-400
      ">

        <h4 className="text-slate-200 font-semibold mb-3">
          Document Translation Information
        </h4>

        <p>• Model: MarianMT SwitchOut p = 0.02</p>
        <p>• Supported format: Microsoft Word (.docx)</p>
        <p>• Maximum file size: 20 MB</p>
        <p>• Translation direction: English → Vietnamese</p>
        <p>• Basic document structure preservation</p>

      </div>

    </main>

  );
}
