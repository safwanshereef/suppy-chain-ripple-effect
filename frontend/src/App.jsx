import { useMemo } from 'react';
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './App.css';

// Static sample of the AtmoGraph supply chain (real port and plant codes from the dataset)
const ports = [
  { id: 'PORT09', risk: 0.2 },
  { id: 'PORT04', risk: 0.1 },
  { id: 'PORT05', risk: 0.8 },
  { id: 'PORT08', risk: 0.1 },
];

const plants = [
  { id: 'PLANT16', port: 'PORT09', risk: 0.2 },
  { id: 'PLANT03', port: 'PORT04', risk: 0.1 },
  { id: 'PLANT12', port: 'PORT05', risk: 0.7 },
  { id: 'PLANT19', port: 'PORT05', risk: 0.6 },
  { id: 'PLANT07', port: 'PORT08', risk: 0.1 },
];

const routes = [
  ['PORT09', 'PORT04'],
  ['PORT04', 'PORT05'],
  ['PORT05', 'PORT08'],
  ['PORT09', 'PORT08'],
];

// Colour a node by its risk score: green is safe, amber is watch, red is at risk
function riskColor(risk) {
  if (risk >= 0.6) return '#ec0909';
  if (risk >= 0.3) return '#f59e0b';
  return '#22c55e';
}

function buildGraph() {
  const nodes = [];
  const edges = [];

  ports.forEach((p, i) => {
    nodes.push({
      id: p.id,
      position: { x: 150 + i * 260, y: 250 },
      data: { label: `${p.id}\nrisk ${p.risk}` },
      style: {
        background: riskColor(p.risk),
        color: '#fff',
        border: '2px solid #1e293b',
        borderRadius: 8,
        padding: 12,
        whiteSpace: 'pre-line',
        fontWeight: 600,
      },
    });
  });

  plants.forEach((pl, i) => {
    nodes.push({
      id: pl.id,
      position: { x: 60 + i * 210, y: 30 },
      data: { label: `${pl.id}\nrisk ${pl.risk}` },
      style: {
        background: riskColor(pl.risk),
        color: '#fff',
        border: '2px solid #1e293b',
        borderRadius: 24,
        padding: 10,
        whiteSpace: 'pre-line',
        fontSize: 12,
      },
    });
    edges.push({
      id: `${pl.id}-${pl.port}`,
      source: pl.id,
      target: pl.port,
      label: 'HOSTED_AT',
      style: { stroke: '#64748b' },
    });
  });

  routes.forEach(([a, b]) => {
    edges.push({
      id: `${a}-${b}`,
      source: a,
      target: b,
      label: 'ROUTE',
      animated: true,
      style: { stroke: '#3b82f6', strokeWidth: 2 },
    });
  });

  return { nodes, edges };
}

export default function App() {
  const { nodes, edges } = useMemo(() => buildGraph(), []);

  return (
    <div className="app">
      <header className="header">
        <h1>AtmoGraph</h1>
        <p>Supply Chain Ripple Effect Predictor</p>
      </header>

      <div className="legend">
        <span><i style={{ background: 'rgb(43, 204, 29)' }} /> Low risk</span>
        <span><i style={{ background: 'rgb(232, 152, 14)' }} /> Watch</span>
        <span><i style={{ background: 'rgb(203, 25, 25)' }} /> At risk</span>
      </div>

      <div className="graph">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}