import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Bot,
  CheckCircle2,
  ChevronDown,
  Clock3,
  LifeBuoy,
  Loader2,
  MapPin,
  MessageSquarePlus,
  RotateCcw,
  SendHorizontal,
  User,
} from "lucide-react";
import { sendMessage } from "../api";
import { ChatMessage } from "../types";
import { FacilityCard } from "./FacilityCard";
import { cn } from "../lib/utils";

const ZONES = [
  { id: "harbor_corner", name: "Bến Cảng Giao Thoa" },
  { id: "folk_culture_island", name: "Đảo Văn Hóa Dân Gian" },
  { id: "river_safari", name: "Khu River Safari" },
  { id: "adventure_land", name: "Vùng Đất Phiêu Lưu" },
  { id: "water_world", name: "Thế Giới Nước" },
  { id: "indoor_games", name: "Trò Chơi Trong Nhà" },
];

const ZONE_SUGGESTIONS: Record<string, string[]> = {
  harbor_corner: [
    "Tìm nhà hàng gần đây",
    "Nhà vệ sinh gần nhất",
    "Quầy hỗ trợ vé ở đâu",
  ],
  water_world: ["Thuê tủ đồ ở đâu", "Khát quá", "Nhà vệ sinh gần nhất"],
  adventure_land: ["Chỗ nghỉ chân", "Khát quá", "Nhà vệ sinh ở đâu"],
  river_safari: ["WC ở đâu", "Mua nước ở đâu", "Tôi cần sơ cứu"],
  indoor_games: [
    "Có quán nào cho trẻ em không",
    "Nhà vệ sinh gần nhất",
    "Khát quá",
  ],
  folk_culture_island: ["Ăn món Việt", "Đi vệ sinh", "Có quà lưu niệm không"],
};

