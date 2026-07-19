import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare,
  Send,
  Plus,
  Trash2,
  Lock,
  Loader2,
  AlertTriangle,
  Heart,
} from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { useAuth } from "../../hooks/useAuth";
import { dashboardCopy } from "../../i18n/dashboard";
import { DashboardHeader } from "../../components/dashboard/DashboardHeader";
import { Button } from "../../components/ui";
import { aiCoachService, type AIConversation, type AIMessage } from "../../services/aiCoachService";
import { ApiError } from "../../services/apiClient";

export default function AICoachPage() {
  const { locale } = useLocale();
  const { user } = useAuth();
  const copy = dashboardCopy[locale];
  const messageSendingEnabled = true;

  const [available, setAvailable] = useState<boolean>(true);
  const [conversations, setConversations] = useState<AIConversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [composerError, setComposerError] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);

  // 1. Check AI coach availability and load conversations
  const loadConversations = useCallback(async () => {
    try {
      const avail = await aiCoachService.getAvailability();
      setAvailable(avail.status === "available");
      if (avail.status === "available") {
        const list = await aiCoachService.getConversations();
        setConversations(list.items);
        if (list.items.length > 0 && !selectedId) {
          setSelectedId(list.items[0].id);
        }
      }
    } catch {
      setError(copy.unavailableState);
    } finally {
      setLoading(false);
    }
  }, [selectedId, copy.unavailableState]);

  useEffect(() => {
    const task = window.setTimeout(() => void loadConversations(), 0);
    return () => window.clearTimeout(task);
  }, [loadConversations]);

  // 2. Load messages for selected conversation
  const loadMessages = useCallback(
    async (id: string) => {
      try {
        const detail = await aiCoachService.getConversation(id);
        setMessages(detail.messages);
        // Update selected conversation in list status/title if needed
        setConversations((prev) =>
          prev.map((c) => (c.id === id ? { ...c, status: detail.status } : c)),
        );
      } catch {
        setError(copy.unavailableState);
      }
    },
    [copy.unavailableState],
  );

  useEffect(() => {
    const task = window.setTimeout(() => {
      if (selectedId) {
        void loadMessages(selectedId);
      } else {
        setMessages([]);
      }
    }, 0);
    return () => window.clearTimeout(task);
  }, [selectedId, loadMessages]);

  // 3. Scroll to bottom when messages or loading state changes
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, submitting]);

  // 4. Create new conversation
  const handleCreateConversation = async () => {
    setError(null);
    try {
      const title = locale === "ar" ? "محادثة جديدة" : "New conversation";
      const created = await aiCoachService.createConversation(title);
      setConversations((prev) => [created, ...prev]);
      setSelectedId(created.id);
    } catch {
      setError(copy.unavailableState);
    }
  };

  // 5. Close conversation
  const handleCloseConversation = async (id: string) => {
    setError(null);
    try {
      const closed = await aiCoachService.closeConversation(id);
      setConversations((prev) => prev.map((c) => (c.id === id ? closed : c)));
    } catch {
      setError(copy.unavailableState);
    }
  };

  // 6. Delete conversation
  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setError(null);
    try {
      await aiCoachService.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (selectedId === id) {
        setSelectedId(null);
      }
    } catch {
      setError(copy.unavailableState);
    }
  };

  // 7. Send user message
  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || !selectedId || submitting) {
      if (!text) setComposerError(locale === "ar" ? "اكتب رسالة قبل الإرسال." : "Write a message before sending.");
      return;
    }
    if (text.length > 2000) {
      setComposerError(locale === "ar" ? "يجب ألا تتجاوز الرسالة 2000 حرف." : "Messages must be 2,000 characters or fewer.");
      return;
    }

    setError(null);
    setComposerError(null);
    setSubmitting(true);
    if (!textToSend) setInput("");

    // Optimistically add user message locally
    const tempUserMsg: AIMessage = {
      id: "temp-user-msg-" + Date.now(),
      conversation_id: selectedId,
      role: "user",
      content: text,
      source: "user",
      created_at: new Date().toISOString(),
      schema_version: 1,
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await aiCoachService.sendMessage(selectedId, text);
      await loadMessages(selectedId);
      if (
        response &&
        (response.safety_decision === "refuse" ||
          response.safety_decision === "professional_guidance_required")
      ) {
        setError(copy.safetyNoticeHeader);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message || copy.safetyNoticeHeader);
        const safetyNotice: AIMessage = {
          id: "temp-safety-" + Date.now(),
          conversation_id: selectedId,
          role: "system_notice",
          content:
            err.message ||
            "The Rahafit Safety Engine has refused this request to maintain medical guidelines.",
          source: "lifecycle",
          created_at: new Date().toISOString(),
          schema_version: 1,
        };
        setMessages((prev) => [...prev, safetyNotice]);
      } else {
        setError(copy.unavailableState);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const selectedConv = conversations.find((c) => c.id === selectedId);
  const isClosed = selectedConv?.status === "closed";

  if (loading) {
    return (
      <div className="coach-layout" style={{ justifyContent: "center", alignItems: "center" }}>
        <Loader2 className="animate-spin text-teal-600" size={32} />
      </div>
    );
  }

  return (
    <div className="dashboard-root" dir={locale === "ar" ? "rtl" : "ltr"}>
      <DashboardHeader displayName={user?.email || "User"} email={user?.email} />

      <motion.main
        className="coach-layout"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* Sidebar */}
        <aside className="coach-sidebar">
          <div className="coach-sidebar-header">
            <Button
              className="ds-button ds-button-primary w-full"
              style={{ display: "flex", gap: "8px", justifyContent: "center" }}
              onClick={handleCreateConversation}
              disabled={!available}
            >
              <Plus size={18} />
              <span>{copy.newConversation}</span>
            </Button>
          </div>

          <div className="coach-sidebar-scroll">
            {conversations.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-sm">{copy.noConversations}</div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`coach-conv-item ${selectedId === conv.id ? "active" : ""}`}
                  onClick={() => setSelectedId(conv.id)}
                >
                  <div className="coach-conv-info">
                    <span className="coach-conv-title">{conv.title}</span>
                    <span className="coach-conv-meta">
                      <span
                        className={`inline-block w-2 h-2 rounded-full ${
                          conv.status === "active" ? "bg-teal-500" : "bg-slate-400"
                        }`}
                      />
                      <span>
                        {conv.status === "active" ? copy.activeStatus : copy.closedStatus}
                      </span>
                    </span>
                  </div>
                  <div className="flex gap-2">
                    {conv.status === "active" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          void handleCloseConversation(conv.id);
                        }}
                        title={copy.closeConversationBtn}
                        aria-label={copy.closeConversationBtn}
                      >
                        <Lock size={14} />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => void handleDeleteConversation(conv.id, e)}
                      title={copy.deleteConversationBtn}
                      aria-label={copy.deleteConversationBtn}
                      className="text-red-500 hover:bg-red-50"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>

        {/* Chat Area */}
        <section className="coach-chat-panel">
          {/* Header */}
          <div className="coach-chat-header">
            <div className="flex items-center gap-3">
              <MessageSquare className="text-teal-600" size={20} />
              <h2 className="text-base font-bold text-slate-800">
                {selectedConv ? selectedConv.title : copy.aiCoachTitle}
              </h2>
            </div>
            {isClosed && (
              <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-xs font-bold">
                <Lock size={12} />
                <span>{copy.closedStatus}</span>
              </div>
            )}
          </div>
          {error && (
            <p className="px-4 py-2 text-sm text-red-700 bg-red-50" role="alert">
              {error}
            </p>
          )}

          {/* Messages Scroll Area */}
          <div className="coach-messages-container" ref={scrollRef}>
            {!available ? (
              <div className="coach-empty-state">
                <div className="coach-empty-icon bg-red-50 text-red-500">
                  <AlertTriangle size={24} />
                </div>
                <h3 className="text-lg font-bold text-slate-800">{copy.unavailableState}</h3>
              </div>
            ) : !selectedId ? (
              <div className="coach-empty-state">
                <div className="coach-empty-icon">
                  <Heart size={24} />
                </div>
                <h3 className="text-lg font-bold text-slate-800">
                  {locale === "ar"
                    ? "ابدأ التحدث مع مدربك الذكي"
                    : "Start chatting with your AI Coach"}
                </h3>
                <p className="text-sm text-slate-500">
                  {locale === "ar"
                    ? "انقر على محادثة جديدة على اليسار لبدء استشارتك الآمنة والمدعومة بالتقارير الصحية."
                    : "Click New Chat on the sidebar to start your secure health-backed consultation."}
                </p>
              </div>
            ) : messages.length === 0 ? (
              /* Suggested Prompts empty state */
              <div className="coach-empty-state" style={{ justifyContent: "flex-end", flex: 1 }}>
                <div className="w-full">
                  <h4 className="text-sm font-bold text-slate-500 mb-3 text-start">
                    {copy.suggestedPromptsHeader}
                  </h4>
                  <div className="coach-suggested-grid">
                    <button
                      className="coach-suggested-card"
                      onClick={() => void handleSendMessage(copy.suggestedPromptWorkout)}
                      disabled={!messageSendingEnabled}
                    >
                      {copy.suggestedPromptWorkout}
                    </button>
                    <button
                      className="coach-suggested-card"
                      onClick={() => void handleSendMessage(copy.suggestedPromptHydration)}
                      disabled={!messageSendingEnabled}
                    >
                      {copy.suggestedPromptHydration}
                    </button>
                    <button
                      className="coach-suggested-card"
                      onClick={() => void handleSendMessage(copy.suggestedPromptRest)}
                      disabled={!messageSendingEnabled}
                    >
                      {copy.suggestedPromptRest}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <AnimatePresence initial={false}>
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    className={`coach-message-row ${msg.role}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className={`coach-bubble ${msg.role}`}>
                      {msg.role === "system_notice" && (
                        <div className="flex items-center gap-2 mb-2 font-bold text-amber-700">
                          <AlertTriangle size={16} />
                          <span>{copy.safetyNoticeHeader}</span>
                        </div>
                      )}
                      <p className="m-0 text-sm whitespace-pre-wrap">{msg.content}</p>
                      <span className="coach-bubble-time">
                        {new Date(msg.created_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                  </motion.div>
                ))}

                {submitting && (
                  <motion.div
                    className="coach-message-row assistant"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <div className="coach-bubble assistant flex items-center gap-2">
                      <Loader2 className="animate-spin text-teal-600" size={16} />
                      <span className="text-sm text-slate-500 font-medium">
                        {locale === "ar" ? "المدرب يكتب..." : "Coach is typing..."}
                      </span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            )}
          </div>

          {/* Composer Form */}
          {selectedId && available && (
            <div className="coach-composer-container">
              {!messageSendingEnabled && (
                <p className="text-sm text-slate-500 font-medium" role="status">
                  {copy.readOnlyNotice}
                </p>
              )}
              {isClosed ? (
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-500 flex items-center gap-2">
                  <Lock size={16} />
                  <span>{copy.closedNotice}</span>
                </div>
              ) : (
                <form
                  className="coach-composer-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    void handleSendMessage();
                  }}
                >
                  <div className="coach-input-wrapper">
                    <label className="sr-only" htmlFor="coach-message">
                      {copy.inputPlaceholder}
                    </label>
                    <input
                      id="coach-message"
                      type="text"
                      className="coach-input"
                      placeholder={copy.inputPlaceholder}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      maxLength={2000}
                      disabled={submitting || !messageSendingEnabled}
                      aria-invalid={Boolean(composerError)}
                      aria-describedby={composerError ? "coach-message-error" : undefined}
                    />
                    {composerError ? <p id="coach-message-error" className="field-error">{composerError}</p> : null}
                  </div>
                  <Button
                    type="submit"
                    className="ds-button ds-button-primary"
                    aria-label={copy.sendButton}
                    disabled={submitting || !messageSendingEnabled}
                    style={{ height: "48px", width: "48px", borderRadius: "12px", padding: 0 }}
                  >
                    <Send
                      size={18}
                      style={{ transform: locale === "ar" ? "rotate(180deg)" : "none" }}
                    />
                  </Button>
                </form>
              )}
            </div>
          )}
        </section>
      </motion.main>
    </div>
  );
}
