import axios from 'axios';
import { 
  Situation, 
  AdviceResponse, 
  MemoryListResponse, 
  ConsolidateResponse,
  MemoryQueryRequest,
  FeedbackRequest,
  FeedbackResponse,
  SimulatorRunRequest,
  SimulatorRunResponse
} from '../types';

const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const updateSituation = async (userId: string, situation: Situation) => {
  const response = await api.post('/situation/update', { user_id: userId, situation });
  return response.data;
};

export const getSituation = async (userId: string) => {
  const response = await api.get<{ situation: Situation }>(`/situation/${userId}`);
  return response.data;
};

export const resetSituation = async (userId: string) => {
  const response = await api.delete(`/situation/${userId}`);
  return response.data;
};

export const generateAdvice = async (userId: string, fact: string) => {
  const response = await api.post<AdviceResponse>('/advice/generate', { user_id: userId, fact });
  return response.data;
};

export const submitFeedback = async (feedback: FeedbackRequest) => {
  const response = await api.post<FeedbackResponse>('/feedback/submit', feedback);
  return response.data;
};

export const getMemories = async (userId: string) => {
  const response = await api.get<MemoryListResponse>(`/memory/${userId}/all`);
  return response.data;
};

export const queryMemories = async (request: MemoryQueryRequest) => {
  const response = await api.post<MemoryListResponse>('/memory/query', request);
  return response.data;
};

export const consolidateMemories = async (userId: string) => {
  const response = await api.post<ConsolidateResponse>(`/memory/${userId}/consolidate`);
  return response.data;
};

export const deleteMemory = async (userId: string, memoryId: string) => {
  const response = await api.delete(`/memory/${userId}/${memoryId}`);
  return response.data;
};

export const clearMemories = async (userId: string) => {
  const response = await api.delete(`/memory/${userId}`);
  return response.data;
};

// Simulator API
import { 
  SimulatorInitRequest, 
  SimulatorInitResponse, 
  ChatResponse, 
  JobResponse, 
  JobResultResponse, 
  PersonaVersionsResponse, 
  RollbackResponse 
} from '../types';

export const startSimulation = async (config: SimulatorInitRequest) => {
  const response = await api.post<SimulatorInitResponse>('/simulator/start', config);
  return response.data;
};

export const runSimulation = async (config: SimulatorRunRequest) => {
  const response = await api.post<SimulatorRunResponse>('/simulator/run', config);
  return response.data;
};

export const chatSimulation = async (sessionId: string, message: string) => {
  const response = await api.post<ChatResponse>('/simulator/chat', { session_id: sessionId, message });
  return response.data;
};

export const resetSimulation = async (sessionId: string) => {
  const response = await api.delete(`/simulator/reset/${sessionId}`);
  return response.data;
};

// Job API
export const startChatJob = async (sessionId: string, message: string) => {
  const response = await api.post<JobResponse>('/simulator/jobs/chat', { session_id: sessionId, message });
  return response.data;
};

export const startRunJob = async (config: SimulatorRunRequest) => {
  const response = await api.post<JobResponse>('/simulator/jobs/run', config);
  return response.data;
};

export const getJobStatus = async (jobId: string) => {
  const response = await api.get<JobResponse>(`/simulator/jobs/${jobId}/status`);
  return response.data;
};

export const getJobResult = async (jobId: string) => {
  const response = await api.get<JobResultResponse>(`/simulator/jobs/${jobId}/result`);
  return response.data;
};

// Persona API
export const getPersonaVersions = async (userId: string, personName: string) => {
  const response = await api.get<PersonaVersionsResponse>(`/simulator/persona/${userId}/${personName}/versions`);
  return response.data;
};

export const rollbackPersona = async (userId: string, personName: string, versionId: string) => {
  const response = await api.post<RollbackResponse>(`/simulator/persona/${userId}/${personName}/rollback`, { persona_version_id: versionId });
  return response.data;
};
