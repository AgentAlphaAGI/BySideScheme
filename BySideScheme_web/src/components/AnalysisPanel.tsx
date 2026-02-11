import React from 'react';
import { Analysis } from '../types';
import { AlertTriangle, TrendingUp, UserCheck, Activity } from 'lucide-react';
import { cn } from '../utils/cn';

interface AnalysisPanelProps {
  analysis: Analysis | null;
}

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ analysis }) => {
  if (!analysis) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-2 p-4">
        <Activity className="w-8 h-8 opacity-20" />
        <p className="text-sm">暂无洞察分析</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-4 space-y-6 scrollbar-thin">
      {/* Overall Score */}
      <div className="p-4 bg-black/40 rounded-lg border border-white/5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">总体风险分</span>
          <span className={cn(
            "text-xl font-bold",
            analysis.overall_risk_score > 70 ? "text-red-500" :
            analysis.overall_risk_score > 40 ? "text-yellow-500" : "text-green-500"
          )}>
            {analysis.overall_risk_score}
          </span>
        </div>
        <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
          <div 
            className={cn("h-full transition-all duration-500",
              analysis.overall_risk_score > 70 ? "bg-red-500" :
              analysis.overall_risk_score > 40 ? "bg-yellow-500" : "bg-green-500"
            )}
            style={{ width: `${analysis.overall_risk_score}%` }}
          />
        </div>
      </div>

      {/* Risks */}
      {analysis.risks.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-neon-red font-semibold text-sm">
            <AlertTriangle className="w-4 h-4" />
            风险预警
          </div>
          {analysis.risks.map((risk, idx) => (
            <div key={idx} className="p-3 bg-red-500/10 rounded-lg border border-red-500/20 text-sm">
              <div className="font-medium text-red-400 mb-1">{risk.title}</div>
              <div className="text-gray-400 text-xs mb-2">{risk.impact}</div>
              {risk.mitigation.length > 0 && (
                <div className="text-xs text-gray-500 bg-black/20 p-2 rounded border border-white/5">
                  <span className="text-gray-400">建议:</span> {risk.mitigation.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Insights */}
      {analysis.situation_insights.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-neon-blue font-semibold text-sm">
            <TrendingUp className="w-4 h-4" />
            局势洞察
          </div>
          <ul className="space-y-2">
            {analysis.situation_insights.map((insight, idx) => (
              <li key={idx} className="text-sm text-gray-300 pl-4 relative before:content-[''] before:absolute before:left-0 before:top-2 before:w-1.5 before:h-1.5 before:bg-neon-blue before:rounded-full">
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Persona Updates */}
      {analysis.persona_updates.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-neon-purple font-semibold text-sm">
            <UserCheck className="w-4 h-4" />
            画像校准
          </div>
          {analysis.persona_updates.map((update, idx) => (
            <div key={idx} className="p-3 bg-neon-purple/10 rounded-lg border border-neon-purple/20 text-sm">
              <div className="font-medium text-neon-purple mb-1">
                {update.person_name} <span className="text-xs opacity-70">({(update.update_confidence * 100).toFixed(0)}% 置信度)</span>
              </div>
              <div className="text-gray-400 text-xs mb-2">
                监测到行为偏差：{update.trait_behavior_chain}
              </div>
              <div className="text-xs text-gray-500 italic border-l-2 border-neon-purple/30 pl-2">
                "{update.updated_persona}"
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Next Actions */}
      {analysis.next_actions.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-green-400 font-semibold text-sm">
            <Activity className="w-4 h-4" />
            下一步建议
          </div>
           <ul className="space-y-2">
            {analysis.next_actions.map((action, idx) => (
              <li key={idx} className="text-sm text-gray-300 pl-4 relative before:content-[''] before:absolute before:left-0 before:top-2 before:w-1.5 before:h-1.5 before:bg-green-400 before:rounded-full">
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AnalysisPanel;
