import { useState } from "react";

const API_BASE = "/api";

const PERFILES = [
  { id: "preciso", nombre: "Preciso", desc: "temperature=0.0 · clasificación, extracción, hechos", color: "blue" },
  { id: "balanceado", nombre: "Balanceado", desc: "temperature=0.7 · chatbots, soporte al cliente", color: "emerald" },
  { id: "creativo", nombre: "Creativo", desc: "temperature=1.2 · brainstorming, copywriting", color: "purple" },
];

const COLOR_MAP = {
  blue: "border-blue-500/50 bg-blue-950/40 text-blue-300",
  emerald: "border-emerald-500/50 bg-emerald-950/40 text-emerald-300",
  purple: "border-purple-500/50 bg-purple-950/40 text-purple-300",
};

function Paso({ numero, titulo, activo, completado, children }) {
  return (
    <div className={`rounded-xl border p-5 transition ${
      activo ? "border-cyan-500/60 bg-slate-900/60" : "border-slate-700/40 bg-slate-900/20"
    }`}>
      <div className="flex items-center gap-3 mb-3">
        <span className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
          completado ? "bg-emerald-500 text-slate-950" : activo ? "bg-cyan-500 text-slate-950" : "bg-slate-700 text-slate-400"
        }`}>
          {completado ? "✓" : numero}
        </span>
        <h3 className="font-semibold text-slate-100">{titulo}</h3>
      </div>
      {children}
    </div>
  );
}

export default function App() {
  const [prompt, setPrompt] = useState(
    "¿Cuál es la política de devoluciones para compras internacionales?"
  );
  const [perfil, setPerfil] = useState("preciso");
  const [grounding, setGrounding] = useState(true);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const enviarDemo = async () => {
    if (!prompt.trim()) return;
    setCargando(true);
    setError(null);
    setResultado(null);
    try {
      const resp = await fetch(`${API_BASE}/demo/completar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, perfil_parametros: perfil, usar_grounding: grounding }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      setResultado(await resp.json());
    } catch (e) {
      setError(`No se pudo conectar al backend: ${e.message}. ¿Está corriendo uvicorn en :8000?`);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-5">
        <h1 className="text-2xl font-bold">🎯 Demo Guiada de Llamada API</h1>
        <p className="text-sm text-slate-400 mt-1">
          Sesión 4 · BSG Institute — Prompt, parámetros y control de alucinación, paso a paso
        </p>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8 space-y-5">
        <Paso numero={1} titulo="El Prompt" activo completado={!!prompt}>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            className="w-full rounded-lg bg-slate-900 border border-slate-700 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </Paso>

        <Paso numero={2} titulo="Los Parámetros" activo completado={!!perfil}>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {PERFILES.map((p) => (
              <button
                key={p.id}
                onClick={() => setPerfil(p.id)}
                className={`text-left rounded-lg border p-3 transition ${
                  perfil === p.id ? COLOR_MAP[p.color] : "border-slate-700/50 bg-slate-900/40 text-slate-400"
                }`}
              >
                <div className="font-semibold text-sm">{p.nombre}</div>
                <div className="text-xs mt-1 opacity-80">{p.desc}</div>
              </button>
            ))}
          </div>
        </Paso>

        <Paso numero={3} titulo="Control de Alucinación" activo completado>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={grounding}
              onChange={(e) => setGrounding(e.target.checked)}
              className="h-4 w-4 accent-cyan-500"
            />
            <span className="text-sm">
              Activar <strong>grounding</strong> — responder solo con base en el contexto verificado de la demo
            </span>
          </label>
          {!grounding && (
            <p className="text-xs text-yellow-400 mt-2">
              ⚠ Sin grounding, el modelo puede inventar información plausible pero falsa — útil para ver el contraste.
            </p>
          )}
        </Paso>

        <Paso numero={4} titulo="Enviar al Backend" activo={!cargando} completado={!!resultado}>
          <button
            onClick={enviarDemo}
            disabled={cargando}
            className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 disabled:cursor-not-allowed font-semibold text-sm transition"
          >
            {cargando ? "Enviando..." : "POST /demo/completar"}
          </button>
          {error && <p className="text-red-400 text-sm mt-3">{error}</p>}
        </Paso>

        {resultado && (
          <Paso numero={5} titulo="Resultado" activo completado>
            <div className="flex flex-wrap gap-3 text-xs text-slate-400 mb-3">
              <span className={resultado.simulado ? "text-yellow-400" : "text-emerald-400"}>
                {resultado.simulado ? "⚠ MODO SIMULADO" : "✓ Llamada real"}
              </span>
              <span>⏱ {resultado.latencia_seg.toFixed(2)}s</span>
              <span>Perfil: {resultado.perfil_usado}</span>
              <span>Grounding: {resultado.grounding_activo ? "activo" : "inactivo"}</span>
            </div>
            <p className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed bg-slate-950/60 rounded-lg p-4 border border-slate-800">
              {resultado.respuesta}
            </p>
            {resultado.senales_alerta?.length > 0 && (
              <div className="mt-3 space-y-1">
                <p className="text-xs font-semibold text-yellow-400">⚠ Señales de alerta:</p>
                {resultado.senales_alerta.map((s, i) => (
                  <p key={i} className="text-xs text-yellow-300 pl-3">• {s}</p>
                ))}
              </div>
            )}
          </Paso>
        )}
      </main>

      <footer className="text-center text-xs text-slate-600 py-6">
        BSG Institute · Fundamentos de Arquitectura LLM · Sesión 4
      </footer>
    </div>
  );
}
