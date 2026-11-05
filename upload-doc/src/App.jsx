import { useRef, useState } from "react";
import "./App.css";

//trashcan pour l'option de retirer le doc déposé
function TrashIcon({ size = 22 }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M10 11v6" />
      <path d="M14 11v6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
      <path d="M3 6h18" />
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </svg>
  );
}

const ACCEPTED_EXTENSIONS = [".pdf", ".docx"];
const FORMAT_ERROR = "Impossible d'importer le CV, format non supporté";

export default function App() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [errorKey, setErrorKey] = useState(0);

  const selectFile = (selectedFile) => {
    setFile(selectedFile);
    setError("");
    setResult(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) selectFile(dropped);
  };

  const handleSelect = (e) => {
    const selected = e.target.files[0];
    if (selected) selectFile(selected);
  };

  //option pour retirer le fichier déposé
  const removeFile = () => {
    setFile(null);
    setError("");
    setResult(null);
    if (inputRef.current) inputRef.current.value = ""; //permet de choisir le même fichier
  };

  const handleZoneAction = () =>
    file ? removeFile() : inputRef.current.click();

  const handleUpload = async () => {
    if (!file || isUploading) return;

    //Vérification du format avant envoi à l'API
    const isSupported = ACCEPTED_EXTENSIONS.some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    );
    if (!isSupported) {
      setResult(null);
      setError(FORMAT_ERROR);
      setErrorKey((k) => k + 1);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setIsUploading(true);
    setError("");
    setResult(null);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${apiUrl}/cv/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Erreur lors de l'extraction du CV.");
      }

      setResult(data);
    } catch (uploadError) {
      setError(uploadError.message || "Impossible de contacter l'API.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="cv-page">
      <section className="cv-container">
        <h1 className="cv-title">Étape 1 : importez votre CV</h1>

        <div className="cv-card">
          <div
            className={`cv-dropzone${isDragging ? " is-dragging" : ""}${
              file ? " has-file" : ""
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={handleZoneAction}
            role="button"
            aria-label={file ? "Retirer le document" : undefined}
            tabIndex={0}
            onKeyDown={(e) => e.key === "Enter" && handleZoneAction()}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.docx"
              onChange={handleSelect}
              style={{ display: "none" }}
            />
            <div>
              {file && <p className="cv-file-name">{file.name}</p>}
              <p className="cv-hint">.pdf et .docx autorisés</p>
            </div>
            {file && (
              <div className="cv-veil" aria-hidden="true">
                <TrashIcon />
                <span>Retirer le document</span>
              </div>
            )}
          </div>

          <button
            className="cv-button"
            onClick={handleUpload}
            disabled={!file || isUploading}
          >
            {isUploading ? "Importation…" : "Importer"}
          </button>

          <div className="cv-error-slot">
            {error && (
              <p key={errorKey} role="alert" className="cv-error-banner">
                {error}
              </p>
            )}
          </div>
        </div>

        {result && (
          <div className="cv-result">
            <p>
              {result.format} · {result.character_count} caractères
              {result.page_count != null && ` · ${result.page_count} page(s)`}
            </p>
            {result.warnings.map((warning) => (
              <p key={warning} className="cv-warning">
                {warning}
              </p>
            ))}
            <pre className="cv-extracted">{result.text}</pre>
          </div>
        )}
      </section>
    </main>
  );
}