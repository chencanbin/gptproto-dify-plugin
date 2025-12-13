/**
 * Text to Image Tool Implementation
 * 文生图工具实现
 */

const GPTProtoClient = require('../lib/gptproto-client');

class TextToImageTool {
  constructor() {
    this.name = 'text_to_image';
  }

  /**
   * 执行文生图
   * @param {Object} params - 工具参数
   * @param {string} params.prompt - 图像描述提示词
   * @param {string} params.size - 图像尺寸
   * @param {string} params.aspect_ratio - 宽高比
   * @param {string} params.output_format - 输出格式
   * @param {Object} credentials - 用户凭证
   * @param {string} credentials.api_key - GPTProto API Key
   * @returns {Promise<Object>} - 执行结果
   */
  async execute(params, credentials) {
    const { prompt, size = '1K', aspect_ratio = '1:1', output_format = 'png' } = params;
    const { api_key } = credentials;

    if (!api_key) {
      return {
        success: false,
        error: 'API Key is required. Please configure your GPTProto API Key.'
      };
    }

    if (!prompt) {
      return {
        success: false,
        error: 'Prompt is required'
      };
    }

    try {
      const client = new GPTProtoClient(api_key);

      console.log(`[TextToImage] Generating image with prompt: "${prompt.substring(0, 50)}..."`);

      // 一站式生成图像
      const result = await client.generateImage({
        prompt,
        size,
        aspect_ratio,
        output_format,
        pollInterval: 2000,  // 2秒轮询一次
        timeout: 300000      // 5分钟超时
      });

      console.log('[TextToImage] Image generated successfully');

      // 返回结果
      return {
        success: true,
        data: {
          image_url: result.output || result.url || result.image_url,
          status: result.status,
          prompt,
          size,
          aspect_ratio,
          output_format
        }
      };

    } catch (error) {
      console.error('[TextToImage] Error:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }
}

module.exports = TextToImageTool;
