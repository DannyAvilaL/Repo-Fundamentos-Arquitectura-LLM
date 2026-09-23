import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export function PanelEtica() {
  const [preguntas, setPreguntas] = useState([]);
  const [respuestas, setRespuestas] = useState({});
  const [resumen, setResumen] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .obtenerPreguntasChecklist()
      .then((data) => setPreguntas(data.preguntas))
      .catch((e) => setError(e.message));
  }, []);

  function actualizarRespuesta(id, campo, valor) {
    setRespuestas((prev) => ({
      ...prev,
      [id]: { ...prev[id], [campo]: valor },
    }));
  }

  async function enviarChecklist() {
    setError(null);
    try {
      const data = await api.validarChecklist(respuestas);
      setResumen(data.resumen);
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section className="panel">
      <h2>Checklist de consideraciones éticas básicas</h2>
      <p className="ayuda">
        Cada pregunta está mapeada a NIST AI RMF 1.0 o al Reglamento de IA de la UE.
        Responda todas antes de enviar — este registro debería acompañar cada corrida
        antes de aprobar el paso a producción.
      </p>

      {preguntas.map((p) => (
        <div key={p.id} className="pregunta-etica">
          <p className="pregunta-texto">{p.pregunta}</p>
          <p className="pregunta-marco">{p.marco_referencia}</p>
          <div className="opciones-respuesta">
            {["si", "parcial", "no", "no_aplica"].map((opcion) => (
              <label key={opcion} className="opcion">
                <input
                  type="radio"
                  name={p.id}
                  value={opcion}
                  checked={respuestas[p.id]?.respuesta === opcion}
                  onChange={() => actualizarRespuesta(p.id, "respuesta", opcion)}
                />
                {opcion}
              </label>
            ))}
          </div>
          <input
            type="text"
            className="justificacion"
            placeholder="Justificación breve (opcional)"
            value={respuestas[p.id]?.justificacion || ""}
            onChange={(e) => actualizarRespuesta(p.id, "justificacion", e.target.value)}
          />
        </div>
      ))}

      <button onClick={enviarChecklist} disabled={preguntas.length === 0}>
        Validar checklist
      </button>

      {error && <p className="error">⚠ {error}</p>}

      {resumen && (
        <div className={resumen.listo_para_avanzar ? "resultado-ok" : "resultado-bloqueado"}>
          <p>
            <strong>{resumen.listo_para_avanzar ? "✅ Sin bloqueantes" : "⛔ Con bloqueantes"}</strong>
          </p>
          <p>{resumen.recomendacion}</p>
          {resumen.items_bloqueantes.length > 0 && (
            <p>Ítems bloqueantes: {resumen.items_bloqueantes.join(", ")}</p>
          )}
        </div>
      )}
    </section>
  );
}
