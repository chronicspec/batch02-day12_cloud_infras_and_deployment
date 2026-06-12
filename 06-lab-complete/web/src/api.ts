import axios from "axios";
import { ChatResponse } from "./types";

const API_BASE = "http://localhost:8001/api/v1";

function repairMojibakeText(value: string): string {
  if (!/[ÃÄÆáºá»]/.test(value)) return value;

  const bytes: number[] = [];
  for (const char of value) {
    const code = char.charCodeAt(0);
    if (code > 255) return value;
    bytes.push(code);
  }

  try {
    const repaired = new TextDecoder("utf-8", { fatal: false }).decode(
      new Uint8Array(bytes),
    );
    return repaired.includes("�") ? value : repaired;
  } catch {
    return value;
  }
}

function repairResponseText<T>(payload: T): T {
  if (typeof payload === "string") {
    return repairMojibakeText(payload) as T;
  }

  if (Array.isArray(payload)) {
    return payload.map((item) => repairResponseText(item)) as T;
  }

  if (payload && typeof payload === "object") {
    return Object.fromEntries(
      Object.entries(payload).map(([key, value]) => [
        key,
        repairResponseText(value),
      ]),
    ) as T;
  }

  return payload;
}

export const sendMessage = async (
  message: string,
  sessionId: string,
  currentZone: string,
): Promise<ChatResponse> => {
  try {
    const res = await axios.post(`${API_BASE}/chat`, {
      session_id: sessionId,
      message,
      current_zone: currentZone,
      language: "vi",
      user_context: { has_child: false },
    });
    return repairResponseText(res.data);
  } catch (error) {
    console.error("Chat API error:", error);
    return {
      type: "error",
      action: "error",
      message: "Đã có lỗi xảy ra khi kết nối đến máy chủ. Vui lòng thử lại sau.",
      reason_summary: "api_error",
      confidence: 0,
    };
  }
};
