import { Alert, Button, Card, Empty, Skeleton, Space, Typography, message } from "antd";
import { Clipboard, Download } from "lucide-react";
import { useEffect, useState } from "react";

import { getEvents, getReport } from "../api/events";

interface ReportProps {
  eventId?: string;
  onSelectEvent: (eventId: string) => void;
}

function downloadMarkdown(eventId: string, content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${eventId}_report.md`;
  link.click();
  URL.revokeObjectURL(url);
}

function Report({ eventId, onSelectEvent }: ReportProps) {
  const [resolvedEventId, setResolvedEventId] = useState(eventId);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [messageApi, contextHolder] = message.useMessage();

  useEffect(() => {
    if (eventId) {
      setResolvedEventId(eventId);
      return;
    }

    getEvents()
      .then((events) => {
        const firstEvent = events[0];
        if (firstEvent) {
          setResolvedEventId(firstEvent.event_id);
          onSelectEvent(firstEvent.event_id);
        }
      })
      .catch((err: Error) => setError(err.message));
  }, [eventId, onSelectEvent]);

  useEffect(() => {
    if (!resolvedEventId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    getReport(resolvedEventId)
      .then((report) => {
        setContent(report.content);
        setError(undefined);
      })
      .catch((err: Error) => {
        setContent("");
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, [resolvedEventId]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      messageApi.success("报告内容已复制");
    } catch {
      messageApi.error("复制失败，请检查浏览器剪贴板权限");
    }
  };

  return (
    <div className="page-stack">
      {contextHolder}
      {error ? <Alert type="error" showIcon message="报告接口暂不可用" description={error} /> : null}
      <Skeleton loading={loading} active paragraph={{ rows: 10 }}>
        {!resolvedEventId ? (
          <Empty description="暂无可展示报告" />
        ) : (
          <Card
            className="analysis-card report-card"
            title={
              <div>
                <Typography.Title level={4}>Markdown 报告内容</Typography.Title>
                <Typography.Text type="secondary">{resolvedEventId}</Typography.Text>
              </div>
            }
            extra={
              <Space wrap>
                <Button icon={<Clipboard size={16} />} disabled={!content} onClick={handleCopy}>
                  复制报告
                </Button>
                <Button
                  type="primary"
                  icon={<Download size={16} />}
                  disabled={!content}
                  onClick={() => downloadMarkdown(resolvedEventId, content)}
                >
                  下载 .md 文件
                </Button>
              </Space>
            }
          >
            {content ? <pre className="markdown-preview">{content}</pre> : <Empty description="暂无报告内容" />}
          </Card>
        )}
      </Skeleton>
    </div>
  );
}

export default Report;
