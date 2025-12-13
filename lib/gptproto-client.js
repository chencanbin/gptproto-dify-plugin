/**
 * GPTProto API Client
 * 用于调用 GPTProto 的 Gemini 图像生成 API
 */

const BASE_URL = 'https://gptproto.com/api/v3';

class GPTProtoClient {
  /**
   * @param {string} apiKey - GPTProto API Key (sk-xxxxx)
   */
  constructor(apiKey) {
    if (!apiKey || !apiKey.startsWith('sk-')) {
      throw new Error('Invalid API Key. Must start with "sk-"');
    }
    this.apiKey = apiKey;
  }

  /**
   * 提交图像生成任务
   * @param {Object} options - 生成选项
   * @param {string} options.prompt - 图像描述提示词
   * @param {string} options.size - 图像尺寸 (1K, 2K, etc.)
   * @param {string} options.aspect_ratio - 宽高比 (1:1, 3:2, 16:9, etc.)
   * @param {string} options.output_format - 输出格式 (png, jpg, webp)
   * @returns {Promise<{result_id: string}>} - 任务 ID
   */
  async submitTask(options) {
    const { prompt, size = '1K', aspect_ratio = '1:1', output_format = 'png' } = options;

    if (!prompt) {
      throw new Error('Prompt is required');
    }

    const response = await fetch(
      `${BASE_URL}/google/gemini-3-pro-image-preview/text-to-image`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt,
          size,
          aspect_ratio,
          output_format
        })
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to submit task: ${response.status} - ${error}`);
    }

    const data = await response.json();
    return data;
  }

  /**
   * 获取任务结果
   * @param {string} resultId - 任务 ID
   * @returns {Promise<Object>} - 任务结果
   */
  async getResult(resultId) {
    if (!resultId) {
      throw new Error('Result ID is required');
    }

    const response = await fetch(
      `${BASE_URL}/predictions/${resultId}/result`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to get result: ${response.status} - ${error}`);
    }

    return await response.json();
  }

  /**
   * 轮询等待任务完成
   * @param {string} resultId - 任务 ID
   * @param {Object} options - 轮询选项
   * @param {number} options.interval - 轮询间隔 (ms)，默认 2000
   * @param {number} options.timeout - 超时时间 (ms)，默认 300000 (5分钟)
   * @returns {Promise<Object>} - 最终结果
   */
  async waitForResult(resultId, options = {}) {
    const { interval = 2000, timeout = 300000 } = options;
    const startTime = Date.now();

    while (true) {
      if (Date.now() - startTime > timeout) {
        throw new Error('Timeout waiting for result');
      }

      const result = await this.getResult(resultId);

      // 检查任务状态
      if (result.status === 'succeeded' || result.status === 'completed') {
        return result;
      }

      if (result.status === 'failed' || result.status === 'error') {
        throw new Error(`Task failed: ${result.error || 'Unknown error'}`);
      }

      // 等待后继续轮询
      await this.sleep(interval);
    }
  }

  /**
   * 一站式生成图像（提交任务 + 轮询结果）
   * @param {Object} options - 生成选项
   * @returns {Promise<Object>} - 生成结果
   */
  async generateImage(options) {
    // 1. 提交任务
    const submitResult = await this.submitTask(options);
    const resultId = submitResult.result_id || submitResult.id || submitResult.prediction_id;

    if (!resultId) {
      throw new Error('No result ID returned from submit task');
    }

    // 2. 轮询等待结果
    const result = await this.waitForResult(resultId, {
      interval: options.pollInterval || 2000,
      timeout: options.timeout || 300000
    });

    return result;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = GPTProtoClient;
