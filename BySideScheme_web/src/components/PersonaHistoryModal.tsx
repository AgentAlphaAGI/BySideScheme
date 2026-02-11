import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, History, RotateCcw, Check } from 'lucide-react';
import { getPersonaVersions, rollbackPersona } from '../services/api';
import { PersonaVersion } from '../types';
import { cn } from '../utils/cn';

interface PersonaHistoryModalProps {
  userId: string;
  personName: string;
  isOpen: boolean;
  onClose: () => void;
}

const PersonaHistoryModal: React.FC<PersonaHistoryModalProps> = ({ 
  userId, 
  personName, 
  isOpen, 
  onClose 
}) => {
  const [versions, setVersions] = useState<PersonaVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [rollbacking, setRollbacking] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && userId && personName) {
      fetchVersions();
    }
  }, [isOpen, userId, personName]);

  const fetchVersions = async () => {
    setLoading(true);
    try {
      const res = await getPersonaVersions(userId, personName);
      setVersions(res.versions);
    } catch (error) {
      console.error("Failed to fetch persona versions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (versionId: string) => {
    if (!window.confirm('确定要回滚到此版本吗？这将创建一个新的版本记录。')) return;
    
    setRollbacking(versionId);
    try {
      await rollbackPersona(userId, personName, versionId);
      await fetchVersions(); // Refresh list
    } catch (error) {
      console.error("Failed to rollback:", error);
    } finally {
      setRollbacking(null);
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-[#1a1a1a] border border-white/10 rounded-xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-neon-purple" />
            画像演进历史: {personName}
          </h3>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
          {loading ? (
            <div className="text-center py-8 text-gray-500">加载中...</div>
          ) : versions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">暂无历史版本记录</div>
          ) : (
            versions.map((version, idx) => (
              <div key={version.id} className="bg-black/40 border border-white/5 rounded-lg p-4 hover:border-white/10 transition-colors relative group">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded">
                      {new Date(version.created_at).toLocaleString()}
                    </span>
                    {idx === 0 && (
                      <span className="text-xs text-green-400 bg-green-500/10 px-2 py-0.5 rounded border border-green-500/20">
                        Current
                      </span>
                    )}
                  </div>
                  {idx !== 0 && (
                    <button
                      onClick={() => handleRollback(version.id)}
                      disabled={!!rollbacking}
                      className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-xs text-neon-blue hover:text-white bg-neon-blue/10 px-2 py-1 rounded border border-neon-blue/20"
                    >
                      {rollbacking === version.id ? (
                        <span className="animate-pulse">回滚中...</span>
                      ) : (
                        <>
                          <RotateCcw className="w-3 h-3" /> 回滚至此
                        </>
                      )}
                    </button>
                  )}
                </div>

                <div className="space-y-3">
                  <div className="text-sm text-gray-300 leading-relaxed bg-black/20 p-3 rounded">
                    {version.persona}
                  </div>
                  
                  {version.deviation_summary && (
                    <div className="text-xs text-gray-400 border-l-2 border-neon-purple/30 pl-3">
                      <div className="font-semibold text-neon-purple mb-1">变更原因:</div>
                      {version.deviation_summary}
                      <div className="mt-1 text-gray-500">
                        置信度: {(version.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>,
    document.body
  );
};

export default PersonaHistoryModal;
