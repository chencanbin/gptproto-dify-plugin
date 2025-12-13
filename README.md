# GPTProto Dify Plugin

使用 GPTProto Gemini-3-Pro API 生成图像的 Dify 插件。

## 功能

- **文生图 (Text to Image)**: 根据文本提示词生成高质量图像
  - 支持多种尺寸: 1K, 2K
  - 支持多种宽高比: 1:1, 3:2, 2:3, 16:9, 9:16
  - 支持多种输出格式: PNG, JPG, WebP

## 项目结构

```
gptproto-dify-plugin/
├── manifest.yaml              # 插件元数据配置
├── package.json               # Node.js 依赖配置
├── index.js                   # 插件入口文件
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略配置
├── lib/
│   └── gptproto-client.js     # GPTProto API 客户端
├── provider/
│   └── tools.yaml             # 工具提供者配置 (含凭证配置)
├── tools/
│   ├── text_to_image.yaml     # 文生图工具定义
│   └── text_to_image.js       # 文生图工具实现
└── _assets/
    └── icon.svg               # 插件图标
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

### 3. 测试插件

```bash
# 健康检查
curl http://localhost:3000/health

# 测试 Ping
curl -X POST http://localhost:3000/api/dify/receive \
  -H "Content-Type: application/json" \
  -d '{"point": "ping"}'

# 测试凭证验证
curl -X POST http://localhost:3000/api/dify/receive \
  -H "Content-Type: application/json" \
  -d '{
    "point": "provider.validate_credentials",
    "params": {
      "credentials": {
        "api_key": "sk-your-api-key"
      }
    }
  }'

# 测试文生图
curl -X POST http://localhost:3000/api/dify/receive \
  -H "Content-Type: application/json" \
  -d '{
    "point": "tool.invoke",
    "params": {
      "tool_name": "text_to_image",
      "tool_parameters": {
        "prompt": "A beautiful sunset over the ocean",
        "size": "1K",
        "aspect_ratio": "16:9",
        "output_format": "png"
      },
      "credentials": {
        "api_key": "sk-your-api-key"
      }
    }
  }'
```

## 配置说明

### 用户凭证

使用此插件前，用户需要在 Dify 中配置 GPTProto API Key：

1. 在 Dify 工作区中添加此插件
2. 输入您的 GPTProto API Key (格式: `sk-xxxxx`)
3. 保存配置

### API 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| prompt | string | 是 | - | 图像描述提示词 |
| size | string | 否 | 1K | 图像尺寸 (1K, 2K) |
| aspect_ratio | string | 否 | 1:1 | 宽高比 |
| output_format | string | 否 | png | 输出格式 |

## 开发指南

### 添加新工具

1. 在 `tools/` 目录下创建 `your_tool.yaml` 定义工具参数
2. 在 `tools/` 目录下创建 `your_tool.js` 实现工具逻辑
3. 在 `provider/tools.yaml` 中注册新工具
4. 在 `index.js` 中注册工具实例

### API 客户端使用

```javascript
const GPTProtoClient = require('./lib/gptproto-client');

const client = new GPTProtoClient('sk-your-api-key');

// 一站式生成图像
const result = await client.generateImage({
  prompt: 'A beautiful landscape',
  size: '1K',
  aspect_ratio: '16:9',
  output_format: 'png'
});

console.log(result.image_url);
```

## 部署

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0

### 生产部署

```bash
npm start
```

## 许可证

MIT License

## 相关链接

- [Dify 官方文档](https://docs.dify.ai/)
- [Dify 插件开发指南](https://docs.dify.ai/en/develop-plugin/getting-started/getting-started-dify-plugin)
- [GPTProto API 文档](https://gptproto.com)
