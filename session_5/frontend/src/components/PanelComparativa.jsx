import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export function PanelComparativa() {
  const [comparativa, setComparativa] = useState([]);
  const [corridas, setCorridas] = useState([]);
  const [error, setError] = useState(null);

  async function recargar() {
    setError(null);
    try {
      const [c, r] = await Promise.all([api.obtenerComparativa(), api.obtenerRegistro()]);
      setComparativa(c.comparativa);
      setCorridas(r.corridas);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    recargar();
  }, []);

  return (
    <section className="panel">
      <h2>Registro de resultados y comparativas</h2>
      <p className="ayuda">
        Cada corrida ejecutada en la pestaña "Evaluar proveedor" queda registrada aquí
        (backend/runs_log.json). Esta vista agrupa por proveedor/modelo para comparar
        calidad, costo y latencia antes de decidir cuál usar.
      </p>

      <button onClick={recargar}>Actualizar</button>
      {error && <p className="error">⚠ {error}</p>}

      <table className="tabla-detalle">
        <thead>
          <tr>
            <th>Proveedor</th>
            <th>Modelo</th>
            <th>Corridas</th>
            <th>Puntaje promedio</th>
            <th>Costo promedio (USD)</th>
            <th>Latencia promedio (s)</th>
          </tr>
        </thead>
        <tbody>
          {comparativa.map((fila) => (
            <tr key={`${fila.proveedor}:${fila.modelo}`}>
              <td>{fila.proveedor}</td>
              <td>{fila.modelo}</td>
              <td>{fila.corridas}</td>
              <td>{fila.puntaje_promedio}</td>
              <td>${fila.costo_promedio_usd}</td>
              <td>{fila.latencia_promedio_segundos}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Historial completo ({corridas.length} corridas)</h3>
      <table className="tabla-detalle">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Proveedor</th>
            <th>Modelo</th>
            <th>Puntaje</th>
            <th>Costo (USD)</th>
            <th>Aprobado por</th>
          </tr>
        </thead>
        <tbody>
          {corridas
            .slice()
            .reverse()
            .map((run) => (
              <tr key={run.id}>
                <td>{new Date(run.timestamp).toLocaleString()}</td>
                <td>{run.proveedor}</td>
                <td>{run.modelo}</td>
                <td>{run.resumen_evaluacion.puntaje_promedio}</td>
                <td>${run.costo_total_usd}</td>
                <td>{run.aprobado_por || "—"}</td>
              </tr>
            ))}
        </tbody>
      </table>
    </section>
  );
}
