import { useState, useEffect } from "react";

const API = "http://localhost:8000";

// ── Colores por proveedor ──────────────────────────────────────────────────
const COLORES = {
  openai   : "border-green-500 bg-green-50 dark:bg-green-950",
  anthropic: "border-orange-500 bg-orange-50 dark:bg-orange-950",
  google   : "border-blue-500 bg-blue-50 dark:bg-blue-950",
  "ollama/local": "border-purple-500 bg-purple-50 dark:bg-purple-950",
  ollama   : "border-purple-500 bg-purple-50 dark:bg-purple-950",
};

const BADGE = {
  openai   : "bg-green-100 text-green-800",
  anthropic: "bg-orange-100 text-orange-800",
  google   : "bg-blue-100 text-blue-800",
  "ollama/local": "bg-purple-100 text-purple-800",
  ollama   : "bg-purple-100 text-purple-800",
};

const PROMPTS_EJEMPLO = [
  "Explica en 3 puntos que es un LLM y para que sirve en empresas.",
  "Cuales son las diferencias entre modelos propietarios y open-source?",
  "Dame un ejemplo de uso de LLMs en atencion al cliente.",
  "Como se calcula el costo de uso de un LLM por API?",
];

// ── Componente: Tarjeta de resultado ──────────────────────────────────────
function TarjetaModelo({ resultado, index }) {
  if (!resultado) return null;
  const colorClass = COLORES[resultado.proveedor] || "border-gray-300 bg-gray-50";
  const badgeClass = BADGE[resultado.proveedor] || "bg-gray-100 text-gray-800";
  const tps = resultado.tiempo_ms > 0 && resultado.tokens?.salida > 0
    ? Math.round(resultado.tokens.salida / (resultado.tiempo_ms / 1000))
    : 0;

  return (
    <div className={`border-2 rounded-xl p-4 flex flex-col gap-2 ${colorClass}`}>
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <span className="font-bold text-gray-900 dark:text-white">{resultado.modelo}</span>
          <span className={`ml-2 text-xs font-medium px-2 py-0.5 rounded-full ${badgeClass}`}>
            {resultado.proveedor}
          </span>
        </div>
        <div className="flex gap-3 text-xs text-gray-500">
          <span>{resultado.tiempo_ms}ms</span>
          {tps > 0 && <span>{tps} tok/s</span>}
          {resultado.tokens?.salida > 0 && (
            <span>{resultado.tokens.entrada}+{resultado.tokens.salida} tokens</span>
          )}
        </div>
      </div>

      {/* Respuesta */}
      {resultado.error ? (
        <div className="text-red-600 text-sm bg-red-50 rounded-lg p-3">
          Error: {resultado.error}
        </div>
      ) : (
        <p className="text-gray-800 dark:text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">
          {resultado.texto}
        </p>
      )}
    </div>
  );
}

