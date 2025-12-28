# GPTProto

A comprehensive AI toolkit plugin for [Dify](https://dify.ai), providing access to **30 cutting-edge AI models** through the GPTProto API.

## Features

- **30 AI Tools** - Complete coverage of text, image, and video generation
- **Multi-Model Support** - Access Gemini, Claude, GPT, Sora, Veo, Hailuo, Seedream models
- **Async Task Processing** - Automatic polling for long-running generation tasks
- **Bilingual Interface** - Full English and Chinese localization

## Available Tools

### Image Generation (7 tools)

| Tool | Model | Description |
|------|-------|-------------|
| `gemini-3-pro-image-preview / text-to-image` | Gemini 3 Pro | High-quality image generation with 1K/2K resolution |
| `gemini-2.5-flash / text-to-image` | Gemini 2.5 Flash | Fast image generation with multiple aspect ratios |
| `gpt-image-1 / text-to-image` | GPT Image 1 | OpenAI's image generation with quality control |
| `seedream-3.0 / text-to-image` | Seedream 3.0 | ByteDance's image model with style options |
| `seedream-4.5 / text-to-image` | Seedream 4.5 | Latest Seedream with enhanced quality |
| `nano-banana / text-to-image` | Nano Banana | Lightweight fast image generation |

### Image Editing (5 tools)

| Tool | Model | Description |
|------|-------|-------------|
| `gemini-3-pro-image-preview / image-edit` | Gemini 3 Pro | Edit images with text prompts and reference images |
| `gpt-image-1 / image-edit` | GPT Image 1 | OpenAI's image editing capabilities |
| `seedream-3.0 / image-edit` | Seedream 3.0 | ByteDance's image editing |
| `seedream-4.5 / image-edit` | Seedream 4.5 | Advanced image editing with style control |
| `nano-banana / image-edit` | Nano Banana | Fast image editing |

### Video Generation (10 tools)

| Tool | Model | Description |
|------|-------|-------------|
| `sora-2 / text-to-video` | Sora 2 | OpenAI's cinematic video generation (5/10/20s) |
| `sora-2 / image-to-video` | Sora 2 | Animate images into videos |
| `veo-3.1 / text-to-video` | Veo 3.1 | Google's latest video model |
| `veo-3.1 / image-to-video` | Veo 3.1 | Image animation with Veo |
| `veo-3-pro / text-to-video` | Veo 3 Pro | Professional video generation |
| `veo-3-pro / image-to-video` | Veo 3 Pro | Professional image-to-video |
| `hailuo-02-pro / text-to-video` | Hailuo 02 Pro | MiniMax's professional video model |
| `hailuo-02-pro / image-to-video` | Hailuo 02 Pro | Image animation with Hailuo |
| `hailuo-2.3-standard / text-to-video` | Hailuo 2.3 | Standard quality video generation |
| `hailuo-2.3-fast / image-to-video` | Hailuo 2.3 | Fast image-to-video conversion |

### Text Generation (8 tools)

| Tool | Model | Description |
|------|-------|-------------|
| `gemini-3-pro-preview / text-generation` | Gemini 3 Pro | Advanced reasoning with video upload and web search |
| `gemini-2.5-pro / text-generation` | Gemini 2.5 Pro | Multimodal with document analysis |
| `gemini-2.5-flash-lite / text-generation` | Gemini 2.5 Flash Lite | Fast and efficient text generation |
| `claude-sonnet-4.5 / multimodal` | Claude Sonnet 4.5 | Balanced intelligence and speed with PDF support |
| `claude-opus-4.5 / multimodal` | Claude Opus 4.5 | Most powerful Claude with extended thinking |
| `gpt-5.2 / text-generation` | GPT-5.2 | OpenAI's latest model with web search |
| `gpt-5.2-pro / text-generation` | GPT-5.2 Pro | Enhanced capabilities with file analysis |
| `gpt-4o / text-generation` | GPT-4o | Multimodal with real-time search |

## Installation

### Method 1: Install from Dify Marketplace

1. Open Dify and go to **Plugins** page
2. Search for "GPTProto" in the marketplace
3. Click **Install**
4. Configure your API key

### Method 2: Manual Installation

1. Download the latest `.difypkg` file from [Releases](https://github.com/chencanbin/gptproto-dify-plugin/releases)
2. Go to Dify **Plugins** → **Install from local file**
3. Upload the `.difypkg` file
4. Configure your GPTProto API key

## Configuration

### Get API Key

1. Visit [GPTProto Dashboard](https://gptproto.com/dashboard/api-key?source=dify)
2. Create an account or sign in
3. Generate a new API key
4. Copy the key to your Dify plugin settings

### Configure in Dify

1. Go to **Plugins** → **GPTProto**
2. Click **Authorize**
3. Enter your GPTProto API Key
4. Click **Save**

## Usage Examples

### Image Generation

```
Tool: gemini-3-pro-image-preview / text-to-image
Prompt: "A serene Japanese garden with cherry blossoms, koi pond, and traditional wooden bridge at sunset"
Size: 2K
Aspect Ratio: 16:9
```

### Video Generation

```
Tool: sora-2 / text-to-video
Prompt: "A astronaut walking on Mars surface, cinematic lighting, dust particles floating"
Duration: 10 seconds
Orientation: Landscape
Size: Large (1080p)
```

### Text Generation with Web Search

```
Tool: gpt-5.2 / text-generation
Prompt: "What are the latest developments in AI research this week?"
Enable Web Search: true
```

## Technical Details

- **Plugin Version**: 0.0.51
- **Runtime**: Python 3.12
- **Architecture**: amd64, arm64
- **Memory**: 1MB

## API Reference

All tools use the GPTProto API. For detailed API documentation, visit:
- [GPTProto API Docs](https://gptproto.com/docs)
- [API Endpoints](https://gptproto.com/apis/list)

## Privacy & Security

- API keys are encrypted and stored securely in Dify
- User prompts are sent to GPTProto API for processing only
- No data is stored by the plugin itself
- See [PRIVACY.md](PRIVACY.md) for detailed privacy policy

## Support

- **Website**: [https://gptproto.com?source=dify](https://gptproto.com?source=dify)
- **Issues**: [GitHub Issues](https://github.com/chencanbin/gptproto-dify-plugin/issues)
- **Email**: support@gptproto.com

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Made with love by [GPTProto](https://gptproto.com?source=dify)
