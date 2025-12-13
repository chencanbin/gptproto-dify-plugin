require('dotenv').config();
const express = require('express');
const cors = require('cors');
const TextToImageTool = require('./tools/text_to_image');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// 工具实例
const tools = {
  text_to_image: new TextToImageTool()
};

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Dify 插件主入口
app.post('/api/dify/receive', async (req, res) => {
  try {
    const { point, params } = req.body;

    console.log(`[Dify] Received request - point: ${point}`);

    // 处理 ping 请求
    if (point === 'ping') {
      return res.json({ result: 'pong' });
    }

    // 处理工具调用
    if (point === 'app.tool.invoke' || point === 'tool.invoke') {
      const { tool_name, tool_parameters, credentials } = params || {};

      const tool = tools[tool_name];
      if (!tool) {
        return res.status(400).json({ error: `Unknown tool: ${tool_name}` });
      }

      const result = await tool.execute(tool_parameters, credentials);

      if (result.success) {
        return res.json({
          result: typeof result.data === 'string'
            ? result.data
            : JSON.stringify(result.data, null, 2)
        });
      } else {
        return res.status(400).json({ error: result.error });
      }
    }

    // 处理凭证验证
    if (point === 'provider.validate_credentials') {
      const { credentials } = params || {};
      const { api_key } = credentials || {};

      if (!api_key || !api_key.startsWith('sk-')) {
        return res.status(400).json({
          error: 'Invalid API Key. Must start with "sk-"'
        });
      }

      // TODO: 可选 - 调用 API 验证 key 是否有效
      return res.json({ result: 'ok' });
    }

    // 未知的 point 类型
    return res.status(400).json({ error: `Unknown point: ${point}` });

  } catch (error) {
    console.error('[Dify] Error processing request:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`🚀 GPTProto Dify Plugin is running on port ${PORT}`);
  console.log(`📍 Health check: http://localhost:${PORT}/health`);
  console.log(`📍 API endpoint: http://localhost:${PORT}/api/dify/receive`);
});

module.exports = app;
