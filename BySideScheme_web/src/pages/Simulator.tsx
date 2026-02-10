import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Users, User, Bot, Trash2, Play, RefreshCw, MessageSquare } from 'lucide-react';
import { startSimulation, chatSimulation, resetSimulation } from '../services/api';
import { ChatMessage, SimulatorInitRequest } from '../types';
import { cn } from '../utils/cn';

const Simulator = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [config, setConfig] = useState<SimulatorInitRequest>({
    user_name: "Me",
    leaders: [
      {
        name: "David",
        title: "直属领导",
        persona: "控制欲强，喜欢听好话，但关键时刻能扛事。口头禅是'抓手'、'赋能'、'闭环'。"
      },
      {
        name: "Sarah",
        title: "部门总监",
        persona: "结果导向，雷厉风行，不喜欢听借口，只看数据。"
      }
    ]
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleStart = async () => {
    setIsLoading(true);
    try {
      const res = await startSimulation(config);
      setSessionId(res.session_id);
      setMessages([{
        sender: "System",
        content: `模拟器已启动。当前场景：${config.leaders.map(c => `${c.name} (${c.title})`).join(', ')} 已上线。`,
        role: "system",
        timestamp: Date.now()
      }]);
    } catch (error) {
      console.error("Failed to start simulation:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    if (sessionId) {
      try {
        await resetSimulation(sessionId);
      } catch (e) {
        console.error(e);
      }
    }
    setSessionId(null);
    setMessages([]);
    setInput('');
  };

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;

    const userMsg: ChatMessage = {
      sender: config.user_name,
      content: input,
      role: "user",
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await chatSimulation(sessionId, userMsg.content);
      const newMsgs = res.new_messages.map(m => ({
        ...m,
        timestamp: Date.now()
      }));
      setMessages(prev => [...prev, ...newMsgs]);
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages(prev => [...prev, {
        sender: "System",
        content: "发送失败，请重试。",
        role: "system",
        timestamp: Date.now()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 h-[calc(100vh-120px)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-neon-purple to-neon-blue">
            职场模拟器 (Simulator)
          </h1>
          <p className="text-gray-400 mt-2">
            基于 AutoGen 的多智能体职场演练场。与具有独立记忆的 AI 同事和领导切磋。
          </p>
        </div>
        
        <div className="flex gap-2">
          {!sessionId ? (
            <button
              onClick={handleStart}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-neon-purple/20 text-neon-purple border border-neon-purple/50 rounded-lg hover:bg-neon-purple/30 transition-all disabled:opacity-50"
            >
              <Play className="w-4 h-4" />
              启动模拟
            </button>
          ) : (
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 bg-red-500/20 text-red-400 border border-red-500/50 rounded-lg hover:bg-red-500/30 transition-all"
            >
              <RefreshCw className="w-4 h-4" />
              重置
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Config Panel (Left) */}
        <div className="w-80 glass-panel p-4 flex flex-col gap-4 overflow-y-auto hidden md:flex">
          <div className="flex items-center gap-2 text-neon-blue font-semibold border-b border-white/10 pb-2">
            <Users className="w-4 h-4" />
            角色配置
          </div>
          
          <div className="space-y-4">
            <div className="p-3 bg-black/40 rounded-lg border border-white/5">
              <div className="text-sm text-gray-400 mb-1">我的角色</div>
              <div className="font-medium text-white">{config.user_name}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm text-gray-400">领导 (Leaders)</div>
              {config.leaders.map((leader, idx) => (
                <div key={idx} className="p-3 bg-black/40 rounded-lg border border-neon-red/20">
                  <div className="font-medium text-neon-red flex items-center gap-2">
                    <User className="w-3 h-3" />
                    {leader.name} <span className="text-xs text-gray-400">({leader.title})</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1 leading-relaxed">
                    {leader.persona}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {!sessionId && (
            <div className="mt-auto text-xs text-gray-500 text-center">
              点击右上角“启动模拟”开始
            </div>
          )}
        </div>

        {/* Chat Area (Right) */}
        <div className="flex-1 glass-panel flex flex-col overflow-hidden relative">
          {!sessionId && messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 gap-4">
              <MessageSquare className="w-16 h-16 opacity-20" />
              <p>等待启动...</p>
            </div>
          ) : (
            <>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
                <AnimatePresence>
                  {messages.map((msg, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={cn(
                        "flex flex-col max-w-[80%]",
                        msg.role === 'user' ? "ml-auto items-end" : "mr-auto items-start",
                        msg.role === 'system' ? "mx-auto items-center max-w-full" : ""
                      )}
                    >
                      {msg.role !== 'system' && (
                        <span className="text-xs text-gray-500 mb-1 px-1">
                          {msg.sender}
                        </span>
                      )}
                      
                      <div className={cn(
                        "p-3 rounded-2xl text-sm leading-relaxed",
                        msg.role === 'user' 
                          ? "bg-neon-blue/20 text-white rounded-tr-none border border-neon-blue/30" 
                          : msg.role === 'system'
                            ? "bg-white/5 text-gray-400 text-xs rounded-lg px-4 py-1"
                            : "bg-black/40 text-gray-200 rounded-tl-none border border-white/10"
                      )}>
                        {msg.content}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                {isLoading && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2 text-gray-500 text-xs ml-4"
                  >
                    <div className="w-2 h-2 bg-neon-green rounded-full animate-pulse" />
                    对方正在输入...
                  </motion.div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-4 border-t border-white/10 bg-black/20 backdrop-blur-sm">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                    placeholder={sessionId ? "输入消息..." : "请先启动模拟"}
                    disabled={!sessionId || isLoading}
                    className="flex-1 bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-neon-blue/50 disabled:opacity-50 placeholder:text-gray-600"
                  />
                  <button
                    onClick={handleSend}
                    disabled={!sessionId || isLoading || !input.trim()}
                    className="p-2 bg-neon-blue/20 text-neon-blue rounded-lg border border-neon-blue/30 hover:bg-neon-blue/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Simulator;
