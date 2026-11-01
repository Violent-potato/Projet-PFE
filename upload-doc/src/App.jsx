import { useRef, useState } from "react";

export default function App() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

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

  const handleUpload = async () => {
    if (!file || isUploading) return;

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
    <main style={styles.page}>
      <section style={styles.container}>
        <h1 style={styles.title}>Importer un document</h1>

        <div
          style={{
            ...styles.box,
            ...styles.dropzone,
            ...(isDragging ? styles.dropzoneActive : {}),
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && inputRef.current.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleSelect}
            style={{ display: "none" }}
          />
          {file ? (
            <p style={styles.fileName}>{file.name}</p>
          ) : (
            <p style={styles.hint}>
              Glissez un document ici ou cliquez pour le choisir
            </p>
          )}
        </div>

        {/* Pour la partie API */}
        <div style={{ ...styles.box, ...styles.uploadBox }}>
          <button
            style={{
              ...styles.button,
              ...(file && !isUploading ? {} : styles.buttonDisabled),
            }}
            onClick={handleUpload}
            disabled={!file || isUploading}
          >
            {isUploading ? "Extraction en cours..." : "Envoyer le document"}
          </button>
        </div>
        {error && (
          <p role="alert" style={styles.error}>
            {error}
          </p>
        )}
        {result && (
          <div style={{ ...styles.box, ...styles.result }}>
            <p>
              {result.format} · {result.character_count} caractères
              {result.page_count != null && ` · ${result.page_count} page(s)`}
            </p>
            {result.warnings.map((warning) => (
              <p key={warning} style={styles.warning}>
                {warning}
              </p>
            ))}
            <pre style={styles.extractedText}>{result.text}</pre>
          </div>
        )}
      </section>
    </main>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f3f5f8",
    fontFamily: "system-ui, sans-serif",
    color: "#1c2333",
  },
  container: {
    width: "100%",
    maxWidth: 520,
    padding: 24,
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  title: { margin: 0, fontSize: 24, fontWeight: 600 },
  box: { borderRadius: 12, background: "#fff" },
  dropzone: {
    height: 200,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    border: "2px dashed #b9c2d3",
    cursor: "pointer",
    textAlign: "center",
    padding: 16,
    transition: "border-color 0.15s, background 0.15s",
  },
  dropzoneActive: { borderColor: "#2b4fd8", background: "#eef2ff" },
  hint: { margin: 0, color: "#5b667d" },
  fileName: { margin: 0, fontWeight: 600, wordBreak: "break-all" },
  uploadBox: {
    padding: 16,
    border: "1px solid #dde2ec",
    display: "flex",
    justifyContent: "center",
  },
  button: {
    padding: "10px 20px",
    border: "none",
    borderRadius: 8,
    background: "#2b4fd8",
    color: "#fff",
    fontSize: 16,
    cursor: "pointer",
  },
  buttonDisabled: { background: "#b9c2d3", cursor: "not-allowed" },
  error: { color: "#b42318" },
  result: { padding: 16, border: "1px solid #dde2ec", textAlign: "left" },
  warning: { color: "#8a5a00" },
  extractedText: {
    maxHeight: 360,
    overflow: "auto",
    whiteSpace: "pre-wrap",
    overflowWrap: "anywhere",
  },
};