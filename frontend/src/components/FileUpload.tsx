
import { useRef, useState } from "react";

import {
  CloudUpload,
  FileText,
  X
} from "lucide-react";

interface FileUploadProps {
  file: File | null;
  disabled?: boolean;
  onFileChange: (file: File | null) => void;
  onError: (message: string) => void;
}

export default function FileUpload({
  file,
  disabled = false,
  onFileChange,
  onError
}: FileUploadProps) {

  const inputRef = useRef<HTMLInputElement>(null);

  const [dragging, setDragging] = useState(false);

  const validateFile = (selectedFile: File) => {

    if (!selectedFile.name.toLowerCase().endsWith(".docx")) {
      onError("Chỉ hỗ trợ file Word định dạng .docx.");
      return;
    }

    if (selectedFile.size === 0) {
      onError("File Word không có nội dung.");
      return;
    }

    if (selectedFile.size > 20 * 1024 * 1024) {
      onError("Dung lượng file không được vượt quá 20 MB.");
      return;
    }

    onError("");
    onFileChange(selectedFile);
  };

  const formatSize = (bytes: number) => {

    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }

    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  return (

    <div>

      <input
        ref={inputRef}
        type="file"
        accept=".docx"
        className="hidden"
        disabled={disabled}
        onChange={(e) => {

          const selected = e.target.files?.[0];

          if (selected) {
            validateFile(selected);
          }

          e.target.value = "";
        }}
      />

      <div

        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragging(true);
        }}

        onDragLeave={() => setDragging(false)}

        onDrop={(e) => {

          e.preventDefault();
          setDragging(false);

          if (disabled) return;

          const selected = e.dataTransfer.files[0];

          if (selected) {
            validateFile(selected);
          }
        }}

        className={`
          border-2 border-dashed rounded-2xl
          p-12 text-center transition
          ${dragging
            ? "border-blue-500 bg-blue-950/30"
            : "border-slate-700 bg-slate-900"
          }
        `}
      >

        <CloudUpload
          size={56}
          className="mx-auto text-blue-400 mb-5"
        />

        <h3 className="text-xl font-semibold mb-2">
          Drag & Drop Your Document
        </h3>

        <p className="text-slate-400 mb-6">
          Kéo thả tài liệu Word hoặc chọn file từ máy tính
        </p>

        <button
          type="button"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
          className="
            bg-blue-600 hover:bg-blue-500
            px-6 py-3 rounded-xl
            font-medium disabled:opacity-50
          "
        >
          Browse Files
        </button>

        <p className="mt-5 text-sm text-slate-500">
          Supported: DOCX · Maximum 20 MB
        </p>

      </div>

      {file && (

        <div className="
          flex items-center gap-4
          bg-slate-900 border border-slate-800
          rounded-xl p-5 mt-5
        ">

          <FileText
            size={38}
            className="text-blue-400 shrink-0"
          />

          <div className="flex-1 min-w-0">

            <p className="font-medium break-all">
              {file.name}
            </p>

            <p className="text-sm text-slate-400">
              {formatSize(file.size)}
            </p>

          </div>

          <button
            type="button"
            disabled={disabled}
            title="Remove file"
            onClick={() => onFileChange(null)}
            className="text-slate-400 hover:text-red-400 disabled:opacity-50"
          >
            <X size={22} />
          </button>

        </div>

      )}

    </div>

  );
}
