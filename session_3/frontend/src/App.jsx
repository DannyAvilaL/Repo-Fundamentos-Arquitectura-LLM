import { useState, useEffect } from "react";

const API_BASE = "/api";

const COLOR_TIPO = {
  directo: { bg: "bg-blue-950/40", border: "border-blue-500/50", text: "text-blue-300", dot: "bg-blue-400" },
  hyperscaler: { bg: "bg-purple-950/40", border: "border-purple-500/50", text: "text-purple-300", dot: "bg-purple-400" },
  "self-hosted": { bg: "bg-emerald-950/40", border: "border-emerald-500/50", text: "text-emerald-300", dot: "bg-emerald-400" },
};

function SelectorProveedores({ proveedores, seleccionados, onToggle }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {proveedores.map((p) => {
        const colores = COLOR_TIPO[p.tipo] || COLOR_TIPO.directo;
        const activo = seleccionados.includes(p.id);
        return (
          <button
            key={p.id}
            onClick={() => onToggle(p.id)}
            className={`text-left rounded-lg border p-3 transition ${
              activo ? `${colores.bg} ${colores.border}` : "bg-slate-900/40 border-slate-700/50"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className={`text-sm font-semibold ${activo ? colores.text : "text-slate-400"}`}>
                {p.nombre}
              </span>
              <span className={`h-2 w-2 rounded-full ${p.configurado ? colores.dot : "bg-slate-600"}`} />
            </div>
            <div className="mt-1 text-xs text-slate-500">
              {p.tipo} · {p.configurado ? "credenciales OK" : "sin configurar (simulado)"}
            </div>
          </button>
        );
      })}
    </div>
  );
}

function TarjetaResultado({ resultado, esMasRapido }) {
  const proveedorLower = resultado.proveedor.toLowerCase();
  let tipo = "directo";
  if (proveedorLower.includes("azure") || proveedorLower.includes("bedrock") || proveedorLower.includes("vertex")) {
    tipo = "hyperscaler";
  } else if (proveedorLower.includes("ollama")) {
    tipo = "self-hosted";
  }
  const colores = COLOR_TIPO[tipo];

  return (
    <div className={`rounded-xl border p-4 ${colores.bg} ${colores.border} ${esMasRapido ? "ring-2 ring-yellow-400/60" : ""}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className={`font-bold ${colores.text}`}>{resultado.proveedor}</h3>
        {esMasRapido && <span className="text-xs font-semibold text-yellow-300">⚡ Más rápido</span>}
      </div>

      <div className="flex flex-wrap gap-3 text-xs text-slate-400 mb-3">
        <span>⏱ {resultado.latencia_seg.toFixed(2)}s</span>
        {resultado.costo_estimado_usd != null && (
          <span>💰 ${resultado.costo_estimado_usd.toFixed(5)}</span>
        )}
        {resultado.simulado && <span className="text-yellow-400">⚠ MODO SIMULADO</span>}
        {resultado.error && <span className="text-red-400">❌ Error</span>}
      </div>

      <p className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
        {resultado.error ? resultado.error : resultado.respuesta}
      </p>
    </div>
  );
}

export default function App() {
  const [proveedores, setProveedores] = useState([]);
  const [seleccionados, setSeleccionados] = useState([]);
  const [prompt, setPrompt] = useState(
    "¿Cuáles son los 3 factores más importantes al elegir un proveedor de inferencia LLM para producción?"
  );
  const [resultados, setResultados] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/proveedores`)
      .then((r) => r.json())
      .then((data) => {
        setProveedores(data);
        setSeleccionados(data.map((p) => p.id));
      })
      .catch(() => setError("No se pudo conectar al backend. ¿Está corriendo uvicorn en :8000?"));
  }, []);

  const toggleProveedor = (id) => {
    setSeleccionados((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));
  };

  const compararProveedores = async () => {
    if (!prompt.trim() || seleccionados.length === 0) return;
    setCargando(true);
    setError(null);
    setResultados(null);
    try {
      const resp = await fetch(`${API_BASE}/comparar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, proveedores: seleccionados }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      setResultados(await resp.json());
    } catch (e) {
      setError(`Error al comparar: ${e.message}`);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-5">
        <h1 className="text-2xl font-bold">🔀 Comparador de Proveedores de Inferencia</h1>
        <p className="text-sm text-slate-400 mt-1">
          Sesión 3 · BSG Institute — Directo vs Hyperscaler vs Self-Hosted, en paralelo
        </p>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        <section>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
            1. Selecciona proveedores a comparar
          </h2>
          <SelectorProveedores proveedores={proveedores} seleccionados={seleccionados} onToggle={toggleProveedor} />
        </section>

        <section>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">2. Prompt de prueba</h2>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            className="w-full rounded-lg bg-slate-900 border border-slate-700 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={compararProveedores}
            disabled={cargando || seleccionados.length === 0}
            className="mt-3 px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed font-semibold text-sm transition"
          >
            {cargando ? "Comparando en paralelo..." : `Comparar (${seleccionados.length} proveedores)`}
          </button>
        </section>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        {resultados && (
          <section>
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">3. Resultados</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {resultados.resultados.map((r) => (
                <TarjetaResultado key={r.proveedor} resultado={r} esMasRapido={r.proveedor === resultados.proveedor_mas_rapido} />
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="text-center text-xs text-slate-600 py-6">
        BSG Institute · Fundamentos de Arquitectura LLM · Sesión 3
      </footer>
    </div>
  );
}
