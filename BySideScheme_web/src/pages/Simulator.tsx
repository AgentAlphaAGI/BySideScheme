import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Users, User, Bot, Trash2, Play, RefreshCw, MessageSquare, PanelRightOpen, PanelRightClose } from 'lucide-react';
import { startSimulation, resetSimulation, startChatJob } from '../services/api';
import { ChatMessage, SimulatorInitRequest, Analysis, PersonConfig } from '../types';
import { cn } from '../utils/cn';
import AnalysisPanel from '../components/AnalysisPanel';
import PersonaHistoryModal from '../components/PersonaHistoryModal';
import { useUserStore } from '../store/userStore';

const API_BASE_URL = 'http://localhost:8001';

const Simulator = () => {
  const userId = useUserStore((state) => state.userId);
  const storeUserName = useUserStore((state: any) => state.user_name || "Me");
  
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(true);
  
  // Modal state
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [selectedPersonForHistory, setSelectedPersonForHistory] = useState<string | null>(null);
  
  const [config, setConfig] = useState<SimulatorInitRequest>({
    user_name: storeUserName,
    user_id: userId,
    people: [
      {
        kind: 'leader',
        name: "David",
        title: "直属领导",
        persona: "风险厌恶型，耳根子软，怕担责，看重数据。关系：摇摆不定。影响力：High",
        engine: "deepseek"
      },
      {
        kind: 'colleague',
        name: "Alex",
        title: "隔壁组长",
        persona: "竞争对手。笑面虎，抢功甩锅型，喜欢在群里@人。关系：敌对。影响力：Medium",
        engine: "deepseek"
      },
      {
        kind: 'colleague',
        name: "Jessica",
        title: "产品经理",
        persona: "合作方。强势，老板红人，喜欢用“用户价值”压技术。关系：合作但紧张。影响力：Medium",
        engine: "deepseek"
      }
    ]
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleStart = async () => {
    setIsLoading(true);
    try {
      const res = await startSimulation({
        ...config,
        user_id: userId // Ensure userId is passed
      });
      setSessionId(res.session_id);
      setMessages([{
        sender: "System",
        content: `模拟器已启动。当前场景：${config.people?.map(c => `${c.name} (${c.title || c.kind})`).join(', ')} 已上线。`,
        role: "system",
        timestamp: Date.now()
      }]);
      setAnalysis(null);
    } catch (error) {
      console.error("Failed to start simulation:", error);
      setMessages(prev => [...prev, {
        sender: "System",
        content: "启动失败，请检查后端服务。",
        role: "system",
        timestamp: Date.now()
      }]);
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
    setAnalysis(null);
    setInput('');
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;

    const userMsg: ChatMessage = {
      sender: config.user_name,
      content: input,
      role: "user",
      timestamp: Date.now()
    };

    // Optimistically add user message to UI
    // Note: We need to handle potential duplication if the SSE stream also sends back the user message
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // Use Job API for streaming response
      const res = await startChatJob(sessionId, userMsg.content);
      const jobId = res.job_id;

      // Close previous connection if exists
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Start SSE
      const es = new EventSource(`${API_BASE_URL}/simulator/jobs/${jobId}/stream`);
      eventSourceRef.current = es;

      es.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Skip if the message is from the user themselves (to avoid duplication with optimistic update)
          // The backend might send back the user's message as part of the group chat history
          if (data.sender === config.user_name || data.role === 'user') {
            return;
          }

          setMessages(prev => {
            // Check if message already exists to avoid duplicates
            const exists = prev.some(m => m.content === data.content && m.sender === data.sender);
            if (exists) return prev;
            
            return [...prev, {
              ...data,
              timestamp: Date.now()
            }];
          });
        } catch (e) {
          console.error("Error parsing SSE message:", e);
        }
      });

      es.addEventListener('analysis', (event) => {
        try {
          const data = JSON.parse(event.data);
          setAnalysis(data);
        } catch (e) {
          console.error("Error parsing SSE analysis:", e);
        }
      });

      es.addEventListener('status', (event) => {
         // Handle status updates if needed
         console.log("Job status:", event.data);
      });

      es.addEventListener('done', () => {
        setIsLoading(false);
        es.close();
        eventSourceRef.current = null;
      });

      es.onerror = (err) => {
        console.error("SSE Error:", err);
        setIsLoading(false);
        es.close();
        eventSourceRef.current = null;
      };

    } catch (error) {
      console.error("Failed to start chat job:", error);
      setMessages(prev => [...prev, {
        sender: "System",
        content: "发送失败，请重试。",
        role: "system",
        timestamp: Date.now()
      }]);
      setIsLoading(false);
    }
  };

  const handleOpenHistory = (personName: string) => {
    setSelectedPersonForHistory(personName);
    setHistoryModalOpen(true);
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
            基于 AutoGen 的多智能体职场演练场。与具有独立记忆的 AI 同事和领导切磋。autogen需要多轮洞察和思考,慢是正常的,请耐心等待
          </p>
        </div>
        
        <div className="flex gap-2">
           <button
            onClick={() => setShowAnalysis(!showAnalysis)}
            className={cn(
              "p-2 rounded-lg border transition-all",
              showAnalysis 
                ? "bg-neon-blue/20 text-neon-blue border-neon-blue/50" 
                : "bg-black/40 text-gray-400 border-white/10 hover:text-white"
            )}
            title="Toggle Analysis Panel"
          >
            {showAnalysis ? <PanelRightClose className="w-5 h-5" /> : <PanelRightOpen className="w-5 h-5" />}
          </button>
          
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
        <div className="w-64 glass-panel p-4 flex flex-col gap-4 overflow-y-auto hidden lg:flex flex-shrink-0">
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
              <div className="text-sm text-gray-400">参与者 (Participants)</div>
              {config.people?.map((person, idx) => (
                <div key={idx} className="p-3 bg-black/40 rounded-lg border border-neon-red/20 relative group">
                  <button
                    onClick={() => handleOpenHistory(person.name)}
                    className="absolute top-2 right-2 p-1 text-gray-500 hover:text-white opacity-0 group-hover:opacity-100 transition-all"
                    title="查看画像演进历史"
                  >
                    <RefreshCw className="w-3 h-3" />
                  </button>
                  <div className="font-medium text-neon-red flex items-center gap-2">
                    <User className="w-3 h-3" />
                    {person.name} <span className="text-xs text-gray-400">({person.title || person.kind})</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                     Engine: {person.engine || 'Default'}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 leading-relaxed line-clamp-3" title={person.persona}>
                    {person.persona}
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

        {/* Chat Area (Center) */}
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
        
        {/* Analysis Panel (Right) */}
        {showAnalysis && (
          <motion.div 
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 320, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="glass-panel flex flex-col overflow-hidden"
          >
             <div className="flex items-center gap-2 text-neon-purple font-semibold border-b border-white/10 p-4 pb-2">
                <Bot className="w-4 h-4" />
                实时洞察
              </div>
             <AnalysisPanel analysis={analysis} />
           </motion.div>
         )}
      </div>

      {userId && selectedPersonForHistory && (
        <PersonaHistoryModal
          userId={userId}
          personName={selectedPersonForHistory}
          isOpen={historyModalOpen}
          onClose={() => setHistoryModalOpen(false)}
        />
      )}
    </div>
  );
};

export default Simulator;
