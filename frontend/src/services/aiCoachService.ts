import { apiRequest } from "./apiClient";

export interface AIConversation {
  id: string;
  title: string;
  status: "active" | "closed" | "deleted";
  created_at: string;
  updated_at: string;
  last_activity_at: string;
  closed_at: string | null;
  last_message_at: string | null;
  message_count: number;
  schema_version: number;
}

export interface AIMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system_notice";
  content: string;
  source: "user" | "application" | "lifecycle";
  created_at: string;
  schema_version: number;
}

export interface AIConversationDetail extends AIConversation {
  messages: AIMessage[];
  message_history_limit: number;
  messages_truncated: boolean;
}

export interface AIConversationList {
  items: AIConversation[];
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface AIAvailability {
  status: "available" | "unavailable";
}

export interface AICoachMessageFlowResponse {
  conversation_id: string;
  user_message: AIMessage;
  assistant_message: AIMessage;
  capability: string;
  safety_decision: string;
  safe_reason_code?: string | null;
  provider_used?: string | null;
  created_at: string;
}

export const aiCoachService = {
  async getAvailability(options?: Parameters<typeof apiRequest>[1]): Promise<AIAvailability> {
    return apiRequest<AIAvailability>("/ai-coach/availability", options);
  },

  async getConversations(
    limit = 10,
    offset = 0,
    options?: Parameters<typeof apiRequest>[1],
  ): Promise<AIConversationList> {
    return apiRequest<AIConversationList>(
      `/ai-coach/conversations?limit=${limit}&offset=${offset}`,
      options,
    );
  },

  async createConversation(
    title?: string,
    options?: Parameters<typeof apiRequest>[1],
  ): Promise<AIConversation> {
    return apiRequest<AIConversation>("/ai-coach/conversations", {
      ...options,
      method: "POST",
      body: { title },
    });
  },

  async getConversation(
    id: string,
    options?: Parameters<typeof apiRequest>[1],
  ): Promise<AIConversationDetail> {
    return apiRequest<AIConversationDetail>(`/ai-coach/conversations/${id}`, options);
  },

  async closeConversation(
    id: string,
    options?: Parameters<typeof apiRequest>[1],
  ): Promise<AIConversation> {
    return apiRequest<AIConversation>(`/ai-coach/conversations/${id}/close`, {
      ...options,
      method: "POST",
    });
  },

  async deleteConversation(id: string, options?: Parameters<typeof apiRequest>[1]): Promise<void> {
    return apiRequest<void>(`/ai-coach/conversations/${id}`, {
      ...options,
      method: "DELETE",
    });
  },

  async sendMessage(
    conversationId: string,
    content: string,
    options?: Parameters<typeof apiRequest>[1],
  ): Promise<AICoachMessageFlowResponse> {
    return apiRequest<AICoachMessageFlowResponse>(
      `/ai-coach/conversations/${conversationId}/messages`,
      {
        ...options,
        method: "POST",
        body: { content },
      },
    );
  },

  async getMessages(
    conversationId: string,
    options?: Parameters<typeof apiRequest>[1],
  ): Promise<AIMessage[]> {
    return apiRequest<AIMessage[]>(`/ai-coach/conversations/${conversationId}/messages`, options);
  },
};
