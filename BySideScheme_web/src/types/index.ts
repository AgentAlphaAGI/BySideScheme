export interface Stakeholder {
  name: string;
  role: string;
  style: string;
  relationship: string;
  influence_level: 'High' | 'Medium' | 'Low';
}

export interface Situation {
  career_type: string;
  current_level: string;
  target_level: string;
  promotion_window: boolean;
  stakeholders: Stakeholder[];
  current_phase: string;
  personal_goal: string;
  recent_events: string[];
}

export interface Decision {
  should_say: boolean;
  timing_check: string;
  strategic_intent: string;
  strategy_summary: string;
  future_impact?: string;
}

export interface Narrative {
  boss_version: string;
  self_version: string;
  strategy_hints: string;
  draft_email?: string; // Optional field for draft email
}

export interface ContextUsed {
  situation: string;
  memory: string;
}

export interface AdviceResponse {
  decision: Decision;
  narrative: Narrative;
  context_used: ContextUsed;
}

export interface Memory {
  id: string;
  user_id: string;
  memory: string;
  hash: string;
  metadata: {
    category: 'narrative' | 'political' | 'career_state' | 'commitment' | 'insight' | 'conversation';
    source?: string;
    risk_level?: string;
    phase?: string;
    status?: string;
    due_date?: string;
    sender?: string;
  };
  created_at: string;
  updated_at?: string;
}

export interface MemoryListResponse {
  memories: Memory[];
}

export interface ConsolidateResponse {
  message: string;
  insights: string[];
}

// Simulator Types
export interface PersonConfig {
  kind: 'leader' | 'colleague';
  name: string;
  title: string;
  persona: string;
  engine?: string;
}

export interface SimulatorInitRequest {
  user_id?: string;
  user_name: string;
  people?: PersonConfig[];
  leaders?: { // Backwards compatibility
    name: string;
    title: string;
    persona: string;
  }[];
}

export interface SimulatorRunRequest {
  user_id?: string;
  user_name: string;
  people?: PersonConfig[];
  leaders?: { // Backwards compatibility
    name: string;
    title: string;
    persona: string;
  }[];
  scenario: string;
  max_rounds: number;
}

export interface Risk {
  title: string;
  severity: 'high' | 'medium' | 'low';
  trigger: string;
  impact: string;
  evidence: string[];
  mitigation: string[];
}

export interface PersonaUpdate {
  person_name: string;
  deviation_detected: boolean;
  observed_traits: string[];
  trait_behavior_chain: string;
  evidence: string[];
  updated_persona: string;
  update_confidence: number;
}

export interface Analysis {
  situation_insights: string[];
  overall_risk_score: number;
  risks: Risk[];
  persona_updates: PersonaUpdate[];
  next_actions: string[];
  uncertainties: string[];
}

export interface SimulatorRunResponse {
  messages: ChatMessage[];
  analysis: Analysis;
}

export interface SimulatorInitResponse {
  session_id: string;
}

export interface ChatMessage {
  sender: string;
  content: string;
  role: string;
  timestamp?: number;
}

export interface ChatResponse {
  session_id: string;
  new_messages: ChatMessage[];
  analysis: Analysis;
}

// Job Types
export interface JobResponse {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  session_id: string;
  created_at: number;
  updated_at: number;
  error?: string | null;
}

export interface JobResultResponse {
  job_id: string;
  session_id: string;
  status: 'completed' | 'failed' | 'running' | 'pending';
  messages: ChatMessage[];
  analysis: Analysis | null;
  error?: string | null;
}

// Persona Version Types
export interface PersonaVersion {
  id: string;
  person_title: string;
  persona: string;
  deviation_summary: string;
  confidence: number;
  created_at: string;
}

export interface PersonaVersionsResponse {
  versions: PersonaVersion[];
}

export interface RollbackResponse {
  rolled_back_to: string;
  new_version_id: string;
}

// Feedback Types
export interface FeedbackRequest {
  user_id: string;
  fact: string;
  advice_result: AdviceResponse;
  rating: number;
  comment: string;
}

export interface FeedbackResponse {
  message: string;
  id: string;
}

// Memory Query
export interface MemoryQueryRequest {
  user_id: string;
  query: string;
  limit?: number;
}

// Graph Types
export interface GraphNode {
  id: string;
  name: string;
  type: 'Person' | 'Event' | 'Project' | 'Resource' | 'Organization';
  properties: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight: number;
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  evidence: string[];
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphChange {
  change_type: string;
  description: string;
  timestamp: string;
}

export interface KeyPlayer {
  name: string;
  centrality: number;
}

export interface GraphInsights {
  key_players: KeyPlayer[];
  risk_relations: GraphEdge[];
  recent_changes: { description: string; timestamp: string }[];
}

export interface GraphExtractRequest {
  text: string;
  situation_context?: string;
}

export interface GraphExtractResponse {
  message: string;
  extracted: {
    entities: { name: string; type: string; properties: Record<string, any> }[];
    relations: { source: string; target: string; type: string; properties: Record<string, any> }[];
  };
}
