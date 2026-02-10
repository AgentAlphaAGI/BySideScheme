import React, { useEffect, useState } from 'react';
import { useUserStore } from '../store/userStore';
import { getSituation, updateSituation, resetSituation } from '../services/api';
import { motion } from 'framer-motion';
import { Situation } from '../types';
import { RefreshCw, Save, Trash2 } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { userId, situation, setSituation } = useUserStore();
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Situation | null>(null);

  const fetchSituation = async () => {
    setLoading(true);
    try {
      const data = await getSituation(userId);
      setSituation(data.situation);
      setEditForm(data.situation);
    } catch (error) {
      console.error("Failed to fetch situation", error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (window.confirm('确定要重置局势吗？这将恢复到初始状态。')) {
      setLoading(true);
      try {
        await resetSituation(userId);
        await fetchSituation();
      } catch (error) {
        console.error("Failed to reset situation", error);
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchSituation();
  }, [userId]);

  const handleSave = async () => {
    if (!editForm) return;
    setLoading(true);
    try {
      await updateSituation(userId, editForm);
      setSituation(editForm);
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to update situation", error);
    } finally {
      setLoading(false);
    }
  };

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  if (loading && !situation) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold neon-text-purple">仪表板</h2>
        <div className="flex gap-2">
           <button 
            onClick={fetchSituation} 
            className="p-2 rounded-full hover:bg-white/10 transition-colors"
            title="刷新"
          >
            <RefreshCw className={loading ? "animate-spin" : ""} size={20} />
          </button>
          <button 
            onClick={handleReset} 
            className="p-2 rounded-full hover:bg-white/10 transition-colors text-red-400"
            title="重置局势"
          >
            <Trash2 size={20} />
          </button>
          {!isEditing ? (
            <button 
              onClick={() => setIsEditing(true)}
              className="bg-surface border border-primary text-primary px-4 py-2 rounded hover:bg-primary hover:text-black transition-colors"
            >
              编辑局势
            </button>
          ) : (
             <button 
              onClick={handleSave}
              className="bg-primary text-black px-4 py-2 rounded flex items-center gap-2 hover:bg-opacity-80 transition-colors"
            >
              <Save size={16} /> 保存
            </button>
          )}
        </div>
      </div>

      {situation && (
        <motion.div 
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          <motion.div variants={item} className="glass p-6 rounded-lg relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="text-6xl font-bold">LV</span>
            </div>
            <h3 className="text-gray-400 text-sm mb-2">当前职级</h3>
            {isEditing ? (
              <input 
                type="text" 
                value={editForm?.current_level}
                onChange={(e) => setEditForm(prev => prev ? {...prev, current_level: e.target.value} : null)}
                className="bg-black/30 border border-gray-600 rounded px-2 py-1 w-full text-xl"
              />
            ) : (
              <p className="text-3xl font-bold">{situation.current_level}</p>
            )}
          </motion.div>

          <motion.div variants={item} className="glass p-6 rounded-lg relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
               <span className="text-6xl font-bold">TG</span>
            </div>
            <h3 className="text-gray-400 text-sm mb-2">目标职级</h3>
            {isEditing ? (
              <input 
                type="text" 
                value={editForm?.target_level}
                onChange={(e) => setEditForm(prev => prev ? {...prev, target_level: e.target.value} : null)}
                className="bg-black/30 border border-gray-600 rounded px-2 py-1 w-full text-xl text-primary"
              />
            ) : (
              <p className="text-3xl font-bold text-primary">{situation.target_level}</p>
            )}
             <div className="mt-2 text-xs">
              晋升窗口: 
              {isEditing ? (
                <input 
                  type="checkbox" 
                  checked={editForm?.promotion_window}
                  onChange={(e) => setEditForm(prev => prev ? {...prev, promotion_window: e.target.checked} : null)}
                  className="ml-2"
                />
              ) : (
                <span className={situation.promotion_window ? "text-green-400 ml-1" : "text-gray-500 ml-1"}>
                  {situation.promotion_window ? "开启" : "关闭"}
                </span>
              )}
            </div>
          </motion.div>

          <motion.div variants={item} className="glass p-6 rounded-lg relative overflow-hidden group">
            <h3 className="text-gray-400 text-sm mb-2">老板风格</h3>
            {isEditing ? (
               <select 
                value={editForm?.boss_style}
                onChange={(e) => setEditForm(prev => prev ? {...prev, boss_style: e.target.value} : null)}
                className="bg-black/30 border border-gray-600 rounded px-2 py-1 w-full text-lg"
              >
                <option value="风险厌恶型">风险厌恶型</option>
                <option value="控制型">控制型</option>
                <option value="放权型">放权型</option>
                <option value="激进型">激进型</option>
              </select>
            ) : (
              <p className="text-2xl font-bold">{situation.boss_style}</p>
            )}
          </motion.div>

          <motion.div variants={item} className="glass p-6 rounded-lg relative overflow-hidden group">
            <h3 className="text-gray-400 text-sm mb-2">当前阶段</h3>
            {isEditing ? (
               <select 
                value={editForm?.current_phase}
                onChange={(e) => setEditForm(prev => prev ? {...prev, current_phase: e.target.value} : null)}
                className="bg-black/30 border border-gray-600 rounded px-2 py-1 w-full text-lg text-secondary"
              >
                <option value="观察期">观察期</option>
                <option value="冲刺期">冲刺期</option>
                <option value="平稳期">平稳期</option>
                <option value="动荡期">动荡期</option>
              </select>
            ) : (
              <p className="text-2xl font-bold text-secondary">{situation.current_phase}</p>
            )}
          </motion.div>
        </motion.div>
      )}
      
      {situation && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass p-6 rounded-lg mt-8"
        >
          <h3 className="text-xl font-bold mb-4">个人目标</h3>
          {isEditing ? (
            <textarea 
              value={editForm?.personal_goal}
              onChange={(e) => setEditForm(prev => prev ? {...prev, personal_goal: e.target.value} : null)}
              className="w-full bg-black/30 border border-gray-600 rounded p-2 text-gray-300"
              rows={2}
            />
          ) : (
            <p className="text-gray-300 italic">"{situation.personal_goal}"</p>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard;