// ── Componente: Selector de modelos ───────────────────────────────────────
function SelectorModelos({ modelos, seleccionados, onChange }) {
  const todos = [...(modelos.cloud || []), ...(modelos.local || [])];

  return (
    <div className="flex flex-wrap gap-2">
      {todos.map((m) => {
        const activo = seleccionados.includes(m.nombre);
        const badgeClass = BADGE[m.tipo === "cloud" ? m.proveedor : "ollama"] || "bg-gray-100 text-gray-700";
        return (
          <button
            key={m.nombre}
            onClick={() => {
              if (activo) onChange(seleccionados.filter((n) => n !== m.nombre));
              else onChange([...seleccionados, m.nombre]);
            }}
            disabled={!m.disponible}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border-2 transition-all
              ${activo
                ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                : m.disponible
                  ? "border-gray-200 bg-white text-gray-600 hover:border-gray-400"
                  : "border-gray-100 bg-gray-50 text-gray-300 cursor-not-allowed"
              }`}
          >
            {m.nombre}
            <span className={`ml-1.5 text-xs px-1 rounded ${badgeClass}`}>
              {m.tipo}
            </span>
            {!m.disponible && <span className="ml-1 text-xs">✗</span>}
          </button>
        );
      })}
    </div>
  );
}

// ── App principal ─────────────────────────────────────────────────────────
export default function App() {
  const [prompt, setPrompt]               = useState("");
  const [modelos, setModelos]             = useState({ cloud: [], local: [] });
  const [seleccionados, setSeleccionados] = useState([]);
  const [resultados, setResultados]       = useState([]);
  const [cargando, setCargando]           = useState(false);
  const [error, setError]                 = useState("");
  const [tiempoTotal, setTiempoTotal]     = useState(0);

  // Cargar lista de modelos al iniciar
  useEffect(() => {
    fetch(`${API}/modelos`)
      .then((r) => r.json())
      .then((data) => {
        setModelos(data);
        // Preseleccionar primer modelo local disponible
        const disponibles = [...(data.local || []), ...(data.cloud || [])].filter((m) => m.disponible);
        if (disponibles.length > 0) setSeleccionados([disponibles[0].nombre]);
      })
      .catch(() => {
        // Fallback si el backend no esta corriendo
        const fallback = {
          cloud: [{ nombre: "gpt-4o-mini", tipo: "cloud", proveedor: "openai", disponible: false, descripcion: "Requiere OPENAI_API_KEY" }],
          local: [{ nombre: "llama3.2", tipo: "local", proveedor: "ollama", disponible: true, descripcion: "Requiere Ollama corriendo" }],
        };
        setModelos(fallback);
        setSeleccionados(["llama3.2"]);
      });
  }, []);

  const comparar = async () => {
    if (!prompt.trim()) { setError("Escribe un prompt primero."); return; }
    if (seleccionados.length === 0) { setError("Selecciona al menos un modelo."); return; }

    setCargando(true);
    setError("");
    setResultados([]);
    setTiempoTotal(0);

    try {
      const resp = await fetch(`${API}/comparar`, {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({ prompt, modelos: seleccionados }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setResultados(data.resultados);
      setTiempoTotal(data.tiempo_total_ms);
    } catch (e) {
      setError(`Error al conectar con el backend: ${e.message}. ¿Esta corriendo uvicorn?`);
    } finally {
      setCargando(false);
    }
  };

  const usarEjemplo = (texto) => {
    setPrompt(texto);
    setResultados([]);
  };

  // Calcular el modelo mas rapido
  const masRapido = resultados.length > 1
    ? resultados.reduce((a, b) => (a.tiempo_ms < b.tiempo_ms && !a.error ? a : b))
    : null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-white">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-4">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold text-indigo-600">Comparador de Modelos LLM</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Sesion 2 — Propietarios vs Open-Source · BSG Institute
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 flex flex-col gap-6">

        {/* Panel de configuracion */}
        <section className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 flex flex-col gap-4">
          <h2 className="font-semibold text-lg">Configuracion</h2>

          {/* Seleccion de modelos */}
          <div>
            <label className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2 block">
              Modelos a comparar
            </label>
            <SelectorModelos
              modelos={modelos}
              seleccionados={seleccionados}
              onChange={setSeleccionados}
            />
            <p className="text-xs text-gray-400 mt-1">
              Modelos sin tilde ✗ requieren API key o Ollama corriendo.
            </p>
          </div>

          {/* Prompts de ejemplo */}
          <div>
            <label className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2 block">
              Prompts de ejemplo
            </label>
            <div className="flex flex-wrap gap-2">
              {PROMPTS_EJEMPLO.map((ej) => (
                <button
                  key={ej}
                  onClick={() => usarEjemplo(ej)}
                  className="text-xs px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition-colors"
                >
                  {ej.substring(0, 45)}...
                </button>
              ))}
            </div>
          </div>

          {/* Textarea prompt */}
          <div>
            <label className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2 block">
              Tu prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => { if (e.ctrlKey && e.key === "Enter") comparar(); }}
              placeholder="Escribe tu pregunta o instruccion... (Ctrl+Enter para enviar)"
              rows={3}
              className="w-full rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
          </div>

          <button
            onClick={comparar}
            disabled={cargando || seleccionados.length === 0}
            className={`self-start px-6 py-2.5 rounded-xl font-semibold text-white transition-all
              ${cargando || seleccionados.length === 0
                ? "bg-gray-300 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-700 active:scale-95"
              }`}
          >
            {cargando ? "Comparando..." : `Comparar ${seleccionados.length} modelo${seleccionados.length !== 1 ? "s" : ""}`}
          </button>

          {error && (
            <div className="text-red-600 bg-red-50 rounded-lg px-4 py-3 text-sm">
              {error}
            </div>
          )}
        </section>

        {/* Resultados */}
        {(cargando || resultados.length > 0) && (
          <section>
            {tiempoTotal > 0 && (
              <div className="flex items-center gap-3 mb-4">
                <span className="text-sm text-gray-500">
                  {resultados.length} respuestas en {tiempoTotal}ms
                </span>
                {masRapido && (
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">
                    Mas rapido: {masRapido.modelo} ({masRapido.tiempo_ms}ms)
                  </span>
                )}
              </div>
            )}

            {cargando ? (
              <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
                {seleccionados.map((m) => (
                  <div key={m} className="border-2 border-gray-200 rounded-xl p-4 animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/3 mb-3" />
                    <div className="h-3 bg-gray-200 rounded w-full mb-2" />
                    <div className="h-3 bg-gray-200 rounded w-4/5 mb-2" />
                    <div className="h-3 bg-gray-200 rounded w-3/4" />
                  </div>
                ))}
              </div>
            ) : (
              <div className={`grid gap-4 ${resultados.length === 1 ? "" : "md:grid-cols-2"}`}>
                {resultados.map((r, i) => (
                  <TarjetaModelo key={r.modelo} resultado={r} index={i} />
                ))}
              </div>
            )}
          </section>
        )}

        {/* Estado sin resultados */}
        {!cargando && resultados.length === 0 && !error && (
          <div className="text-center py-16 text-gray-400">
            <div className="text-6xl mb-4">⚖️</div>
            <p className="text-lg font-medium">Compara modelos LLM side by side</p>
            <p className="text-sm mt-1">Selecciona modelos, escribe un prompt y presiona Comparar</p>
          </div>
        )}

        {/* Info footer */}
        <footer className="text-center text-xs text-gray-400 pt-4 border-t border-gray-200 dark:border-gray-800">
          BSG Institute · Sesion 2: Tipos de Modelos y Escenarios de Aplicacion
        </footer>
      </main>
    </div>
  );
}
