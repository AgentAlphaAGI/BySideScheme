import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ForceGraph2D, { type ForceGraphMethods } from 'react-force-graph-2d';
import { motion } from 'framer-motion';
import {
  RefreshCw,
  Trash2,
  Search,
  Filter,
  ZoomIn,
  ZoomOut,
  Maximize2,
  AlertTriangle,
  TrendingUp,
} from 'lucide-react';
import { useUserStore } from '../store/userStore';
import { getGraph, getGraphInsights, clearGraph } from '../services/api';
import { GraphNode, GraphEdge, GraphData, GraphInsights } from '../types';
import EntityDetailPanel from '../components/EntityDetailPanel';

// ------------------------------------------------------------------
// 颜色配置（赛博朋克风格）
// ------------------------------------------------------------------
const NODE_COLORS: Record<string, string> = {
  Person: '#00d4ff',       // cyan / primary
  Event: '#f59e0b',        // amber
  Project: '#10b981',      // emerald
  Resource: '#8b5cf6',     // violet / secondary
  Organization: '#ef4444', // rose
};

const NODE_BORDER_COLORS: Record<string, string> = {
  Person: '#0891b2',
  Event: '#d97706',
  Project: '#059669',
  Resource: '#7c3aed',
  Organization: '#dc2626',
};

const SENTIMENT_EDGE_COLORS: Record<string, string> = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#6b7280',
};

const NODE_TYPE_LABELS: Record<string, string> = {
  Person: '人物',
  Event: '事件',
  Project: '项目',
  Resource: '资源',
  Organization: '组织',
};

// ------------------------------------------------------------------
// ForceGraph data shape
// ------------------------------------------------------------------
interface FGNode {
  id: string;
  name: string;
  type: string;
  properties: Record<string, any>;
  x?: number;
  y?: number;
}

interface FGLink {
  source: string | FGNode;
  target: string | FGNode;
  type: string;
  weight: number;
  sentiment: string;
  confidence: number;
  evidence: string[];
}

interface FGData {
  nodes: FGNode[];
  links: FGLink[];
}

