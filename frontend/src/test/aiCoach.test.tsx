import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import * as React from "react";

import { AuthContext } from "../contexts/AuthContext";
import AICoachPage from "../pages/aiCoach/AICoachPage";
import { aiCoachService } from "../services/aiCoachService";
import type { AuthContextValue } from "../types/auth";

vi.mock("../services/aiCoachService", () => {
  return {
    aiCoachService: {
      getAvailability: vi.fn(),
      getConversations: vi.fn(),
      getConversation: vi.fn(),
      createConversation: vi.fn(),
      sendMessage: vi.fn(),
      closeConversation: vi.fn(),
      deleteConversation: vi.fn(),
    },
  };
});

vi.mock("../contexts/LocaleContext", () => {
  return {
    useLocale: () => ({
      locale: "en",
      setLocale: vi.fn(),
    }),
    LocaleProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

vi.mock("../theme", () => {
  return {
    useTheme: () => ({
      theme: "light",
      toggleTheme: vi.fn(),
    }),
    ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

function context(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: {
      id: "test-user",
      email: "user@example.com",
      is_active: true,
      created_at: "2026-07-16T12:00:00Z",
    },
    isLoading: false,
    error: null,
    login: vi.fn(),
    register: vi.fn(),
    loginWithGoogle: vi.fn(),
    logout: vi.fn(),
    clearError: vi.fn(),
    ...overrides,
  };
}

describe("AI Coach Page tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders availability error when AI is configured as unavailable", async () => {
    vi.mocked(aiCoachService.getAvailability).mockResolvedValue({ status: "unavailable" });

    render(
      <AuthContext.Provider value={context()}>
        <MemoryRouter>
          <AICoachPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    await waitFor(() => {
      expect(screen.getByText(/AI Coach is currently unavailable/i)).toBeInTheDocument();
    });
  });

  it("renders conversation history and suggested prompts empty state", async () => {
    vi.mocked(aiCoachService.getAvailability).mockResolvedValue({ status: "available" });
    vi.mocked(aiCoachService.getConversations).mockResolvedValue({
      items: [
        {
          id: "conv-1",
          title: "My Fitness Goals",
          status: "active",
          created_at: "2026-07-16T12:00:00Z",
          updated_at: "2026-07-16T12:00:00Z",
          last_activity_at: "2026-07-16T12:00:00Z",
          closed_at: null,
          last_message_at: null,
          message_count: 0,
          schema_version: 1,
        },
      ],
      limit: 10,
      offset: 0,
      has_more: false,
    });
    vi.mocked(aiCoachService.getConversation).mockResolvedValue({
      id: "conv-1",
      title: "My Fitness Goals",
      status: "active",
      created_at: "2026-07-16T12:00:00Z",
      updated_at: "2026-07-16T12:00:00Z",
      last_activity_at: "2026-07-16T12:00:00Z",
      closed_at: null,
      last_message_at: null,
      message_count: 0,
      schema_version: 1,
      messages: [],
      message_history_limit: 50,
      messages_truncated: false,
    });

    render(
      <AuthContext.Provider value={context()}>
        <MemoryRouter>
          <AICoachPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "My Fitness Goals" })).toBeInTheDocument();
      expect(screen.getByText("Suggested topics:")).toBeInTheDocument();
    });
  });

  it("sends user message and displays replies", async () => {
    vi.mocked(aiCoachService.getAvailability).mockResolvedValue({ status: "available" });
    vi.mocked(aiCoachService.getConversations).mockResolvedValue({
      items: [
        {
          id: "conv-1",
          title: "My Fitness Goals",
          status: "active",
          created_at: "2026-07-16T12:00:00Z",
          updated_at: "2026-07-16T12:00:00Z",
          last_activity_at: "2026-07-16T12:00:00Z",
          closed_at: null,
          last_message_at: null,
          message_count: 1,
          schema_version: 1,
        },
      ],
      limit: 10,
      offset: 0,
      has_more: false,
    });
    vi.mocked(aiCoachService.getConversation).mockResolvedValueOnce({
      id: "conv-1",
      title: "My Fitness Goals",
      status: "active",
      created_at: "2026-07-16T12:00:00Z",
      updated_at: "2026-07-16T12:00:00Z",
      last_activity_at: "2026-07-16T12:00:00Z",
      closed_at: null,
      last_message_at: null,
      message_count: 0,
      schema_version: 1,
      messages: [],
      message_history_limit: 50,
      messages_truncated: false,
    });

    render(
      <AuthContext.Provider value={context()}>
        <MemoryRouter>
          <AICoachPage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Ask your AI Coach...")).toBeInTheDocument();
    });

    vi.mocked(aiCoachService.sendMessage).mockResolvedValue({
      conversation_id: "conv-1",
      capability: "explain_workout",
      safety_decision: "allow",
      created_at: "2026-07-16T12:01:00Z",
      user_message: {
        id: "msg-1",
        conversation_id: "conv-1",
        role: "user",
        content: "What is my plan?",
        source: "user",
        created_at: "2026-07-16T12:00:59Z",
        schema_version: 1,
      },
      assistant_message: {
        id: "msg-2",
        conversation_id: "conv-1",
        role: "assistant",
        content: "This is the coach reply.",
        source: "application",
        created_at: "2026-07-16T12:01:00Z",
        schema_version: 1,
      },
    });

    vi.mocked(aiCoachService.getConversation).mockResolvedValue({
      id: "conv-1",
      title: "My Fitness Goals",
      status: "active",
      created_at: "2026-07-16T12:00:00Z",
      updated_at: "2026-07-16T12:01:00Z",
      last_activity_at: "2026-07-16T12:01:00Z",
      closed_at: null,
      last_message_at: null,
      message_count: 2,
      schema_version: 1,
      messages: [
        {
          id: "msg-1",
          conversation_id: "conv-1",
          role: "user",
          content: "Hello Coach",
          source: "user",
          created_at: "2026-07-16T12:00:00Z",
          schema_version: 1,
        },
        {
          id: "msg-2",
          conversation_id: "conv-1",
          role: "assistant",
          content: "This is the coach reply.",
          source: "application",
          created_at: "2026-07-16T12:01:00Z",
          schema_version: 1,
        },
      ],
      message_history_limit: 50,
      messages_truncated: false,
    });

    const inputEl = screen.getByPlaceholderText("Ask your AI Coach...");
    fireEvent.change(inputEl, { target: { value: "Hello Coach" } });
    const sendBtn = screen.getByRole("button", { name: /send/i });
    fireEvent.click(sendBtn);
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(screen.getByText("This is the coach reply.")).toBeInTheDocument();
      expect(aiCoachService.sendMessage).toHaveBeenCalledTimes(1);
    });
  });
});
