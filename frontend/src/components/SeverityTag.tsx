import { Tag } from "antd";

const severityColorMap: Record<string, string> = {
  S: "magenta",
  A: "red",
  B: "orange",
  C: "gold",
  D: "green",
};

interface SeverityTagProps {
  level?: string | null;
}

function SeverityTag({ level }: SeverityTagProps) {
  const normalizedLevel = String(level || "D").toUpperCase();

  return (
    <Tag className="severity-tag" color={severityColorMap[normalizedLevel] || "default"}>
      {normalizedLevel}
    </Tag>
  );
}

export default SeverityTag;