// ------------------------------------------------------------------
// Component
// ------------------------------------------------------------------
const GraphView: React.FC = () => {
  const { userId } = useUserStore();
  const graphRef = useRef<ForceGraphMethods<FGNode, FGLink>>();

  // Data
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [insights, setInsights] = useState<GraphInsights | null>(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState<GraphNode | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilters, setActiveFilters] = useState<Set<string>>(
    new Set(['Person', 'Event', 'Project', 'Resource', 'Organization'])
  );
  const [showInsights, setShowInsights] = useState(false);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const containerRef = useRef<HTMLDivElement>(null);

  // ------------------------------------------------------------------
  // Data fetching
  // ------------------------------------------------------------------
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [data, insightsData] = await Promise.all([
        getGraph(userId),
        getGraphInsights(userId).catch(() => null),
      ]);
      setGraphData(data);
      setInsights(insightsData);
    } catch (error) {
      console.error('Failed to fetch graph data', error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Resize observer
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setDimensions({ width, height });
      }
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  // ------------------------------------------------------------------
  // Filtered data for ForceGraph
  // ------------------------------------------------------------------
  const fgData: FGData = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] };

    const lowerSearch = searchTerm.toLowerCase();

    const filteredNodes = graphData.nodes.filter((n) => {
      if (!activeFilters.has(n.type)) return false;
      if (searchTerm && !n.name.toLowerCase().includes(lowerSearch)) return false;
      return true;
    });

    const nodeIds = new Set(filteredNodes.map((n) => n.id));

    const filteredEdges = graphData.edges.filter(
      (e) => nodeIds.has(e.source) && nodeIds.has(e.target)
    );

    return {
      nodes: filteredNodes.map((n) => ({ ...n })),
      links: filteredEdges.map((e) => ({
        source: e.source,
        target: e.target,
        type: e.type,
        weight: e.weight,
        sentiment: e.sentiment,
        confidence: e.confidence,
        evidence: e.evidence,
      })),
    };
  }, [graphData, activeFilters, searchTerm]);

  // ------------------------------------------------------------------
  // Handlers
  // ------------------------------------------------------------------
  const handleNodeClick = useCallback(
    (node: FGNode) => {
      if (!graphData) return;
      const found = graphData.nodes.find((n) => n.id === node.id);
      setSelectedEntity(found || null);

      // Center on node
      if (graphRef.current) {
        graphRef.current.centerAt(node.x, node.y, 500);
        graphRef.current.zoom(2, 500);
      }
    },
    [graphData]
  );

  const handleNavigateToEntity = useCallback(
    (entityName: string) => {
      if (!graphData) return;
      const target = graphData.nodes.find((n) => n.name === entityName);
      if (target) {
        setSelectedEntity(target);
        const fgNode = fgData.nodes.find((n) => n.id === target.id);
        if (fgNode && graphRef.current) {
          graphRef.current.centerAt(fgNode.x, fgNode.y, 500);
          graphRef.current.zoom(2, 500);
        }
      }
    },
    [graphData, fgData]
  );

  const handleClearGraph = async () => {
    if (window.confirm('确定要清空整个图谱吗？此操作不可撤销。')) {
      try {
        await clearGraph(userId);
        setGraphData(null);
        setSelectedEntity(null);
        setInsights(null);
      } catch (error) {
        console.error('Failed to clear graph', error);
      }
    }
  };

  const toggleFilter = (type: string) => {
    setActiveFilters((prev) => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  };

  // ------------------------------------------------------------------
  // Canvas node renderer
  // ------------------------------------------------------------------
  const nodeCanvasObject = useCallback(
    (node: FGNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const label = node.name;
      const fontSize = Math.max(12 / globalScale, 3);
      const nodeRadius = 6;
      const isSelected = selectedEntity?.id === node.id;

      // Glow effect for selected node
      if (isSelected) {
        ctx.shadowColor = NODE_COLORS[node.type] || '#00d4ff';
        ctx.shadowBlur = 20;
      }

      // Node circle
      ctx.beginPath();
      ctx.arc(node.x!, node.y!, nodeRadius, 0, 2 * Math.PI);
      ctx.fillStyle = NODE_COLORS[node.type] || '#00d4ff';
      ctx.fill();

      // Border
      ctx.strokeStyle = isSelected
        ? '#ffffff'
        : NODE_BORDER_COLORS[node.type] || '#0891b2';
      ctx.lineWidth = isSelected ? 2 / globalScale : 1 / globalScale;
      ctx.stroke();

      // Reset shadow
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;

      // Label
      ctx.font = `${fontSize}px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillStyle = '#e5e7eb';
      ctx.fillText(label, node.x!, node.y! + nodeRadius + 2);
    },
    [selectedEntity]
  );

  const linkCanvasObject = useCallback(
    (link: FGLink, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const source = link.source as FGNode;
      const target = link.target as FGNode;
      if (!source.x || !target.x) return;

      const edgeColor = SENTIMENT_EDGE_COLORS[link.sentiment] || SENTIMENT_EDGE_COLORS.neutral;
      const lineWidth = Math.max(link.weight * 3, 0.5) / globalScale;

      ctx.beginPath();
      ctx.moveTo(source.x, source.y!);
      ctx.lineTo(target.x, target.y!);
      ctx.strokeStyle = edgeColor;
      ctx.lineWidth = lineWidth;
      ctx.globalAlpha = 0.4 + link.weight * 0.6;
      ctx.stroke();
      ctx.globalAlpha = 1;

      // Arrow
      const angle = Math.atan2(target.y! - source.y!, target.x - source.x);
      const arrowLen = 4 / globalScale;
      const arrowX = target.x - Math.cos(angle) * 8;
      const arrowY = target.y! - Math.sin(angle) * 8;

      ctx.beginPath();
      ctx.moveTo(arrowX, arrowY);
      ctx.lineTo(
        arrowX - arrowLen * Math.cos(angle - Math.PI / 6),
        arrowY - arrowLen * Math.sin(angle - Math.PI / 6)
      );
      ctx.lineTo(
        arrowX - arrowLen * Math.cos(angle + Math.PI / 6),
        arrowY - arrowLen * Math.sin(angle + Math.PI / 6)
      );
      ctx.fillStyle = edgeColor;
      ctx.fill();

      // Relation type label (only when zoomed in enough)
      if (globalScale > 1.5) {
        const midX = (source.x + target.x) / 2;
        const midY = (source.y! + target.y!) / 2;
        const fontSize = Math.max(8 / globalScale, 2);
        ctx.font = `${fontSize}px Inter, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#9ca3af';
        ctx.globalAlpha = 0.7;
        ctx.fillText(link.type, midX, midY);
        ctx.globalAlpha = 1;
      }
    },
    []
  );

  // ------------------------------------------------------------------
  // Edges as GraphEdge[] for the detail panel
  // ------------------------------------------------------------------
  const edgesForPanel: GraphEdge[] = useMemo(() => {
    if (!graphData) return [];
    return graphData.edges;
  }, [graphData]);

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  const isEmpty = !graphData || graphData.nodes.length === 0;

  return (
    <div className="space-y-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center flex-shrink-0">
        <h2 className="text-3xl font-bold neon-text-purple">局势图谱</h2>
        <div className="flex gap-2">
          <button
            onClick={fetchData}
            className="p-2 rounded-full hover:bg-white/10 transition-colors"
            title="刷新"
          >
            <RefreshCw className={loading ? 'animate-spin' : ''} size={20} />
          </button>
          <button
            onClick={() => setShowInsights((v) => !v)}
            className={`p-2 rounded-full transition-colors ${
              showInsights ? 'bg-primary/20 text-primary' : 'hover:bg-white/10'
            }`}
            title="图谱洞察"
          >
            <TrendingUp size={20} />
          </button>
          <button
            onClick={handleClearGraph}
            className="p-2 rounded-full hover:bg-white/10 transition-colors text-red-400"
            title="清空图谱"
          >
            <Trash2 size={20} />
          </button>
        </div>
      </div>

      {/* Toolbar: Search + Filters */}
      <div className="flex flex-wrap gap-3 items-center flex-shrink-0">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="搜索实体..."
            className="w-full bg-surface border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:border-primary/50 transition-colors"
          />
        </div>

        {/* Type Filters */}
        <div className="flex gap-1.5 items-center">
          <Filter size={14} className="text-gray-500 mr-1" />
          {Object.entries(NODE_TYPE_LABELS).map(([type, label]) => (
            <button
              key={type}
              onClick={() => toggleFilter(type)}
              className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-all ${
                activeFilters.has(type)
                  ? 'border-current opacity-100'
                  : 'border-gray-700 opacity-40 hover:opacity-70'
              }`}
              style={{
                color: activeFilters.has(type)
                  ? NODE_COLORS[type]
                  : '#9ca3af',
              }}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Zoom controls */}
        <div className="flex gap-1">
          <button
            onClick={() => graphRef.current?.zoom(graphRef.current.zoom() * 1.5, 300)}
            className="p-1.5 rounded hover:bg-white/10 transition-colors"
            title="放大"
          >
            <ZoomIn size={16} />
          </button>
          <button
            onClick={() => graphRef.current?.zoom(graphRef.current.zoom() / 1.5, 300)}
            className="p-1.5 rounded hover:bg-white/10 transition-colors"
            title="缩小"
          >
            <ZoomOut size={16} />
          </button>
          <button
            onClick={() => graphRef.current?.zoomToFit(400, 40)}
            className="p-1.5 rounded hover:bg-white/10 transition-colors"
            title="适应窗口"
          >
            <Maximize2 size={16} />
          </button>
        </div>

        {/* Stats */}
        <div className="text-xs text-gray-500 ml-auto">
          {fgData.nodes.length} 节点 / {fgData.links.length} 关系
        </div>
      </div>

      {/* Insights Panel (collapsible) */}
      {showInsights && insights && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="glass rounded-lg p-4 space-y-3 flex-shrink-0"
        >
          <h3 className="text-sm font-bold text-primary flex items-center gap-2">
            <TrendingUp size={14} /> 图谱洞察
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            {/* Key Players */}
            <div>
              <h4 className="text-gray-400 text-xs mb-1.5">关键人物</h4>
              {insights.key_players.length > 0 ? (
                insights.key_players.slice(0, 5).map((p) => (
                  <div
                    key={p.name}
                    className="flex justify-between py-0.5 cursor-pointer hover:text-primary transition-colors"
                    onClick={() => handleNavigateToEntity(p.name)}
                  >
                    <span>{p.name}</span>
                    <span className="text-gray-500">连接度 {p.centrality}</span>
                  </div>
                ))
              ) : (
                <p className="text-gray-600 italic">暂无数据</p>
              )}
            </div>

            {/* Risk Relations */}
            <div>
              <h4 className="text-gray-400 text-xs mb-1.5 flex items-center gap-1">
                <AlertTriangle size={12} className="text-rose-400" /> 风险关系
              </h4>
              {insights.risk_relations.length > 0 ? (
                insights.risk_relations.slice(0, 5).map((r, i) => (
                  <div key={i} className="py-0.5 text-rose-300/80">
                    {r.source} → {r.target}{' '}
                    <span className="text-gray-500">({r.type})</span>
                  </div>
                ))
              ) : (
                <p className="text-gray-600 italic">暂无风险</p>
              )}
            </div>

            {/* Recent Changes */}
            <div>
              <h4 className="text-gray-400 text-xs mb-1.5">近期变化</h4>
              {insights.recent_changes.length > 0 ? (
                insights.recent_changes.slice(0, 5).map((c, i) => (
                  <div key={i} className="py-0.5 text-gray-300">
                    {c.description}
                  </div>
                ))
              ) : (
                <p className="text-gray-600 italic">暂无变化</p>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Main Graph Area */}
      <div className="flex-1 relative glass rounded-lg overflow-hidden min-h-[400px]" ref={containerRef}>
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center z-10 bg-black/50">
            <RefreshCw className="w-8 h-8 animate-spin text-primary" />
          </div>
        )}

        {isEmpty && !loading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <div className="text-6xl mb-4 opacity-20">🕸</div>
            <p className="text-lg">图谱为空</p>
            <p className="text-sm mt-2">
              通过"策略顾问"输入职场事实，系统将自动构建局势图谱
            </p>
          </div>
        ) : (
          <ForceGraph2D
            ref={graphRef}
            graphData={fgData}
            width={dimensions.width}
            height={dimensions.height}
            nodeCanvasObject={nodeCanvasObject}
            linkCanvasObject={linkCanvasObject}
            onNodeClick={handleNodeClick}
            onBackgroundClick={() => setSelectedEntity(null)}
            nodeId="id"
            linkSource="source"
            linkTarget="target"
            cooldownTicks={100}
            d3AlphaDecay={0.02}
            d3VelocityDecay={0.3}
            enableNodeDrag={true}
            enableZoomInteraction={true}
            enablePanInteraction={true}
            backgroundColor="transparent"
          />
        )}

        {/* Entity Detail Panel */}
        {selectedEntity && graphData && (
          <EntityDetailPanel
            entity={selectedEntity}
            edges={edgesForPanel}
            allNodes={graphData.nodes}
            onClose={() => setSelectedEntity(null)}
            onNavigate={handleNavigateToEntity}
          />
        )}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-gray-500 flex-shrink-0">
        <span className="text-gray-400">节点类型:</span>
        {Object.entries(NODE_TYPE_LABELS).map(([type, label]) => (
          <span key={type} className="flex items-center gap-1">
            <span
              className="w-2.5 h-2.5 rounded-full inline-block"
              style={{ backgroundColor: NODE_COLORS[type] }}
            />
            {label}
          </span>
        ))}
        <span className="text-gray-400 ml-4">关系情感:</span>
        <span className="flex items-center gap-1">
          <span className="w-4 h-0.5 bg-emerald-400 inline-block rounded" /> 正面
        </span>
        <span className="flex items-center gap-1">
          <span className="w-4 h-0.5 bg-rose-400 inline-block rounded" /> 负面
        </span>
        <span className="flex items-center gap-1">
          <span className="w-4 h-0.5 bg-gray-500 inline-block rounded" /> 中性
        </span>
      </div>
    </div>
  );
};

export default GraphView;
