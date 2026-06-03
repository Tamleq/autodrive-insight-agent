import { Alert, Button, Card, Col, Empty, List, Row, Skeleton, Space, Typography } from "antd";
import { Activity, AlertOctagon, Bell, Bot, Gauge, ShieldAlert } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getEvents, type DrivingEvent } from "../api/events";
import MetricCard from "../components/MetricCard";
import SeverityTag from "../components/SeverityTag";
import { buildEventInsight, deriveIssueType, deriveSeverityLevel } from "../utils/eventInsights";

interface DashboardProps {
  onOpenEvent: (eventId: string) => void;
}

const severityLevels = ["S", "A", "B", "C", "D"];
const severityColors: Record<string, string> = {
  S: "#e879f9",
  A: "#f43f5e",
  B: "#fb923c",
  C: "#facc15",
  D: "#22c55e",
};

function Dashboard({ onOpenEvent }: DashboardProps) {
  const [events, setEvents] = useState<DrivingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    setLoading(true);
    getEvents()
      .then((data) => {
        setEvents(data);
        setError(undefined);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const dashboardData = useMemo(() => {
    const eventInsights = events.map((event) => ({
      event,
      insight: buildEventInsight(event),
    }));

    const severityDistribution = severityLevels.map((level) => ({
      level,
      count: eventInsights.filter(({ insight }) => insight.severityLevel === level).length,
    }));

    const typeCounts = eventInsights.reduce<Record<string, number>>((acc, { insight }) => {
      acc[insight.issueType] = (acc[insight.issueType] || 0) + 1;
      return acc;
    }, {});

    const topTypes = Object.entries(typeCounts)
      .map(([type, count]) => ({ type, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    const allHighRiskEvents = eventInsights
      .filter(
        ({ event, insight }) =>
          ["S", "A"].includes(insight.severityLevel) || event.takeover || event.aeb_triggered,
      )
      .map(({ event }) => event);

    const highRiskEvents = [...allHighRiskEvents]
      .sort((a, b) => String(b.timestamp).localeCompare(String(a.timestamp)))
      .slice(0, 6);

    const averageRiskScore = events.length
      ? Math.round(eventInsights.reduce((sum, { insight }) => sum + insight.severityScore, 0) / events.length)
      : 0;

    return {
      total: events.length,
      anomalies: events.length,
      highRisk: allHighRiskEvents.length,
      takeover: events.filter((event) => event.takeover).length,
      aeb: events.filter((event) => event.aeb_triggered).length,
      severityDistribution,
      topTypes,
      highRiskEvents,
      averageRiskScore,
      dominantIssueType: topTypes[0]?.type || "-",
    };
  }, [events]);

  const topTypesTotal = dashboardData.topTypes.reduce((sum, item) => sum + item.count, 0);

  return (
    <div className="page-stack">
      {error ? <Alert type="error" showIcon message="后端接口暂不可用" description={error} /> : null}
      <Skeleton loading={loading} active paragraph={{ rows: 8 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} xl={4}>
            <MetricCard title="总事件数" value={dashboardData.total} icon={<Activity size={22} />} />
          </Col>
          <Col xs={24} sm={12} xl={5}>
            <MetricCard title="异常事件数" value={dashboardData.anomalies} icon={<Bell size={22} />} color="#60a5fa" />
          </Col>
          <Col xs={24} sm={12} xl={5}>
            <MetricCard title="高风险事件数" value={dashboardData.highRisk} icon={<ShieldAlert size={22} />} color="#fb7185" />
          </Col>
          <Col xs={24} sm={12} xl={5}>
            <MetricCard title="人工接管次数" value={dashboardData.takeover} icon={<Gauge size={22} />} color="#f59e0b" />
          </Col>
          <Col xs={24} sm={12} xl={5}>
            <MetricCard title="AEB 触发次数" value={dashboardData.aeb} icon={<AlertOctagon size={22} />} color="#f43f5e" />
          </Col>
        </Row>

        <Row gutter={[16, 16]}>
          <Col xs={24} xl={12}>
            <Card title="严重度分布" className="analysis-card">
              <div className="chart-panel chart-panel--compact">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dashboardData.severityDistribution} margin={{ top: 24, right: 18, left: 0, bottom: 6 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f334a" vertical={false} />
                    <XAxis dataKey="level" stroke="#8fa6c3" tickLine={false} />
                    <YAxis allowDecimals={false} stroke="#8fa6c3" tickLine={false} axisLine={false} />
                    <Tooltip />
                    <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                      {dashboardData.severityDistribution.map((item) => (
                        <Cell key={item.level} fill={severityColors[item.level]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="severity-summary">
                <div>
                  <Typography.Text type="secondary">平均风险分</Typography.Text>
                  <Typography.Title level={4}>{dashboardData.averageRiskScore}</Typography.Title>
                </div>
                <div className="severity-legend">
                  {dashboardData.severityDistribution.map((item) => (
                    <span key={item.level}>
                      <SeverityTag level={item.level} /> {item.count}
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          </Col>
          <Col xs={24} xl={12}>
            <Card title="问题类型 Top 5" className="analysis-card">
              {dashboardData.topTypes.length ? (
                <>
                  <div className="issue-summary">
                    <Typography.Text type="secondary">主要问题</Typography.Text>
                    <Typography.Title level={4}>{dashboardData.dominantIssueType}</Typography.Title>
                  </div>
                  <div className="chart-panel chart-panel--compact">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={dashboardData.topTypes} layout="vertical" margin={{ top: 18, right: 42, left: 8, bottom: 8 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1f334a" horizontal={false} />
                        <XAxis type="number" allowDecimals={false} stroke="#8fa6c3" tickLine={false} axisLine={false} />
                        <YAxis type="category" dataKey="type" width={132} stroke="#cbd5e1" tickLine={false} axisLine={false} />
                        <Tooltip />
                        <Bar dataKey="count" fill="#38bdf8" radius={[0, 8, 8, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="issue-rank-list">
                    {dashboardData.topTypes.map((item) => (
                      <div key={item.type} className="issue-rank-item">
                        <span>{item.type}</span>
                        <strong>{item.count}</strong>
                        <div>
                          <i style={{ width: `${topTypesTotal ? (item.count / topTypesTotal) * 100 : 0}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <Empty description="暂无类型数据" />
              )}
            </Card>
          </Col>
        </Row>

        <Card title="最近高风险事件" className="analysis-card">
          <List
            dataSource={dashboardData.highRiskEvents}
            locale={{ emptyText: <Empty description="暂无高风险事件" /> }}
            renderItem={(event) => (
              <List.Item
                actions={[
                  <Button key="detail" type="link" onClick={() => onOpenEvent(event.event_id)}>
                    查看详情
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  avatar={<Bot className="list-avatar-icon" size={24} />}
                  title={
                    <Space>
                      <Typography.Text strong>{event.event_id}</Typography.Text>
                      <SeverityTag level={deriveSeverityLevel(event)} />
                      <Typography.Text type="secondary">{deriveIssueType(event)}</Typography.Text>
                    </Space>
                  }
                  description={`${event.timestamp} · ${event.scene_type} · ${event.summary || event.event_type}`}
                />
              </List.Item>
            )}
          />
        </Card>
      </Skeleton>
    </div>
  );
}

export default Dashboard;
