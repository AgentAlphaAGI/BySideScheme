import React, { useState, useEffect } from 'react';
import { Situation, Stakeholder } from '../types';
import { Plus, Trash2, Save } from 'lucide-react';

interface SituationFormProps {
  initialSituation: Situation | null;
  onSave: (situation: Situation) => void;
  isLoading?: boolean;
}

const defaultSituation: Situation = {
  career_type: '互联网大厂',
  current_level: 'P6',
  target_level: 'P7',
  promotion_window: false,
  stakeholders: [],
  current_phase: '平稳期',
  personal_goal: '',
  recent_events: []
};

const SituationForm: React.FC<SituationFormProps> = ({ initialSituation, onSave, isLoading }) => {
  const [formData, setFormData] = useState<Situation>(defaultSituation);

  useEffect(() => {
    if (initialSituation) {
      setFormData(initialSituation);
    }
  }, [initialSituation]);

  const handleChange = (field: keyof Situation, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleStakeholderChange = (index: number, field: keyof Stakeholder, value: any) => {
    const newStakeholders = [...formData.stakeholders];
    newStakeholders[index] = { ...newStakeholders[index], [field]: value };
    handleChange('stakeholders', newStakeholders);
  };

  const addStakeholder = () => {
    const newStakeholder: Stakeholder = {
      name: '',
      role: '',
      style: '',
      relationship: '',
      influence_level: 'Medium'
    };
    handleChange('stakeholders', [...formData.stakeholders, newStakeholder]);
  };

  const removeStakeholder = (index: number) => {
    const newStakeholders = formData.stakeholders.filter((_, i) => i !== index);
    handleChange('stakeholders', newStakeholders);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Info */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">行业类型 (Career Type)</label>
          <input
            type="text"
            value={formData.career_type}
            onChange={e => handleChange('career_type', e.target.value)}
            className="w-full bg-black/30 border border-gray-700 rounded px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-gray-400">当前阶段 (Current Phase)</label>
          <input
            type="text"
            value={formData.current_phase}
            onChange={e => handleChange('current_phase', e.target.value)}
            className="w-full bg-black/30 border border-gray-700 rounded px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-gray-400">当前职级 (Current Level)</label>
          <input
            type="text"
            value={formData.current_level}
            onChange={e => handleChange('current_level', e.target.value)}
            className="w-full bg-black/30 border border-gray-700 rounded px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm text-gray-400">目标职级 (Target Level)</label>
          <input
            type="text"
            value={formData.target_level}
            onChange={e => handleChange('target_level', e.target.value)}
            className="w-full bg-black/30 border border-gray-700 rounded px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
          />
        </div>
        <div className="space-y-2 md:col-span-2">
          <label className="text-sm text-gray-400">个人目标 (Personal Goal)</label>
          <input
            type="text"
            value={formData.personal_goal}
            onChange={e => handleChange('personal_goal', e.target.value)}
            className="w-full bg-black/30 border border-gray-700 rounded px-4 py-2 text-white focus:outline-none focus:border-purple-500 transition-colors"
          />
        </div>
        <div className="flex items-center space-x-3 pt-2 md:col-span-2">
          <input
            type="checkbox"
            id="promotion_window"
            checked={formData.promotion_window}
            onChange={e => handleChange('promotion_window', e.target.checked)}
            className="w-5 h-5 rounded border-gray-700 bg-black/30 text-purple-500 focus:ring-purple-500"
          />
          <label htmlFor="promotion_window" className="text-sm text-gray-300">是否处于晋升窗口期</label>
        </div>
      </div>

      {/* Stakeholders */}
      <div className="space-y-4 pt-4 border-t border-gray-800">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-200">关键干系人 (Stakeholders)</h3>
          <button
            type="button"
            onClick={addStakeholder}
            className="flex items-center gap-1 text-sm text-purple-400 hover:text-purple-300 transition-colors"
          >
            <Plus size={16} /> 添加
          </button>
        </div>
        
        {formData.stakeholders.length === 0 && (
          <p className="text-sm text-gray-500 italic">暂无干系人信息，请添加</p>
        )}

        {formData.stakeholders.map((stakeholder, index) => (
          <div key={index} className="glass p-4 rounded-lg space-y-3 relative group">
            <button
              type="button"
              onClick={() => removeStakeholder(index)}
              className="absolute top-2 right-2 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <Trash2 size={16} />
            </button>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs text-gray-500">姓名</label>
                <input
                  value={stakeholder.name}
                  onChange={e => handleStakeholderChange(index, 'name', e.target.value)}
                  className="w-full bg-black/30 border border-gray-700 rounded px-3 py-1.5 text-sm text-white focus:border-purple-500 outline-none"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-gray-500">角色</label>
                <input
                  value={stakeholder.role}
                  onChange={e => handleStakeholderChange(index, 'role', e.target.value)}
                  className="w-full bg-black/30 border border-gray-700 rounded px-3 py-1.5 text-sm text-white focus:border-purple-500 outline-none"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-gray-500">行事风格</label>
                <input
                  value={stakeholder.style}
                  onChange={e => handleStakeholderChange(index, 'style', e.target.value)}
                  className="w-full bg-black/30 border border-gray-700 rounded px-3 py-1.5 text-sm text-white focus:border-purple-500 outline-none"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-gray-500">关系状态</label>
                <input
                  value={stakeholder.relationship}
                  onChange={e => handleStakeholderChange(index, 'relationship', e.target.value)}
                  className="w-full bg-black/30 border border-gray-700 rounded px-3 py-1.5 text-sm text-white focus:border-purple-500 outline-none"
                />
              </div>
              <div className="space-y-1 md:col-span-2">
                <label className="text-xs text-gray-500">影响力</label>
                <select
                  value={stakeholder.influence_level}
                  onChange={e => handleStakeholderChange(index, 'influence_level', e.target.value)}
                  className="w-full bg-black/30 border border-gray-700 rounded px-3 py-1.5 text-sm text-white focus:border-purple-500 outline-none"
                >
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="pt-6">
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save size={20} />
          {isLoading ? '保存中...' : '保存局势配置'}
        </button>
      </div>
    </form>
  );
};

export default SituationForm;
