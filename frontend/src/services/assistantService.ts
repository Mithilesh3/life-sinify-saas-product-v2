import API from "./api";

export interface AssistantUsage {
  used_tokens: number;
  remaining_tokens: number;
  token_limit: number;
  plans: Record<string, number>;
}

export interface AssistantChatResult {
  message: string;
  used_tokens: number;
  remaining_tokens: number;
  token_limit: number;
}

const assistantService = {
  getUsage: async () => {
    const res = await API.get<AssistantUsage>("/assistant/usage");
    return res.data;
  },

  sendMessage: async (message: string) => {
    const res = await API.post<AssistantChatResult>("/assistant/chat", { message });
    return res.data;
  },

  topup: async (amountInr: 100 | 500) => {
    const res = await API.post<AssistantUsage>("/assistant/topup", { amount_inr: amountInr });
    return res.data;
  },
};

export default assistantService;
