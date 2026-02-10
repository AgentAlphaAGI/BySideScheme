import React, { useState } from 'react';
import { useUserStore } from '../store/userStore';
import { generateAdvice } from '../services/api';
import { AdviceResponse } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Shield, Sword, AlertTriangle } from 'lucide-react';
import { cn } from '../utils/cn';

const Advisor: React.FC = () => {
  const { userId } = useUserStore();
  const [fact, setFact] = useState('');
  const [loading, setLoading] = useState(false);
  const [advice, setAdvice] = useState<AdviceResponse | null>(null);

  const handleGenerate = async () => {
    if (!fact.trim()) return;
    setLoading(true);
    setAdvice(null);
    try {
      const data = await generateAdvice(userId, fact);
      setAdvice(data);
    } catch (error) {
      console.error("Failed to generate advice", error);
    } finally {
      setLoading(false);
    }
  };

  const getStrategyIcon = (intent: string) => {
    if (intent.includes('防守') || intent.includes('潜伏')) return <Shield className="w-5 h-5" />;
    if (intent.includes('收割') || intent.includes('进攻')) return <Sword className="w-5 h-5" />;
    return <AlertTriangle className="w-5 h-5" />;
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold neon-text-purple">策略顾问</h2>
      
      <div className="glass p-6 rounded-lg">
        <textarea 
          className="w-full bg-black/30 border border-gray-700 rounded p-4 text-white focus:outline-none focus:border-primary transition-colors resize-none"
          rows={5}
          placeholder="请输入今日发生的职场事实... (例如: 项目延期了，老板在早会上发火)"
          value={fact}
          onChange={(e) => setFact(e.target.value)}
          disabled={loading}
        />
        <div className="mt-4 flex justify-between items-center">
          <span className="text-xs text-gray-500">
            {fact.length} 字符
          </span>
          <button 
            onClick={handleGenerate}
            disabled={loading || !fact.trim()}
            className="bg-primary text-black font-bold py-2 px-6 rounded flex items-center gap-2 hover:bg-opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Sparkles className="animate-spin" /> : <Send size={18} />}
            {loading ? '生成中...' : '生成策略'}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {advice && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Decision Card */}
            <div className="glass p-6 rounded-lg border-l-4 border-secondary">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-secondary/20 rounded-full text-secondary">
                  {getStrategyIcon(advice.decision.strategic_intent)}
                </div>
                <div>
                  <h3 className="text-lg font-bold">决策引擎判断</h3>
                  <div className="flex gap-2 text-xs mt-1">
                    <span className={cn("px-2 py-0.5 rounded", advice.decision.should_say ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400")}>
                      {advice.decision.should_say ? "建议表达" : "建议沉默"}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">
                      时机: {advice.decision.timing_check}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">
                      意图: {advice.decision.strategic_intent}
                    </span>
                  </div>
                </div>
              </div>
              <p className="text-gray-300 bg-black/20 p-4 rounded border-l-2 border-gray-600">
                {advice.decision.strategy_summary}
              </p>
            </div>

            {/* Narratives Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Boss Version */}
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="glass p-6 rounded-lg border border-primary/30"
              >
                <h3 className="text-primary font-bold mb-4 flex items-center gap-2">
                  <span className="w-2 h-2 bg-primary rounded-full"></span>
                  对上版本 (Boss Version)
                </h3>
                <div className="bg-black/30 p-4 rounded text-gray-200 leading-relaxed min-h-[120px]">
                  {advice.narrative.boss_version}
                </div>
              </motion.div>

              {/* Self Version */}
              <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="glass p-6 rounded-lg border border-secondary/30"
              >
                <h3 className="text-secondary font-bold mb-4 flex items-center gap-2">
                  <span className="w-2 h-2 bg-secondary rounded-full"></span>
                  自我复盘 (Self Version)
                </h3>
                <div className="bg-black/30 p-4 rounded text-gray-200 leading-relaxed min-h-[120px]">
                  {advice.narrative.self_version}
                </div>
              </motion.div>
            </div>

            {/* Strategy Hints */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="glass p-6 rounded-lg bg-gradient-to-r from-primary/10 to-transparent"
            >
              <h3 className="text-white font-bold mb-2">💡 策略提示</h3>
              <p className="text-gray-300">{advice.narrative.strategy_hints}</p>
            </motion.div>

            {/* Context Used */}
            <div className="text-xs text-gray-500 mt-8 border-t border-gray-800 pt-4">
              <details>
                <summary className="cursor-pointer hover:text-gray-300">查看引用上下文</summary>
                <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div>
                    <h4 className="font-bold mb-1">记忆引用:</h4>
                    <pre className="bg-black/50 p-2 rounded overflow-auto max-h-40 whitespace-pre-wrap">{advice.context_used.memory}</pre>
                   </div>
                   <div>
                    <h4 className="font-bold mb-1">局势引用:</h4>
                    <pre className="bg-black/50 p-2 rounded overflow-auto max-h-40 whitespace-pre-wrap">{advice.context_used.situation}</pre>
                   </div>
                </div>
              </details>
            </div>

          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Advisor;
