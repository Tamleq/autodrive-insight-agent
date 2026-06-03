export type SeverityLevel = "S" | "A" | "B" | "C" | "D";

export interface DrivingEvent {
  event_id: string;
  vehicle_id: string;
  timestamp: string;
  scene_type: string;
  weather: string;
  road_type?: string;
  ego_speed: number;
  brake_acc: number;
  steering_angle?: number;
  takeover: boolean;
  aeb_triggered: boolean;
  lane_confidence?: number;
  object_type?: string;
  object_confidence?: number;
  ttc?: number;
  lateral_offset?: number;
  perception_status?: string;
  planning_status?: string;
  event_type: string;
  severity: SeverityLevel | string;
  summary: string;
  log_text?: string;
  [key: string]: unknown;
}

export interface MatchedRule {
  rule_id?: string;
  rule_name?: string;
  description?: string;
  evidence?: Record<string, unknown>;
  risk_score?: number;
}

export interface SeverityResult {
  score?: number;
  level: SeverityLevel | string;
  reason?: string;
  factors?: string[];
}

export interface AiAnalysis {
  summary?: string;
  scenario_description?: string;
  possible_causes?: string[];
  risk_assessment?: string;
  recommendations?: string[];
  need_human_review?: boolean;
  [key: string]: unknown;
}

export interface AnalysisResult {
  event: DrivingEvent;
  matched_rules: MatchedRule[];
  severity: SeverityResult;
  ai_analysis: AiAnalysis;
  report: string;
  report_path: string;
}

export interface ReportResponse {
  event_id: string;
  report_format: string;
  content: string;
}

export interface EventFilters {
  scene_type?: string;
  takeover?: boolean;
  aeb_triggered?: boolean;
}

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const API_UNAVAILABLE_MESSAGE =
  "后端服务未启动或无法访问。请确认 FastAPI 正在运行，并且 Vite 已代理到 http://localhost:8000。";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(url, {
      headers: {
        Accept: "application/json",
        ...(options?.headers ?? {}),
      },
      ...options,
    });
  } catch {
    throw new ApiError(API_UNAVAILABLE_MESSAGE);
  }

  if (!response.ok) {
    let detail = `接口请求失败：${response.status}`;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : detail;
    } catch {
      // Keep the HTTP status fallback when the response is not JSON.
    }
    throw new ApiError(detail, response.status);
  }

  return response.json() as Promise<T>;
}

export async function getEvents(filters: EventFilters = {}): Promise<DrivingEvent[]> {
  const params = new URLSearchParams();
  if (filters.scene_type) {
    params.set("scene_type", filters.scene_type);
  }
  if (filters.takeover !== undefined) {
    params.set("takeover", String(filters.takeover));
  }
  if (filters.aeb_triggered !== undefined) {
    params.set("aeb_triggered", String(filters.aeb_triggered));
  }

  const query = params.toString();
  return request<DrivingEvent[]>(`/api/events${query ? `?${query}` : ""}`);
}

export function getEvent(eventId: string): Promise<DrivingEvent> {
  return request<DrivingEvent>(`/api/events/${encodeURIComponent(eventId)}`);
}

export function analyzeEvent(eventId: string): Promise<AnalysisResult> {
  return request<AnalysisResult>(`/api/analyze/${encodeURIComponent(eventId)}`, {
    method: "POST",
  });
}

export function getReport(eventId: string): Promise<ReportResponse> {
  return request<ReportResponse>(`/api/report/${encodeURIComponent(eventId)}`);
}
