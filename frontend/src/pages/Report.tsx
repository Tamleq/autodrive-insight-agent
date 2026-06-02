import { Card, Typography } from "antd";

function Report() {
  return (
    <div className="page-stack">
      <Typography.Title level={2}>Report</Typography.Title>
      <Card title="Mock Markdown Report">
        <Typography.Paragraph>
          AutoDrive Insight Agent has generated a mock event report for EVT-0001.
          The final report module will export structured Markdown based on rule hits,
          severity grade, and AI analysis.
        </Typography.Paragraph>
      </Card>
    </div>
  );
}

export default Report;
