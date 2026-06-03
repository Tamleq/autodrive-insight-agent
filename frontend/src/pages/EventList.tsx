import { Alert, Button, Card, Empty, Select, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getEvents, type DrivingEvent, type EventFilters } from "../api/events";
import SeverityTag from "../components/SeverityTag";
import { deriveIssueType, deriveSeverityLevel } from "../utils/eventInsights";

interface EventListProps {
  onOpenEvent: (eventId: string) => void;
}

type BooleanFilter = "all" | "true" | "false";

function booleanFilterValue(value: BooleanFilter): boolean | undefined {
  if (value === "all") {
    return undefined;
  }
  return value === "true";
}

function EventList({ onOpenEvent }: EventListProps) {
  const [events, setEvents] = useState<DrivingEvent[]>([]);
  const [sceneOptions, setSceneOptions] = useState<string[]>([]);
  const [sceneType, setSceneType] = useState<string>();
  const [takeover, setTakeover] = useState<BooleanFilter>("all");
  const [aebTriggered, setAebTriggered] = useState<BooleanFilter>("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    getEvents()
      .then((data) => {
        setSceneOptions([...new Set(data.map((event) => event.scene_type).filter(Boolean))]);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    const filters: EventFilters = {
      scene_type: sceneType,
      takeover: booleanFilterValue(takeover),
      aeb_triggered: booleanFilterValue(aebTriggered),
    };

    setLoading(true);
    getEvents(filters)
      .then((data) => {
        setEvents(data);
        setError(undefined);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [sceneType, takeover, aebTriggered]);

  const columns: ColumnsType<DrivingEvent> = useMemo(
    () => [
      {
        title: "事件 ID",
        dataIndex: "event_id",
        fixed: "left",
        width: 130,
        render: (eventId: string) => (
          <Button type="link" onClick={() => onOpenEvent(eventId)}>
            {eventId}
          </Button>
        ),
      },
      { title: "车辆 ID", dataIndex: "vehicle_id", width: 120 },
      { title: "时间", dataIndex: "timestamp", width: 190 },
      { title: "场景", dataIndex: "scene_type", ellipsis: true },
      {
        title: "问题类型",
        key: "derived_issue_type",
        width: 180,
        ellipsis: true,
        render: (_, record) => deriveIssueType(record),
      },
      {
        title: "接管",
        dataIndex: "takeover",
        width: 90,
        render: (value: boolean) => <Tag color={value ? "orange" : "default"}>{value ? "是" : "否"}</Tag>,
      },
      {
        title: "AEB",
        dataIndex: "aeb_triggered",
        width: 90,
        render: (value: boolean) => <Tag color={value ? "red" : "default"}>{value ? "是" : "否"}</Tag>,
      },
      {
        title: "严重度",
        key: "derived_severity",
        width: 95,
        render: (_, record) => <SeverityTag level={deriveSeverityLevel(record)} />,
      },
      {
        title: "操作",
        key: "action",
        fixed: "right",
        width: 110,
        render: (_, record) => (
          <Button size="small" icon={<Search size={14} />} onClick={() => onOpenEvent(record.event_id)}>
            详情
          </Button>
        ),
      },
    ],
    [onOpenEvent],
  );

  return (
    <div className="page-stack">
      {error ? <Alert type="error" showIcon message="后端接口暂不可用" description={error} /> : null}
      <Card className="analysis-card">
        <div className="table-toolbar">
          <div>
            <Typography.Title level={4}>事件表格</Typography.Title>
            <Typography.Text type="secondary">
              按场景、是否接管、是否触发 AEB 筛选智能驾驶异常事件
            </Typography.Text>
          </div>
          <Space wrap>
            <Select
              allowClear
              placeholder="选择场景"
              value={sceneType}
              onChange={setSceneType}
              options={sceneOptions.map((scene) => ({ value: scene, label: scene }))}
              style={{ minWidth: 220 }}
            />
            <Select
              value={takeover}
              onChange={setTakeover}
              style={{ width: 140 }}
              options={[
                { value: "all", label: "接管：全部" },
                { value: "true", label: "接管：是" },
                { value: "false", label: "接管：否" },
              ]}
            />
            <Select
              value={aebTriggered}
              onChange={setAebTriggered}
              style={{ width: 140 }}
              options={[
                { value: "all", label: "AEB：全部" },
                { value: "true", label: "AEB：是" },
                { value: "false", label: "AEB：否" },
              ]}
            />
          </Space>
        </div>
        <Table
          rowKey="event_id"
          dataSource={events}
          columns={columns}
          loading={loading}
          locale={{ emptyText: <Empty description="暂无事件数据" /> }}
          scroll={{ x: 1180 }}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          onRow={(record) => ({
            onDoubleClick: () => onOpenEvent(record.event_id),
          })}
        />
      </Card>
    </div>
  );
}

export default EventList;
