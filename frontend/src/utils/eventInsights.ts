import type { DrivingEvent, SeverityLevel } from "../api/events";

export interface EventInsight {
  severityLevel: SeverityLevel;
  severityScore: number;
  issueType: string;
}

function asNumber(value: unknown): number | undefined {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
  }
  return undefined;
}

function containsAny(value: unknown, keywords: string[]) {
  return typeof value === "string" && keywords.some((keyword) => value.toLowerCase().includes(keyword));
}

function levelForScore(score: number): SeverityLevel {
  if (score >= 80) {
    return "S";
  }
  if (score >= 60) {
    return "A";
  }
  if (score >= 40) {
    return "B";
  }
  if (score >= 20) {
    return "C";
  }
  return "D";
}

export function deriveSeverityScore(event: DrivingEvent) {
  const brakeAcc = asNumber(event.brake_acc);
  const ttc = asNumber(event.ttc);
  const objectConfidence = asNumber(event.object_confidence);
  const laneConfidence = asNumber(event.lane_confidence);
  const egoSpeed = asNumber(event.ego_speed);
  const lateralOffset = Math.abs(asNumber(event.lateral_offset) ?? 0);

  let score = 0;

  if (event.aeb_triggered) {
    score += 25;
  }
  if (event.takeover) {
    score += 25;
  }
  if (brakeAcc !== undefined && brakeAcc <= -3.5) {
    score += 20;
  }
  if (ttc !== undefined && ttc <= 1.5) {
    score += 20;
  }
  if (objectConfidence !== undefined && objectConfidence < 0.5) {
    score += 10;
  }
  if (laneConfidence !== undefined && laneConfidence < 0.45) {
    score += 15;
  }
  if (lateralOffset > 0.5) {
    score += 10;
  }
  if (egoSpeed !== undefined && egoSpeed > 40 && event.takeover) {
    score += 10;
  }
  if (containsAny(event.planning_status, ["abnormal", "deviation"])) {
    score += 15;
  }
  if (containsAny(event.perception_status, ["unstable", "lost", "low_confidence"])) {
    score += 15;
  }

  return score;
}

export function deriveSeverityLevel(event: DrivingEvent): SeverityLevel {
  return levelForScore(deriveSeverityScore(event));
}

export function deriveIssueType(event: DrivingEvent) {
  const brakeAcc = asNumber(event.brake_acc);
  const ttc = asNumber(event.ttc);
  const objectConfidence = asNumber(event.object_confidence);
  const laneConfidence = asNumber(event.lane_confidence);
  const egoSpeed = asNumber(event.ego_speed);
  const lateralOffset = Math.abs(asNumber(event.lateral_offset) ?? 0);

  if (event.aeb_triggered && objectConfidence !== undefined && objectConfidence < 0.55 && brakeAcc !== undefined && brakeAcc <= -3) {
    return "AEB 疑似误触发";
  }
  if (event.takeover && egoSpeed !== undefined && egoSpeed > 40) {
    return "高速接管";
  }
  if (ttc !== undefined && ttc <= 1.5 && brakeAcc !== undefined && brakeAcc <= -3.5) {
    return "低 TTC 急制动";
  }
  if ((laneConfidence !== undefined && laneConfidence < 0.5) || lateralOffset > 0.45) {
    return "车道线置信度下降";
  }
  if (objectConfidence !== undefined && objectConfidence < 0.6) {
    return "目标感知置信度低";
  }
  if (containsAny(event.planning_status, ["abnormal", "deviation"])) {
    return "规划轨迹异常";
  }
  if (containsAny(event.perception_status, ["unstable", "lost", "low_confidence"])) {
    return "感知跟踪异常";
  }
  if (event.aeb_triggered) {
    return "AEB 触发";
  }
  if (event.takeover) {
    return "人工接管";
  }
  return "常规异常";
}

export function buildEventInsight(event: DrivingEvent): EventInsight {
  const severityScore = deriveSeverityScore(event);
  return {
    severityScore,
    severityLevel: levelForScore(severityScore),
    issueType: deriveIssueType(event),
  };
}
