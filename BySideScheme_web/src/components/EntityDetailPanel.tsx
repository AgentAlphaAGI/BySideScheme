import React from 'react';
import { X, User, Calendar, Briefcase, Box, Building } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GraphNode, GraphEdge } from '../types';

interface EntityDetailPanelProps {
  entity: GraphNode | null;
  edges: GraphEdge[];
  allNodes: GraphNode[];
  onClose: () => void;
  onNavigate: (entityName: string) => void;
}

const NODE_TYPE_CONFIG: Record<string, { icon: React.ElementType; color: string; label: string }> = {
  Person: { icon: User, color: 'text-cyan-400', label: '人物' },
  Event: { icon: Calendar, color: 'text-orange-400', label: '事件' },
  Project: { icon: Briefcase, color: 'text-emerald-400', label: '项目' },
  Resource: { icon: Box, color: 'text-violet-400', label: '资源' },
  Organization: { icon: Building, color: 'text-rose-400', label: '组织' },
};

const SENTIMENT_LABELS: Record<string, { text: string; color: string }> = {
  positive: { text: '正面', color: 'text-emerald-400' },
  negative: { text: '负面', color: 'text-rose-400' },
  neutral: { text: '中性', color: 'text-gray-400' },
};

const EntityDetailPanel: React.FC<EntityDetailPanelProps> = ({
  entity,
  edges,
  allNodes,
  onClose,
  onNavigate,
}) => {
  if (!entity) return null;

  const config = NODE_TYPE_CONFIG[entity.type] || NODE_TYPE_CONFIG.Person;
  const Icon = config.icon;

  // Find connected edges (as source or target)
  const connectedEdges = edges.filter(
    (e) => e.source === entity.id || e.target === entity.id
  );

  // Helper: get node name by id
  const getNodeName = (id: string) => {
    const node = allNodes.find((n) => n.id === id);
    return node?.name || id;
  };

  const getNodeType = (id: string) => {
    const node = allNodes.find((n) => n.id === id);
    return node?.type || 'Person';
  };

  // Properties to display (filter out internal ones)
  const displayProps = Object.entries(entity.properties).filter(
    ([key]) => !['name', 'created_at', 'updated_at'].includes(key)
  );

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: 320, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 320, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="absolute top-0 right-0 h-full w-80 glass border-l border-white/10 overflow-y-auto z-20"
      >
        {/* Header */}
        <div className="sticky top-0 glass p-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className={`w-5 h-5 ${config.color}`} />
            <span className={`text-xs px-2 py-0.5 rounded-full border ${config.color} border-current/30`}>
              {config.label}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-white/10 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="p-4 space-y-5">
          {/* Entity Name */}
          <div>
            <h3 className="text-xl font-bold">{entity.name}</h3>
            {entity.properties.role && (
              <p className="text-sm text-gray-400 mt-1">{entity.properties.role}</p>
            )}
            {entity.properties.description && (
              <p className="text-sm text-gray-300 mt-2">{entity.properties.description}</p>
            )}
          </div>

          {/* Properties */}
          {displayProps.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-400 mb-2">属性</h4>
              <div className="space-y-1.5">
                {displayProps.map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-500">{key}</span>
                    <span className="text-gray-200 text-right max-w-[60%] truncate">
                      {String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="text-xs text-gray-600 space-y-1">
            {entity.properties.created_at && (
              <div>创建: {new Date(entity.properties.created_at).toLocaleString('zh-CN')}</div>
            )}
            {entity.properties.updated_at && (
              <div>更新: {new Date(entity.properties.updated_at).toLocaleString('zh-CN')}</div>
            )}
          </div>

          {/* Connected Relations */}
          {connectedEdges.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-400 mb-2">
                关系 ({connectedEdges.length})
              </h4>
              <div className="space-y-2">
                {connectedEdges.map((edge, idx) => {
                  const isSource = edge.source === entity.id;
                  const otherId = isSource ? edge.target : edge.source;
                  const otherName = getNodeName(otherId);
                  const otherType = getNodeType(otherId);
                  const otherConfig = NODE_TYPE_CONFIG[otherType] || NODE_TYPE_CONFIG.Person;
                  const sentimentInfo = SENTIMENT_LABELS[edge.sentiment] || SENTIMENT_LABELS.neutral;

                  return (
                    <div
                      key={idx}
                      className="glass rounded-lg p-3 hover:bg-white/5 transition-colors cursor-pointer"
                      onClick={() => onNavigate(otherName)}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-1.5">
                          <span className={`text-xs ${otherConfig.color}`}>
                            {otherConfig.label}
                          </span>
                          <span className="text-sm font-medium">{otherName}</span>
                        </div>
                        <span className={`text-xs ${sentimentInfo.color}`}>
                          {sentimentInfo.text}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span className="text-primary">
                          {isSource ? '→' : '←'} {edge.type}
                        </span>
                        <span>强度: {(edge.weight * 100).toFixed(0)}%</span>
                        <span>信心: {(edge.confidence * 100).toFixed(0)}%</span>
                      </div>
                      {edge.evidence && edge.evidence.length > 0 && edge.evidence[0] && (
                        <p className="text-xs text-gray-600 mt-1.5 italic truncate">
                          "{edge.evidence[0]}"
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {connectedEdges.length === 0 && (
            <div className="text-sm text-gray-600 italic">暂无已知关系</div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default EntityDetailPanel;
