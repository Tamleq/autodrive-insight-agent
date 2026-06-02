import { Layout, Menu, Typography } from "antd";
import {
  AlertTriangle,
  BarChart3,
  FileText,
  ListChecks,
} from "lucide-react";
import { useState } from "react";

import Dashboard from "./pages/Dashboard";
import EventDetail from "./pages/EventDetail";
import EventList from "./pages/EventList";
import Report from "./pages/Report";

const { Header, Content, Sider } = Layout;

const pages = {
  dashboard: <Dashboard />,
  events: <EventList />,
  detail: <EventDetail />,
  report: <Report />,
};

function App() {
  const [activePage, setActivePage] = useState<keyof typeof pages>("dashboard");

  return (
    <Layout className="app-shell">
      <Sider width={248} className="app-sider">
        <div className="brand">
          <AlertTriangle size={24} />
          <div>
            <Typography.Title level={4}>AutoDrive Insight</Typography.Title>
            <Typography.Text>Agent Demo</Typography.Text>
          </div>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[activePage]}
          onClick={({ key }) => setActivePage(key as keyof typeof pages)}
          items={[
            { key: "dashboard", icon: <BarChart3 size={18} />, label: "Dashboard" },
            { key: "events", icon: <ListChecks size={18} />, label: "Event List" },
            { key: "detail", icon: <AlertTriangle size={18} />, label: "Event Detail" },
            { key: "report", icon: <FileText size={18} />, label: "Report" },
          ]}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Typography.Title level={3}>Intelligent Driving Event Analysis</Typography.Title>
        </Header>
        <Content className="app-content">{pages[activePage]}</Content>
      </Layout>
    </Layout>
  );
}

export default App;
