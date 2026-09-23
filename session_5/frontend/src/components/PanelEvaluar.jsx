import React, { useState } from "react";
import { api } from "../api.js";

const PROVEEDORES = ["openai", "anthropic", "google", "ollama"];

export function PanelEvaluar() {
  const [proveedor, setProveedor] = useState("ollama");
  const [aprobadoPor, setAprobadoPor] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [resultado, setResultado] = useState(null);

  async function ejecutarEvaluacion() {
    setCargando(true);
    setError(null);
    try {
      const data = await api.evaluar(proveedor, aprobadoPor || undefined);
      setResultado(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <section className="panel">
      <h2>Correr el dataset dorado contra un proveedor</h2>
      <p className="ayuda">
        Corre las 10 preguntas de soporte de "Tienda Andina" contra el proveedor
        elegido y calcula superposición léxica, cautela apropiada en preguntas de
        alto riesgo, longitud relativa y costo estimado. Sin API key configurada,
        el proveedor responde en modo simulado (ver backend/proveedores.py).
      </p>

      <div className="fila-controles">
        <label>
          Proveedor
          <select value={proveedor} onChange={(e) => setProveedor(e.target.value)}>
            {PROVEEDORES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label>
          Aprobado por (opcional)
          <input
            type="text"
            value={aprobadoPor}
            onChange={(e) => setAprobadoPor(e.target.value)}
            placeholder="nombre del responsable"
          />
        </label>
        <button onClick={ejecutarEvaluacion} disabled={cargando}>
          {cargando ? "Evaluando…" : "Ejecutar evaluación"}
        </button>
      </div>

      {error && <p className="error">⚠ {error}</p>}

      {resultado && (
        <div className="resultado">
          <div className="tarjetas-resumen">
            <div className="tarjeta">
              <span className="tarjeta-valor">
                {resultado.run.resumen_evaluacion.puntaje_promedio}
              </span>
              <span className="tarjeta-etiqueta">Puntaje promedio (0–1)</span>
            </div>
            <div className="tarjeta">
              <span className="tarjeta-valor">
                {resultado.run.resumen_evaluacion.puntaje_promedio_riesgo_alto ?? "N/A"}
              </span>
              <span className="tarjeta-etiqueta">Puntaje en ítems de riesgo alto</span>
            </div>
            <div className="tarjeta">
              <span className="tarjeta-valor">${resultado.run.costo_total_usd}</span>
              <span className="tarjeta-etiqueta">Costo total de la corrida (USD)</span>
            </div>
            <div className="tarjeta">
              <span className="tarjeta-valor">
                {resultado.run.latencia_promedio_segundos}s
              </span>
              <span className="tarjeta-etiqueta">Latencia promedio</span>
            </div>
          </div>

          <table className="tabla-detalle">
            <thead>
              <tr>
                <th>Pregunta</th>
                <th>Categoría</th>
                <th>Riesgo</th>
                <th>Puntaje</th>
              </tr>
            </thead>
            <tbody>
              {resultado.detalle_items.map((item) => (
                <tr key={item.item_id}>
                  <td>{item.pregunta}</td>
                  <td>{item.categoria}</td>
                  <td className={`riesgo riesgo-${item.riesgo_alucinacion}`}>
                    {item.riesgo_alucinacion}
                  </td>
                  <td>{item.puntaje_compuesto}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
