import { Card, Descriptions, Tag, Typography } from "antd";

import type { MatchedRule } from "../api/events";

interface RuleHitCardProps {
  rule: MatchedRule;
}

function RuleHitCard({ rule }: RuleHitCardProps) {
  const evidence = rule.evidence ? JSON.stringify(rule.evidence, null, 2) : "-";

  return (
    <Card className="rule-hit-card" size="small">
      <div className="rule-hit-card__header">
        <Typography.Text strong>{rule.rule_name || rule.description || "规则命中"}</Typography.Text>
        {rule.rule_id ? <Tag color="cyan">{rule.rule_id}</Tag> : null}
      </div>
      <Descriptions size="small" column={1}>
        <Descriptions.Item label="命中条件">{rule.description || "-"}</Descriptions.Item>
        <Descriptions.Item label="风险分">{rule.risk_score ?? "-"}</Descriptions.Item>
        <Descriptions.Item label="证据">
          <pre className="inline-code-block">{evidence}</pre>
        </Descriptions.Item>
      </Descriptions>
    </Card>
  );
}

export default RuleHitCard;
