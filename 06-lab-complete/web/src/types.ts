export interface Facility {
  id: string;
  name: string;
  type: string;
  zone_id: string;
  tags: string[];
  kid_friendly: boolean;
  is_open: boolean;
  crowd_level: "low" | "medium" | "high";
  wait_time_min: number;
  distance_map: Record<string, number>;
  walk_time_map: Record<string, number>;
  amenities: string[];
  description: string;
  lat?: number;
  lng?: number;
}

export interface Navigation {
  from_zone?: string;
  to_zone?: string;
  distance_m: number;
  walk_time_min: number;
  direction_text: string | null;
}

export interface ChatResponse {
  type: "success" | "clarification" | "fallback" | "fast_track" | "out_of_scope" | "error";
  action: string;
  message: string;
  reason_summary: string;
  confidence: number;
  selected_facility?: Facility | null;
  alternatives?: Facility[];
  cross_sell_facilities?: Facility[];
  navigation?: Navigation | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
}
