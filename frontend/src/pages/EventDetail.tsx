import { Card, Descriptions, Tag, Typography } from "antd";

function EventDetail() {
  return (
    <div className="page-stack">
      <Typography.Title level={2}>Event Detail</Typography.Title>
      <Card>
        <Descriptions bordered column={1}>
          <Descriptions.Item label="Event ID">EVT-0001</Descriptions.Item>
          <Descriptions.Item label="Vehicle ID">CAR-1024</Descriptions.Item>
          <Descriptions.Item label="Scenario">Urban following</Descriptions.Item>
          <Descriptions.Item label="Rule Hits">
            <Tag>AEB Triggered</Tag>
            <Tag>TTC Too Low</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Severity">
            <Tag color="red">A</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Summary">
            AEB triggered with low TTC during an urban following scenario.
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
}

export default EventDetail;
