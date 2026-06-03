import { Card, Statistic } from "antd";
import type { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: number | string;
  icon: ReactNode;
  color?: string;
  suffix?: string;
}

function MetricCard({ title, value, icon, color = "#38bdf8", suffix }: MetricCardProps) {
  return (
    <Card className="metric-card">
      <div className="metric-card__body">
        <div className="metric-card__icon" style={{ color }}>
          {icon}
        </div>
        <Statistic title={title} value={value} suffix={suffix} />
      </div>
    </Card>
  );
}

export default MetricCard;
