import React, { useState } from "react";
import { api } from "../api.js";

export function PanelCosteo() {
  const [costoPorLlamada, setCostoPorLlamada] = useState(0.002);
  const [usuarios, setUsuarios] = useState(500);
  const [llamadasPorUsuario, setLlamadasPorUsuario] = useState(10);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);

  async function proyectar() {
    setError(null);
    try {
      const data = await api.proyectarCosto({
        costo_por_llamada_usd: Number(costoPorLlamada),
        usuarios_estimados: Number(usuarios),
        llamadas_por_usuario_mes: Number(llamadasPorUsuario),
      });
      setResultado(data);
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section className="panel">
      <h2>Proyección de costo del PoC</h2>
      <p className="ayuda">
        Traduce el costo por llamada (obtenido en la pestaña de evaluación) a un
        estimado mensual y anual según el volumen esperado de uso.
      </p>

      <div className="fila-controles">
        <label>
          Costo por llamada (USD)
          <input
            type="number"
            step="0.0001"
            value={costoPorLlamada}
            onChange={(e) => setCostoPorLlamada(e.target.value)}
          />
        </label>
        <label>
          Usuarios estimados
          <input type="number" value={usuarios} onChange={(e) => setUsuarios(e.target.value)} />
        </label>
        <label>
          Llamadas por usuario / mes
          <input
            type="number"
            value={llamadasPorUsuario}
            onChange={(e) => setLlamadasPorUsuario(e.target.value)}
          />
        </label>
        <button onClick={proyectar}>Calcular proyección</button>
      </div>

      {error && <p className="error">⚠ {error}</p>}

      {resultado && (
        <div className="tarjetas-resumen">
          <div className="tarjeta">
            <span className="tarjeta-valor">{resultado.llamadas_totales_mes}</span>
            <span className="tarjeta-etiqueta">Llamadas / mes</span>
          </div>
          <div className="tarjeta">
            <span className="tarjeta-valor">${resultado.costo_estimado_mes_usd}</span>
            <span className="tarjeta-etiqueta">Costo estimado / mes</span>
          </div>
          <div className="tarjeta">
            <span className="tarjeta-valor">${resultado.costo_estimado_anio_usd}</span>
            <span className="tarjeta-etiqueta">Costo estimado / año</span>
          </div>
          <p className="nota-advertencia">{resultado.advertencia}</p>
        </div>
      )}
    </section>
  );
}
