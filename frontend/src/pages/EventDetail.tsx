import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Empty,
  List,
  Row,
  Skeleton,
  Space,
  Tag,
  Typography,
  message,
} from "antd";
import { FileText, Radar, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  analyzeEvent,
  getEvent,
  getEvents,
  type AiAnalysis,
  type AnalysisResult,
  type DrivingEvent,
  type SeverityResult,
} from "../api/events";
import MetricCard from "../components/MetricCard";
import RuleHitCard from "../components/RuleHitCard";
import SeverityTag from "../components/SeverityTag";

interface EventDetailProps {
  eventId?: string;
  onSelectEvent: (eventId: string) => void;
  onOpenReport: (eventId: string) => void;
}

function formatMetric(value: unknown, digits = 2) {
  if (typeof value === "number") {
    return Number(value.toFixed(digits));
  }
  return value === undefined || value === null || value === "" ? "-" : String(value);
}

function renderTextList(items?: string[]) {
  if (!items?.length) {
    return <Typography.Text type="secondary">暂无</Typography.Text>;
  }
  return (
    <List
      size="small"
      dataSource={items}
      renderItem={(item) => (
        <List.Item>
          <Typography.Text>{item}</Typography.Text>
        </List.Item>
      )}
    />
  );
}

function EventDetail({ eventId, onSelectEvent, onOpenReport }: EventDetailProps) {
  const [resolvedEventId, setResolvedEventId] = useState(eventId);
  const [event, setEvent] = useState<DrivingEvent>();
  const [analysis, setAnalysis] = useState<AnalysisResult>();
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string>();
  const [messageApi, contextHolder] = message.useMessage();

  useEffect(() => {
    if (eventId) {
      setResolvedEventId(eventId);
      return;
    }

    getEvents()
      .then((data) => {
        const firstEvent = data[0];
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
    setAnalysis(undefined);
    getEvent(resolvedEventId)
      .then((data) => {
        setEvent(data);
        setError(undefined);
      })
      .catch((err: Error) => {
        setEvent(undefined);
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, [resolvedEventId]);

  const severity: SeverityResult | undefined = analysis?.severity;
  const aiAnalysis: AiAnalysis | undefined = analysis?.ai_analysis;

  const basicItems = useMemo(
    () => [
      { label: "事件 ID", value: event?.event_id },
      { label: "车辆 ID", value: event?.vehicle_id },
      { label: "时间", value: event?.timestamp },
      { label: "场景", value: event?.scene_type },
      { label: "天气", value: event?.weather },
      { label: "道路类型", value: event?.road_type },
      { label: "问题类型", value: event?.event_type },
      { label: "人工接管", value: event?.takeover ? "是" : "否" },
      { label: "AEB 触发", value: event?.aeb_triggered ? "是" : "否" },
    ],
    [event],
  );

  const handleAnalyze = async () => {
    if (!resolvedEventId) {
      return;
    }

    setAnalyzing(true);
    try {
      const result = await analyzeEvent(resolvedEventId);
      setAnalysis(result);
      messageApi.success("AI 分析报告已生成");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="page-stack">
      {contextHolder}
      {error ? <Alert type="error" showIcon message="后端接口暂不可用" description={error} /> : null}
      <Skeleton loading={loading} active paragraph={{ rows: 8 }}>
        {!event ? (
          <Empty description="暂无可展示事件" />
        ) : (
          <>
            <div className="detail-header">
              <div>
                <Typography.Title level={3}>{event.event_id}</Typography.Title>
                <Typography.Text type="secondary">{event.summary || event.log_text || event.scene_type}</Typography.Text>
              </div>
              <Space wrap>
                <Button icon={<FileText size={16} />} onClick={() => onOpenReport(event.event_id)}>
                  查看报告
                </Button>
                <Button
                  type="primary"
                  icon={<Sparkles size={16} />}
                  loading={analyzing}
                  onClick={handleAnalyze}
                >
                  生成 AI 分析报告
                </Button>
              </Space>
            </div>

            <Card title="事件基本信息" className="analysis-card">
              <Descriptions bordered column={{ xs: 1, md: 2, xl: 3 }}>
                {basicItems.map((item) => (
                  <Descriptions.Item key={item.label} label={item.label}>
                    {item.value || "-"}
                  </Descriptions.Item>
                ))}
                <Descriptions.Item label="严重度评级">
                  <Space>
                    <SeverityTag level={severity?.level || event.severity} />
                    {severity?.score !== undefined ? <Tag color="cyan">score {severity.score}</Tag> : null}
                  </Space>
                </Descriptions.Item>
              </Descriptions>
            </Card>

            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} xl={5}>
                <MetricCard title="车速" value={formatMetric(event.ego_speed)} suffix="km/h" icon={<Radar size={22} />} />
              </Col>
              <Col xs={24} sm={12} xl={5}>
                <MetricCard title="制动加速度" value={formatMetric(event.brake_acc)} suffix="m/s2" icon={<Radar size={22} />} color="#fb7185" />
              </Col>
              <Col xs={24} sm={12} xl={4}>
                <MetricCard title="TTC 碰撞时间" value={formatMetric(event.ttc)} suffix="s" icon={<Radar size={22} />} color="#f59e0b" />
              </Col>
              <Col xs={24} sm={12} xl={5}>
                <MetricCard title="目标置信度" value={formatMetric(event.object_confidence, 3)} icon={<Radar size={22} />} color="#22d3ee" />
              </Col>
              <Col xs={24} sm={12} xl={5}>
                <MetricCard title="车道置信度" value={formatMetric(event.lane_confidence, 3)} icon={<Radar size={22} />} color="#34d399" />
              </Col>
            </Row>

            <Row gutter={[16, 16]}>
              <Col xs={24} xl={12}>
                <Card title="规则命中结果" className="analysis-card">
                  {analysis?.matched_rules.length ? (
                    <Space direction="vertical" size={12} className="full-width">
                      {analysis.matched_rules.map((rule, index) => (
                        <RuleHitCard key={`${rule.rule_id || "rule"}-${index}`} rule={rule} />
                      ))}
                    </Space>
                  ) : (
                    <Empty description="点击生成 AI 分析报告后展示规则命中结果" />
                  )}
                </Card>
              </Col>
              <Col xs={24} xl={12}>
                <Card title="严重度评级" className="analysis-card">
                  <Space direction="vertical" size={12} className="full-width">
                    <Space>
                      <SeverityTag level={severity?.level || event.severity} />
                      {severity?.score !== undefined ? <Tag color="cyan">score {severity.score}</Tag> : null}
                    </Space>
                    <Typography.Paragraph>{severity?.reason || "尚未生成详细评级说明。"}</Typography.Paragraph>
                    <div className="factor-list">
                      {(severity?.factors || []).map((factor) => (
                        <Tag key={factor}>{factor}</Tag>
                      ))}
                    </div>
                  </Space>
                </Card>
              </Col>
            </Row>

            <Card title="AI 分析结果" className="analysis-card">
              {aiAnalysis ? (
                <Row gutter={[16, 16]}>
                  <Col xs={24} xl={12}>
                    <Typography.Title level={5}>分析摘要</Typography.Title>
                    <Typography.Paragraph>{aiAnalysis.summary || "-"}</Typography.Paragraph>
                    <Typography.Title level={5}>场景描述</Typography.Title>
                    <Typography.Paragraph>{aiAnalysis.scenario_description || "-"}</Typography.Paragraph>
                    <Typography.Title level={5}>风险评估</Typography.Title>
                    <Typography.Paragraph>{aiAnalysis.risk_assessment || "-"}</Typography.Paragraph>
                  </Col>
                  <Col xs={24} xl={12}>
                    <Typography.Title level={5}>可能原因</Typography.Title>
                    {renderTextList(aiAnalysis.possible_causes)}
                    <Typography.Title level={5}>建议动作</Typography.Title>
                    {renderTextList(aiAnalysis.recommendations)}
                    <Tag color={aiAnalysis.need_human_review ? "red" : "green"}>
                      {aiAnalysis.need_human_review ? "需要人工复核" : "可进入常规闭环"}
                    </Tag>
                  </Col>
                </Row>
              ) : (
                <Empty description="尚未生成 AI 分析结果" />
              )}
            </Card>
          </>
        )}
      </Skeleton>
    </div>
  );
}

export default EventDetail;
