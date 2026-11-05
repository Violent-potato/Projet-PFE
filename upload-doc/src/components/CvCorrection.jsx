
import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function CvCorrection() {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState("fr");
  const [corrections, setCorrections] = useState([]);
  const [accepted, setAccepted] = useState({});
  const [correctedText, setCorrectedText] = useState("");
  const [rewrites, setRewrites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function checkGrammar() {
    if (!text.trim()) {
      setError("Veuillez saisir le texte du CV.");
      return;
    }

    setLoading(true);
    setError("");
    setCorrectedText("");
    setRewrites([]);

    try {
      const response = await fetch(`${API_URL}/correction/grammar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Erreur API");

      setCorrections(data.corrections);
      setAccepted({});
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function applyCorrections() {
    const selected = corrections.filter((item) => accepted[item.id]);

    if (selected.length === 0) {
      setError("Choisissez au moins une correction à appliquer.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/correction/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_text: text,
          corrections,
          accepted_suggestions: accepted,
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Erreur API");

      setCorrectedText(data.corrected_text);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function rewriteProfessionally() {
    const sourceText = correctedText || text;

    if (!sourceText.trim()) {
      setError("Aucun texte à reformuler.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/correction/rewrite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: sourceText, language }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Erreur API");

      setRewrites(data.suggestions);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 850, margin: "40px auto", padding: 20 }}>
      <h1>Correction et amélioration du CV</h1>

      <label>Langue du CV</label>
      <select value={language} onChange={(e) => setLanguage(e.target.value)}>
        <option value="fr">Français</option>
        <option value="en">Anglais</option>
      </select>

      <h3>Texte extrait du CV</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Collez ici le texte extrait de votre CV..."
        rows={9}
        style={{ width: "100%", padding: 12, boxSizing: "border-box" }}
      />

      <button onClick={checkGrammar} disabled={loading}>
        {loading ? "Analyse en cours..." : "Détecter les erreurs"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {corrections.length > 0 && (
        <section>
          <h2>Suggestions de correction ({corrections.length})</h2>

          {corrections.map((item) => (
            <article
              key={item.id}
              style={{ border: "1px solid #ddd", padding: 14, marginBottom: 12 }}
            >
              <p><strong>Texte détecté :</strong> {item.original}</p>
              <p><strong>Explication :</strong> {item.message}</p>

              <label>Choisir une correction :</label>
              <select
                value={accepted[item.id] || ""}
                onChange={(e) =>
                  setAccepted((previous) => ({
                    ...previous,
                    [item.id]: e.target.value,
                  }))
                }
              >
                <option value="">Ignorer cette erreur</option>
                {item.suggestions.map((suggestion, index) => (
                  <option key={index} value={suggestion}>
                    {suggestion}
                  </option>
                ))}
              </select>
            </article>
          ))}

          <button onClick={applyCorrections} disabled={loading}>
            Appliquer les corrections sélectionnées
          </button>
        </section>
      )}

      {correctedText && (
        <section>
          <h2>Texte corrigé</h2>
          <textarea
            value={correctedText}
            readOnly
            rows={8}
            style={{ width: "100%", padding: 12, boxSizing: "border-box" }}
          />
          <button onClick={rewriteProfessionally} disabled={loading}>
            Proposer une reformulation professionnelle
          </button>
        </section>
      )}

      {rewrites.map((item, index) => (
        <article
          key={index}
          style={{ border: "1px solid #ddd", padding: 14, marginTop: 15 }}
        >
          <h3>Proposition de reformulation</h3>
          <p><strong>Original :</strong> {item.original}</p>
          <p><strong>Proposition :</strong> {item.rewritten}</p>
          <p><strong>Explication :</strong> {item.explanation}</p>
        </article>
      ))}
    </main>
  );
}
