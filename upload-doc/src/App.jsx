import { useRef, useState } from "react";

export default function App() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  };

  const handleSelect = (e) => {
    const selected = e.target.files[0];
    if (selected) setFile(selected);
  };

  const handleUpload = async () => {
    if (!file) return;

    //Envoi API à ajouter
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
            style={{ ...styles.button, ...(file ? {} : styles.buttonDisabled) }}
            onClick={handleUpload}
            disabled={!file}
          >
            Envoyer le document
          </button>
        </div>
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
};