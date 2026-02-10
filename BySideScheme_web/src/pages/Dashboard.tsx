import React, { useEffect, useState } from 'react';
import { useUserStore } from '../store/userStore';
import { getSituation, resetSituation } from '../services/api';
import { motion } from 'framer-motion';
import { RefreshCw, Trash2, Edit } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { userId, situation, setSituation } = useUserStore();
  const [loading, setLoading] = useState(false);

  const fetchSituation = async () => {
    setLoading(true);
    try {
      const data = await getSituation(userId);
      setSituation(data.situation);
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
          <Link
            to="/profile"
            className="bg-surface border border-primary text-primary px-4 py-2 rounded hover:bg-primary hover:text-black transition-colors flex items-center gap-2"
          >
            <Edit size={16} />
            编辑局势
          </Link>
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
            <p className="text-3xl font-bold">{situation.current_level}</p>
          </motion.div>

          <motion.div variants={item} className="glass p-6 rounded-lg relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
               <span className="text-6xl font-bold">TG</span>
            </div>
            <h3 className="text-gray-400 text-sm mb-2">目标职级</h3>
            <p className="text-3xl font-bold text-primary">{situation.target_level}</p>
             <div className="mt-2 text-xs">
              晋升窗口: 
              <span className={situation.promotion_window ? "text-green-400 ml-1" : "text-gray-500 ml-1"}>
                {situation.promotion_window ? "开启" : "关闭"}
              </span>
            </div>
          </motion.div>

          <motion.div variants={item} className="glass p-6 rounded-lg relative overflow-hidden group">
            <h3 className="text-gray-400 text-sm mb-2">关键干系人</h3>
            <div className="space-y-1">
              {situation.stakeholders && situation.stakeholders.length > 0 ? (
                 situation.stakeholders.slice(0, 2).map((s, i) => (
                    <div key={i} className="text-sm">
                      <span className="font-bold">{s.name}</span>: {s.role}
                    </div>
                 ))
              ) : (
                <p className="text-sm text-gray-500">暂无干系人</p>
              )}
               {situation.stakeholders && situation.stakeholders.length > 2 && (
                  <p className="text-xs text-gray-500">+{situation.stakeholders.length - 2} 更多</p>
               )}
            </div>
          </motion.div>

          <motion.div variants={item} className="glass p-6 rounded-lg relative overflow-hidden group">
            <h3 className="text-gray-400 text-sm mb-2">当前阶段</h3>
            <p className="text-2xl font-bold text-secondary">{situation.current_phase}</p>
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
          <p className="text-gray-300 italic">"{situation.personal_goal}"</p>
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard;
