import React, { useState } from 'react';
import { useUserStore } from '../store/userStore';
import { User, LogOut } from 'lucide-react';

const Profile: React.FC = () => {
  const { userId, setUserId, setSituation } = useUserStore();
  const [inputUserId, setInputUserId] = useState(userId);

  const handleUpdateUser = () => {
    if (inputUserId.trim() && inputUserId !== userId) {
      if (window.confirm('切换用户将清空当前会话状态，确定吗？')) {
        setUserId(inputUserId);
        setSituation(null as any); // Force refresh situation on next dashboard load
        alert('用户已切换');
      }
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <h2 className="text-3xl font-bold neon-text-purple">个人中心</h2>
      
      <div className="glass p-8 rounded-lg">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-20 h-20 bg-gradient-to-tr from-primary to-secondary rounded-full flex items-center justify-center">
            <User size={40} className="text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-bold">User Profile</h3>
            <p className="text-gray-400">Manage your identity</p>
          </div>
        </div>

        <div className="space-y-4">
          <label className="block text-sm text-gray-400">当前用户 ID (User ID)</label>
          <div className="flex gap-4">
            <input 
              type="text" 
              value={inputUserId}
              onChange={(e) => setInputUserId(e.target.value)}
              className="flex-1 bg-black/30 border border-gray-700 rounded px-4 py-2 text-white focus:outline-none focus:border-primary"
            />
            <button 
              onClick={handleUpdateUser}
              className="bg-surface border border-gray-600 px-4 py-2 rounded hover:bg-white/10 transition-colors"
            >
              切换用户
            </button>
          </div>
          <p className="text-xs text-gray-500">
            * 这是一个演示版应用，用户系统基于 User ID 进行隔离。在实际生产环境中，这里会替换为完整的 OAuth 认证流程。
          </p>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-800">
          <button 
            className="flex items-center gap-2 text-red-400 hover:text-red-300 transition-colors"
            onClick={() => alert("Logout functionality would go here")}
          >
            <LogOut size={18} />
            退出登录
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;