const initialMessage =
  "Xin chào, mình đã sẵn sàng hỗ trợ điều phối điểm đến trong VinWonders Nam Hội An.";

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: "init", role: "assistant", content: initialMessage },
  ]);
  const [input, setInput] = useState("");
  const [zone, setZone] = useState("water_world");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(
    () => "sess_" + Math.random().toString(36).substring(7),
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const currentZone = useMemo(
    () => ZONES.find((item) => item.id === zone) ?? ZONES[0],
    [zone],
  );

  const lastAssistantResponse = [...messages]
    .reverse()
    .find((message) => message.role === "assistant" && message.response)?.response;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), role: "user", content: userMessage },
    ]);
    setIsLoading(true);

    const response = await sendMessage(userMessage, sessionId, zone);

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        role: "assistant",
        content: response.message,
        response,
      },
    ]);
    setIsLoading(false);
  };

  const clearChat = () => {
    setMessages([{ id: "init", role: "assistant", content: initialMessage }]);
  };

  return (
    <main className="min-h-screen bg-[linear-gradient(90deg,rgba(255,255,255,0.045)_1px,transparent_1px),linear-gradient(180deg,rgba(255,255,255,0.045)_1px,transparent_1px)] bg-[size:56px_56px] text-slate-950">
      <header className="border-b border-white/15 bg-[#06152a]/70 text-white shadow-[0_18px_60px_rgba(0,0,0,0.28)] backdrop-blur-2xl">
        <div className="mx-auto flex h-20 w-full max-w-7xl items-center justify-between px-4 md:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(0,87,184,0.92),rgba(18,179,168,0.82))] text-white shadow-[0_14px_40px_rgba(18,179,168,0.28)] ring-1 ring-white/25">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-vin-gold">
                VinWonders Nam Hội An
              </p>
              <h1 className="text-xl font-black tracking-tight text-white">
                Premium Guest Concierge
              </h1>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-teal-100 shadow-inner md:flex">
            <CheckCircle2 className="h-4 w-4" />
            API online
          </div>
        </div>
      </header>

      <div className="mx-auto grid min-h-[calc(100vh-80px)] w-full max-w-7xl gap-5 px-4 py-5 md:px-6 lg:grid-cols-[300px_minmax(0,1fr)_310px]">
        <aside className="space-y-4">
          <section className="overflow-hidden rounded-3xl border border-white/20 bg-white/[0.13] p-5 text-white shadow-[0_28px_90px_rgba(0,0,0,0.30)] backdrop-blur-2xl">
            <div className="mb-6 rounded-2xl border border-white/15 bg-[linear-gradient(135deg,rgba(0,87,184,0.82),rgba(18,179,168,0.48),rgba(247,201,72,0.18))] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.18)]">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-amber-100">
                Concierge mode
              </p>
              <h2 className="mt-2 text-2xl font-black leading-tight text-white">
                Curated park guidance
              </h2>
              <p className="mt-2 text-sm leading-6 text-white/75">
                Điều phối tiện ích theo khu vực, nhu cầu và mức ưu tiên của khách.
              </p>
            </div>
            <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-amber-100/80">
              Current zone
            </label>
            <div className="relative">
              <MapPin className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-vin-gold" />
              <select
                className="h-11 w-full appearance-none rounded-xl border border-white/20 bg-white/95 pl-9 pr-9 text-sm font-bold text-vin-ink outline-none transition focus:border-vin-gold focus:ring-4 focus:ring-amber-200/40"
                value={zone}
                onChange={(event) => setZone(event.target.value)}
              >
                {ZONES.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            </div>
          </section>

          <section className="rounded-3xl border border-white/20 bg-white/[0.86] p-4 shadow-[0_24px_70px_rgba(0,0,0,0.24)] backdrop-blur-2xl">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900">Quick prompts</h2>
              <MessageSquarePlus className="h-4 w-4 text-slate-400" />
            </div>
            <div className="space-y-2">
              {ZONE_SUGGESTIONS[zone]?.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="w-full rounded-xl border border-slate-200 bg-white/80 px-3 py-2.5 text-left text-sm font-semibold text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-vin-gold hover:bg-white hover:text-vin-blue hover:shadow-md"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/20 bg-white/[0.86] p-4 shadow-[0_24px_70px_rgba(0,0,0,0.22)] backdrop-blur-2xl">
            <h2 className="text-sm font-bold text-slate-900">Session</h2>
            <dl className="mt-3 space-y-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <dt className="text-slate-500">Zone</dt>
                <dd className="truncate font-semibold text-slate-900">
                  {currentZone.name}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-slate-500">Messages</dt>
                <dd className="font-semibold text-slate-900">{messages.length}</dd>
              </div>
            </dl>
          </section>
        </aside>

        <section className="flex min-h-[700px] flex-col overflow-hidden rounded-3xl border border-white/25 bg-white/[0.88] shadow-[0_34px_110px_rgba(0,0,0,0.38)] backdrop-blur-2xl">
          <div className="flex items-center justify-between border-b border-white/50 bg-[linear-gradient(135deg,rgba(255,255,255,0.96),rgba(239,246,255,0.82))] px-5 py-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-vin-blue/70">
                Live concierge thread
              </p>
              <h2 className="mt-1 text-xl font-black text-vin-ink">Conversation</h2>
              <p className="mt-1 text-sm text-slate-500">
                {currentZone.name}
              </p>
            </div>
            <button
              onClick={clearChat}
              className="inline-flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white/[0.85] px-3 text-sm font-bold text-slate-700 shadow-sm transition hover:border-vin-gold hover:bg-white hover:text-vin-blue"
              title="Làm mới"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </button>
          </div>

          <div className="flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top_right,rgba(0,87,184,0.10),transparent_34%),radial-gradient(circle_at_bottom_left,rgba(247,201,72,0.13),transparent_32%),linear-gradient(180deg,rgba(248,250,252,0.94),rgba(226,232,240,0.92))] px-4 py-5">
            <div className="mx-auto max-w-3xl space-y-5">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex gap-3",
                    message.role === "user" ? "justify-end" : "justify-start",
                  )}
                >
                  {message.role === "assistant" && (
                <Avatar tone="assistant">
                      <Bot className="h-4 w-4" />
                    </Avatar>
                  )}

                  <div
                    className={cn(
                      "max-w-[86%] md:max-w-[76%]",
                      message.role === "user" ? "order-1" : "order-2",
                    )}
                  >
                    <div
                      className={cn(
                        "rounded-lg px-4 py-3 text-sm leading-6 shadow-sm",
                        message.role === "user"
                          ? "bg-[linear-gradient(135deg,#0057B8,#123C69)] text-white shadow-[0_16px_42px_rgba(0,87,184,0.22)]"
                          : "border border-white/70 bg-white/90 text-slate-800 backdrop-blur",
                      )}
                    >
                      {message.content}
                    </div>

                    {message.response &&
                      (message.response.selected_facility ||
                        Boolean(message.response.alternatives?.length) ||
                        Boolean(message.response.cross_sell_facilities?.length)) && (
                        <div className="mt-3 space-y-3">
                          {message.response.selected_facility && (
                            <FacilityCard
                              facility={message.response.selected_facility}
                              navigation={message.response.navigation}
                            />
                          )}

                          {Boolean(
                            message.response.cross_sell_facilities?.length,
                          ) && (
                            <ResultGroup title="Nearby utilities">
                              {message.response.cross_sell_facilities?.map(
                                (facility) => (
                                  <FacilityCard
                                    key={facility.id}
                                    facility={facility}
                                    isAlternative
                                  />
                                ),
                              )}
                            </ResultGroup>
                          )}

                          {Boolean(message.response.alternatives?.length) && (
                            <ResultGroup title="Alternatives">
                              {message.response.alternatives?.map((facility) => (
                                <FacilityCard
                                  key={facility.id}
                                  facility={facility}
                                  isAlternative
                                />
                              ))}
                            </ResultGroup>
                          )}
                        </div>
                      )}
                  </div>

                  {message.role === "user" && (
                    <Avatar tone="user">
                      <User className="h-4 w-4" />
                    </Avatar>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start gap-3">
                  <Avatar tone="assistant">
                    <Bot className="h-4 w-4" />
                  </Avatar>
                  <div className="flex items-center rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
                    <Loader2 className="mr-2 h-4 w-4 animate-spin text-vin-teal" />
                    Đang xử lý yêu cầu...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            className="border-t border-white/70 bg-[linear-gradient(135deg,rgba(255,255,255,0.94),rgba(239,246,255,0.84))] p-4 backdrop-blur"
          >
            <div className="mx-auto flex max-w-3xl items-center gap-3">
              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Nhập câu hỏi hoặc chọn gợi ý bên trái"
                className="h-12 min-w-0 flex-1 rounded-2xl border border-slate-200 bg-white/95 px-4 text-sm font-medium text-slate-900 shadow-inner outline-none transition placeholder:text-slate-400 focus:border-vin-gold focus:ring-4 focus:ring-amber-200/40"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#F7C948,#F59E0B)] text-vin-ink shadow-[0_18px_44px_rgba(245,158,11,0.32)] transition hover:scale-[1.03] focus:outline-none focus:ring-4 focus:ring-amber-200/50 disabled:cursor-not-allowed disabled:opacity-50"
                title="Gửi"
              >
                <SendHorizontal className="h-5 w-5" />
              </button>
            </div>
          </form>
        </section>

        <aside className="space-y-4">
          <section className="rounded-3xl border border-white/20 bg-white/[0.86] p-4 shadow-[0_24px_70px_rgba(0,0,0,0.22)] backdrop-blur-2xl">
            <h2 className="text-sm font-bold text-slate-900">Latest result</h2>
            <dl className="mt-3 space-y-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <dt className="text-slate-500">Status</dt>
                <dd className="font-semibold capitalize text-slate-900">
                  {lastAssistantResponse?.type ?? "Ready"}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-slate-500">Confidence</dt>
                <dd className="font-semibold text-slate-900">
                  {lastAssistantResponse
                    ? `${Math.round(lastAssistantResponse.confidence * 100)}%`
                    : "-"}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-slate-500">Action</dt>
                <dd className="truncate font-semibold text-slate-900">
                  {lastAssistantResponse?.action ?? "-"}
                </dd>
              </div>
            </dl>
          </section>

          <section className="rounded-3xl border border-white/20 bg-white/[0.86] p-4 shadow-[0_24px_70px_rgba(0,0,0,0.22)] backdrop-blur-2xl">
            <h2 className="text-sm font-bold text-slate-900">Operations</h2>
            <div className="mt-3 space-y-2">
              <StatusRow
                icon={<CheckCircle2 className="h-4 w-4" />}
                label="Routing"
                value="Deterministic"
              />
              <StatusRow
                icon={<Clock3 className="h-4 w-4" />}
                label="Response mode"
                value={isLoading ? "Working" : "Standby"}
              />
              <StatusRow
                icon={<LifeBuoy className="h-4 w-4" />}
                label="Emergency path"
                value="Enabled"
              />
            </div>
          </section>
        </aside>
      </div>
    </main>
  );
}

function Avatar({
  children,
  tone,
}: {
  children: React.ReactNode;
  tone: "assistant" | "user";
}) {
  return (
    <div
      className={cn(
        "mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl shadow-sm",
        tone === "assistant"
          ? "order-1 bg-[linear-gradient(135deg,#0057B8,#12B3A8)] text-white shadow-[0_12px_32px_rgba(18,179,168,0.24)]"
          : "order-2 bg-[linear-gradient(135deg,#F7C948,#F59E0B)] text-vin-ink",
      )}
    >
      {children}
    </div>
  );
}

function ResultGroup({
  children,
  title,
}: {
  children: React.ReactNode;
  title: string;
}) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
        {title}
      </p>
      {children}
    </div>
  );
}

function StatusRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-white/70 bg-white/70 px-3 py-2 shadow-sm">
      <div className="flex items-center gap-2 text-vin-blue">
        {icon}
        <span className="text-sm">{label}</span>
      </div>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
}
