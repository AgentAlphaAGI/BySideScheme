import React, { useEffect, useState } from 'react';
import { useUserStore } from '../store/userStore';
import { getMemories, consolidateMemories, deleteMemory } from '../services/api';
import { Memory as MemoryType } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Trash2, Zap, Search } from 'lucide-react';
import { cn } from '../utils/cn';

const Memory: React.FC = () => {
  const { userId } = useUserStore();
  const [memories, setMemories] = useState<MemoryType[]>([]);
  const [loading, setLoading] = useState(false);
  const [consolidating, setConsolidating] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchMemories = async () => {
    setLoading(true);
    try {
      const data = await getMemories(userId);
      setMemories(data.memories);
    } catch (error) {
      console.error("Failed to fetch memories", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, [userId]);

  const handleConsolidate = async () => {
    setConsolidating(true);
    try {
      await consolidateMemories(userId);
      await fetchMemories();
    } catch (error) {
      console.error("Failed to consolidate memories", error);
    } finally {
      setConsolidating(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteMemory(userId, id);
      setMemories(prev => prev.filter(m => m.id !== id));
    } catch (error) {
      console.error("Failed to delete memory", error);
    }
  };

  const filteredMemories = memories.filter(m => 
    m.memory.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.metadata.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getCategoryColor = (category: string) => {
    switch(category) {
      case 'insight': return 'border-purple-500 text-purple-400';
      case 'narrative': return 'border-blue-500 text-blue-400';
      case 'political': return 'border-red-500 text-red-400';
      case 'commitment': return 'border-yellow-500 text-yellow-400';
      default: return 'border-gray-500 text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <h2 className="text-3xl font-bold neon-text-purple">记忆库</h2>
        <div className="flex gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
            <input 
              type="text" 
              placeholder="搜索记忆..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-black/30 border border-gray-700 rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-primary"
            />
          </div>
          <button 
            onClick={handleConsolidate}
            disabled={consolidating}
            className="bg-secondary text-white px-4 py-2 rounded-full flex items-center gap-2 hover:bg-opacity-80 transition-colors disabled:opacity-50 text-sm whitespace-nowrap"
          >
            <Zap size={16} className={consolidating ? "animate-pulse" : ""} />
            {consolidating ? '整理中...' : '整理记忆'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Brain className="w-12 h-12 animate-pulse text-gray-600" />
        </div>
      ) : (
        <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {filteredMemories.map((memory) => (
              <motion.div
                key={memory.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className={cn(
                  "glass p-4 rounded-lg border-t-2 relative group hover:bg-white/5 transition-colors",
                  getCategoryColor(memory.metadata.category)
                )}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className={cn("text-xs uppercase font-bold px-2 py-0.5 rounded bg-black/30", getCategoryColor(memory.metadata.category))}>
                    {memory.metadata.category}
                  </span>
                  <button 
                    onClick={() => handleDelete(memory.id)}
                    className="text-gray-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed line-clamp-4 hover:line-clamp-none transition-all">
                  {memory.memory}
                </p>
                <div className="mt-4 pt-2 border-t border-gray-800 flex justify-between items-center text-xs text-gray-600">
                  <span>{new Date(memory.created_at).toLocaleDateString()}</span>
                  {memory.metadata.source && (
                    <span className="truncate max-w-[100px]">{memory.metadata.source}</span>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}
      
      {!loading && filteredMemories.length === 0 && (
        <div className="text-center py-20 text-gray-500">
          暂无相关记忆
        </div>
      )}
    </div>
  );
};

export default Memory;
