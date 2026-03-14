import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";
import assistantService, { type AssistantUsage } from "../../services/assistantService";

type MessageRole = "user" | "assistant";

interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;
}

const quickPrompts = [
  "Numerology reading for career growth",
  "Best muhurat guidance for business opening",
  "Relationship compatibility through numerology",
  "Suggest Vedic remedies based on my report",
  "Signature numerology improvement suggestions",
  "Which spiritual store items can support my current phase?",
];

export default function AstrologerChatPage() {
  const [usage, setUsage] = useState<AssistantUsage | null>(null);
  const [loadingUsage, setLoadingUsage] = useState(true);
  const [sending, setSending] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      text:
        "1. Core Reading\nWelcome to LifeSignify Assistant.\n\n2. Vedic + Numerology Guidance\nAsk about numerology, muhurat, rituals, compatibility, or store remedies.\n\n3. 3 Action Steps\n- Today: Pick one clear life focus.\n- This Week: Ask one specific guidance question.\n- This Month: Follow a consistent correction routine.",
    },
  ]);

  const refreshUsage = async () => {
    try {
      const data = await assistantService.getUsage();
      setUsage(data);
    } catch {
      toast.error("Unable to load assistant usage");
    } finally {
      setLoadingUsage(false);
    }
  };

  useEffect(() => {
    void refreshUsage();
  }, []);

  const submitMessage = async (message: string) => {
    const clean = message.trim();
    if (!clean || sending) return;

    setMessages((prev) => [
      ...prev,
      { id: `u-${Date.now()}`, role: "user", text: clean },
    ]);
    setDraft("");
    setSending(true);

    try {
      const result = await assistantService.sendMessage(clean);
      setMessages((prev) => [
        ...prev,
        { id: `a-${Date.now()}`, role: "assistant", text: result.message },
      ]);
      setUsage((prev) =>
        prev
          ? {
              ...prev,
              used_tokens: result.token_limit - result.remaining_tokens,
              remaining_tokens: result.remaining_tokens,
              token_limit: result.token_limit,
            }
          : prev
      );
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || "Assistant request failed");
    } finally {
      setSending(false);
    }
  };

  const topup = async (amount: 100 | 500) => {
    try {
      const next = await assistantService.topup(amount);
      setUsage(next);
      toast.success(`Token pack added: ₹${amount}`);
    } catch {
      toast.error("Top-up failed");
    }
  };

  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / LifeSignify Assistant"
        title="Domain-safe Vedic and Numerology assistant."
        description="The assistant is restricted to LifeSignify services only and follows deterministic-first guidance from your profile and reports."
        badges={["Domain-restricted", "Medical-safe", "Law-safe"]}
      />

      <section className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <DashboardCard title="Assistant chat" description="Strictly within LifeSignify Vedic, Numerology, Muhurat, Rituals, and Store guidance.">
          <div className="space-y-3">
            <div className="max-h-[420px] overflow-y-auto rounded-[16px] border border-white/10 bg-black/20 p-3">
              <div className="space-y-3">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`rounded-[12px] border p-3 text-sm whitespace-pre-wrap ${
                      message.role === "assistant"
                        ? "border-cyan-400/20 bg-cyan-400/5 text-slate-100"
                        : "border-white/10 bg-white/5 text-slate-200"
                    }`}
                  >
                    <p className="mb-1 text-[11px] uppercase tracking-[0.16em] text-slate-400">
                      {message.role === "assistant" ? "LifeSignify Assistant" : "You"}
                    </p>
                    {message.text}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              <input
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="Ask within LifeSignify scope..."
                className="register-input"
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    void submitMessage(draft);
                  }
                }}
              />
              <AnimatedButton loading={sending} onClick={() => void submitMessage(draft)}>
                Send
              </AnimatedButton>
            </div>
          </div>
        </DashboardCard>

        <div className="space-y-4">
          <DashboardCard title="Token usage" description="Free 1K tokens. Upgrade packs available.">
            {loadingUsage ? (
              <p className="type-body">Loading usage...</p>
            ) : usage ? (
              <div className="space-y-2">
                <p className="type-body">Used: {usage.used_tokens}</p>
                <p className="type-body">Remaining: {usage.remaining_tokens}</p>
                <p className="type-body">Limit: {usage.token_limit}</p>
                <div className="grid gap-2 pt-2">
                  <AnimatedButton variant="secondary" onClick={() => void topup(100)}>
                    Add ₹100 (5K tokens)
                  </AnimatedButton>
                  <AnimatedButton variant="success" onClick={() => void topup(500)}>
                    Add ₹500 (50K tokens)
                  </AnimatedButton>
                </div>
              </div>
            ) : (
              <p className="type-body">Usage unavailable.</p>
            )}
          </DashboardCard>

          <DashboardCard title="Quick prompts" description="Aligned with post-login service scope.">
            <div className="space-y-2">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => void submitMessage(prompt)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-left text-sm text-slate-200 transition hover:border-cyan-300/40 hover:bg-cyan-400/10"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </DashboardCard>
        </div>
      </section>
    </div>
  );
}
