import { Card, Table, Tag, Typography } from "antd";

const mockEvents = [
  {
    eventId: "EVT-0001",
    vehicleId: "CAR-1024",
    type: "AEB Trigger",
    severity: "A",
    status: "Ready",
  },
  {
    eventId: "EVT-0002",
    vehicleId: "CAR-2048",
    type: "Driver Takeover",
    severity: "B",
    status: "Pending",
  },
  {
    eventId: "EVT-0003",
    vehicleId: "CAR-4096",
    type: "Planning Anomaly",
    severity: "C",
    status: "Mocked",
  },
];

function EventList() {
  return (
    <div className="page-stack">
      <Typography.Title level={2}>Event List</Typography.Title>
      <Card>
        <Table
          rowKey="eventId"
          dataSource={mockEvents}
          pagination={false}
          columns={[
            { title: "Event ID", dataIndex: "eventId" },
            { title: "Vehicle ID", dataIndex: "vehicleId" },
            { title: "Type", dataIndex: "type" },
            {
              title: "Severity",
              dataIndex: "severity",
              render: (severity: string) => <Tag color="red">{severity}</Tag>,
            },
            { title: "Status", dataIndex: "status" },
          ]}
        />
      </Card>
    </div>
  );
}

export default EventList;
