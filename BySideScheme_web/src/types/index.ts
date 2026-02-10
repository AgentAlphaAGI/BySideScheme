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
export interface SimulatorInitRequest {
  user_name: string;
  leaders: {
    name: string;
    title: string;
    persona: string;
  }[];
}

export interface SimulatorRunRequest {
  user_name: string;
  leaders: {
    name: string;
    title: string;
    persona: string;
  }[];
  scenario: string;
  max_rounds: number;
}

export interface SimulatorRunResponse {
  messages: ChatMessage[];
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
