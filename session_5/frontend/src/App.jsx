import React, { useState } from "react";
import { PanelEvaluar } from "./components/PanelEvaluar.jsx";
import { PanelCosteo } from "./components/PanelCosteo.jsx";
import { PanelEtica } from "./components/PanelEtica.jsx";
import { PanelComparativa } from "./components/PanelComparativa.jsx";

const PESTANAS = [
  { id: "evaluar", etiqueta: "1. Evaluar proveedor" },
  { id: "costeo", etiqueta: "2. Proyección de costo" },
  { id: "etica", etiqueta: "3. Checklist de ética" },
  { id: "comparativa", etiqueta: "4. Registro y comparativa" },
];

export default function App() {
  const [pestanaActiva, setPestanaActiva] = useState("evaluar");

  return (
    <div className="app">
      <header className="app-header">
        <p className="eyebrow">Fundamentos de Arquitectura LLM · Sesión 5</p>
        <h1>Evaluación, Costeo y Ética en el Uso de LLM</h1>
        <p className="subtitulo">
          PoC de referencia: dataset dorado de "Tienda Andina" (10 ítems), harness de
          evaluación ligero, calculadora de costo y checklist ético.
        </p>
      </header>

      <nav className="tabs">
        {PESTANAS.map((p) => (
          <button
            key={p.id}
            className={p.id === pestanaActiva ? "tab tab-activo" : "tab"}
            onClick={() => setPestanaActiva(p.id)}
          >
            {p.etiqueta}
          </button>
        ))}
      </nav>

      <main className="contenido">
        {pestanaActiva === "evaluar" && <PanelEvaluar />}
        {pestanaActiva === "costeo" && <PanelCosteo />}
        {pestanaActiva === "etica" && <PanelEtica />}
        {pestanaActiva === "comparativa" && <PanelComparativa />}
      </main>
    </div>
  );
}
