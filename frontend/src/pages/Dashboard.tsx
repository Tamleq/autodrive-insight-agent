import { Card, Col, Row, Statistic, Typography } from "antd";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const severityData = [
  { level: "S", count: 1 },
  { level: "A", count: 4 },
  { level: "B", count: 8 },
  { level: "C", count: 16 },
  { level: "D", count: 24 },
];

function Dashboard() {
  return (
    <div className="page-stack">
      <Typography.Title level={2}>Dashboard</Typography.Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="Total Events" value={53} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="High Severity" value={5} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="Reports Generated" value={12} />
          </Card>
        </Col>
      </Row>
      <Card title="Severity Distribution">
        <div className="chart-panel">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={severityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="level" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#1677ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}

export default Dashboard;
