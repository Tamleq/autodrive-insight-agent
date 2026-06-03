import { ConfigProvider, Layout, Menu, Typography, theme } from "antd";
import { AlertTriangle, BarChart3, FileText, ListChecks } from "lucide-react";
import { useMemo, useState } from "react";

import Dashboard from "./pages/Dashboard";
import EventDetail from "./pages/EventDetail";
import EventList from "./pages/EventList";
import Report from "./pages/Report";

const { Header, Content, Sider } = Layout;

type PageKey = "dashboard" | "events" | "detail" | "report";

function App() {
  const [activePage, setActivePage] = useState<PageKey>("dashboard");
  const [selectedEventId, setSelectedEventId] = useState<string>();

  const pageTitle = useMemo(
    () =>
      ({
        dashboard: "驾驶事件总览",
        events: "事件检索",
        detail: "事件详情分析",
        report: "AI 分析报告",
      })[activePage],
    [activePage],
  );

  const openEventDetail = (eventId: string) => {
    setSelectedEventId(eventId);
    setActivePage("detail");
  };

  const openReport = (eventId: string) => {
    setSelectedEventId(eventId);
    setActivePage("report");
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: "#38bdf8",
          borderRadius: 8,
          colorBgLayout: "#07111f",
          colorBgContainer: "#0d1828",
          colorBorder: "#1f334a",
          colorText: "#e5f0ff",
          colorTextSecondary: "#8fa6c3",
          fontFamily:
            "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        },
      }}
    >
      <Layout className="app-shell">
        <Sider width={260} className="app-sider">
          <div className="brand">
            <div className="brand__mark">
              <AlertTriangle size={24} />
            </div>
            <div>
              <Typography.Title level={4}>AutoDrive Insight</Typography.Title>
              <Typography.Text>智能驾驶数据分析台</Typography.Text>
            </div>
          </div>
          <Menu
            mode="inline"
            selectedKeys={[activePage]}
            onClick={({ key }) => setActivePage(key as PageKey)}
            items={[
              { key: "dashboard", icon: <BarChart3 size={18} />, label: "总览" },
              { key: "events", icon: <ListChecks size={18} />, label: "事件列表" },
              { key: "detail", icon: <AlertTriangle size={18} />, label: "事件详情" },
              { key: "report", icon: <FileText size={18} />, label: "分析报告" },
            ]}
          />
        </Sider>
        <Layout>
          <Header className="app-header">
            <div>
              <Typography.Text className="app-header__eyebrow">
                车企内部 AI 数据分析平台
              </Typography.Text>
              <Typography.Title level={3}>{pageTitle}</Typography.Title>
            </div>
            {selectedEventId ? (
              <Typography.Text className="app-header__event">
                当前事件：{selectedEventId}
              </Typography.Text>
            ) : null}
          </Header>
          <Content className="app-content">
            {activePage === "dashboard" ? <Dashboard onOpenEvent={openEventDetail} /> : null}
            {activePage === "events" ? <EventList onOpenEvent={openEventDetail} /> : null}
            {activePage === "detail" ? (
              <EventDetail
                eventId={selectedEventId}
                onSelectEvent={setSelectedEventId}
                onOpenReport={openReport}
              />
            ) : null}
            {activePage === "report" ? (
              <Report eventId={selectedEventId} onSelectEvent={setSelectedEventId} />
            ) : null}
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

export default App;
