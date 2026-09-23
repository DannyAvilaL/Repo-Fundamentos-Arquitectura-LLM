const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function pedir(ruta, opciones = {}) {
  const resp = await fetch(`${API_BASE}${ruta}`, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
  });
  if (!resp.ok) {
    const cuerpo = await resp.json().catch(() => ({}));
    throw new Error(cuerpo.detail || `Error HTTP ${resp.status}`);
  }
  return resp.json();
}

export const api = {
  obtenerDataset: () => pedir("/api/dataset"),
  evaluar: (proveedor, aprobado_por) =>
    pedir("/api/evaluar", {
      method: "POST",
      body: JSON.stringify({ proveedor, aprobado_por }),
    }),
  proyectarCosto: (payload) =>
    pedir("/api/costeo/proyeccion", { method: "POST", body: JSON.stringify(payload) }),
  obtenerPreguntasChecklist: () => pedir("/api/checklist/preguntas"),
  validarChecklist: (respuestas) =>
    pedir("/api/checklist/validar", {
      method: "POST",
      body: JSON.stringify({ respuestas }),
    }),
  obtenerRegistro: () => pedir("/api/registro"),
  obtenerComparativa: () => pedir("/api/registro/comparativa"),
};
