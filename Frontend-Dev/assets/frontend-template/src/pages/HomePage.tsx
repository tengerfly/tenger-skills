import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Card, Skeleton, Space, Tag, Typography } from '../components/ui';
import { fetchDemoPing } from '../api/demo';

/**
 * 模板首页（活示例）：演示标准「加载/错误/成功」三态 + 请求层用法 + 组件一律从 ui 出口引入。
 * 新项目接入真实首页后整页替换本文件。
 */
export default function HomePage() {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['demo', 'ping'],
    queryFn: fetchDemoPing,
  });

  return (
    <div className="page-col">
      <section className="home-hero">
        <h1>前端模板已就绪</h1>
        <p>
          Vite + React 18 + TypeScript strict + React Query + Sass token，组件库经 ui 出口隔离可整体替换。
          下方示例演示了页面三态约定。
        </p>
        <Space>
          <Tag color="processing">request() 统一解包</Tag>
          <Tag color="success">三态渲染</Tag>
          <Tag color="warning">SSE 流式（api/stream.ts）</Tag>
        </Space>
      </section>

      <Card title="请求层三态演示（GET /demo/ping，未启动后端时应看到错误态）" style={{ maxWidth: 640 }}>
        {isLoading ? (
          <Skeleton active paragraph={{ rows: 1 }} />
        ) : isError ? (
          <Alert
            type="error"
            showIcon
            message="请求失败"
            description="后端未就绪或接口不存在。真实页面照此模式：Skeleton / Alert+重新加载 / 数据渲染。"
            action={
              <Button size="small" danger loading={isFetching} onClick={() => refetch()}>
                重新加载
              </Button>
            }
          />
        ) : (
          <Typography.Paragraph code copyable>
            {data?.message}
          </Typography.Paragraph>
        )}
      </Card>
    </div>
  );
}
