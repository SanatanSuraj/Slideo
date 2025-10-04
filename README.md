<p align="center">
  <img src="readme_assets/images/presenton-logo.png" height="90" alt="Presenton Logo" />
</p>

<p align="center">
  <a href="https://discord.gg/9ZsKKxudNE">
    <img src="https://img.shields.io/badge/Discord-Join%20Community-5865F2?logo=discord&style=for-the-badge" alt="Join our Discord" />
  </a>
  &nbsp;
  <a href="https://x.com/presentonai">
    <img src="https://img.shields.io/badge/X-Follow%20Us-000000?logo=twitter&style=for-the-badge" alt="Follow us on X" />
  </a>
</p>

# Open-Source AI Presentation Generator and API (Gamma, Beautiful AI, Decktopus Alternative)

**Presenton** is an open-source application for generating presentations with AI — all running locally on your device. Stay in control of your data and privacy while using models like OpenAI and Google Gemini.

__✨ Now, generate presentations with your existing PPTX file! Just upload your presentation file to create template design and then use that template to generate on brand and on design presentation on any topic.__

![Demo](readme_assets/demo.gif)

> [!NOTE]
> **Enterprise Inquiries:**
> For enterprise use, custom deployments, or partnership opportunities, contact us at **[suraj@presenton.ai](mailto:suraj@presenton.ai)**.

> [!IMPORTANT]
> Like Presenton? A ⭐ star shows your support and encourages us to keep building!

> [!TIP]
> For detailed setup guides, API documentation, and advanced configuration options, visit our **[Official Documentation](https://docs.presenton.ai)**

## ✨ More Freedom with AI Presentations

Presenton gives you complete control over your AI presentation workflow. Choose your models, customize your experience, and keep your data private.

* ✅ **Custom Templates & Themes** — Create unlimited presentation designs with HTML and Tailwind CSS
* ✅ **AI Template Generation** — Create presentation templates from existing Powerpoint documents.
* ✅ **Flexible Generation** — Build presentations from prompts or uploaded documents
* ✅ **Export Ready** — Save as PowerPoint (PPTX) and PDF with professional formatting
* ✅ **Built-In MCP Server** — Generate presentations over Model Context Protocol
* ✅ **Bring Your Own Key** — Use your own API keys for OpenAI, Google Gemini, Anthropic Claude, or any compatible provider. Only pay for what you use, no hidden fees or subscriptions.
* ✅ **OpenAI API Compatible** — Connect to any OpenAI-compatible endpoint with your own models
* ✅ **Multi-Provider Support** — Mix and match text and image generation providers
* ✅ **Versatile Image Generation** — Choose from DALL-E 3, Gemini Flash, Pexels, or Pixabay
* ✅ **Rich Media Support** — Icons, charts, and custom graphics for professional presentations
* ✅ **Runs Locally** — All processing happens on your device, no cloud dependencies
* ✅ **API Deployment** — Host as your own API service for your team
* ✅ **Fully Open-Source** — Apache 2.0 licensed, inspect, modify, and contribute

## Presenton Cloud
<a href="https://presenton.ai" target="_blank" align="center">
  
  <img src="readme_assets/cloud-banner.png" height="350" alt="Presenton Logo" />
</a>

## 🚀 Local Development Setup

### Prerequisites
- **Node.js 20+**
- **Python 3.11**
- **npm** (comes with Node.js)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd presenton
```

2. **Install dependencies**
```bash
bash setup.sh
```

3. **Start the application**
```bash
# Quick start with automatic process management
./run_local.sh

# Or use npm scripts
npm run dev    # Development mode
npm start      # Production mode
```

4. **Access the application**
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 🚀 Quick Start Scripts

**`setup.sh`** - Automated setup script:
- Checks Node.js 20+ and Python 3.11+
- Installs all dependencies
- Creates `.env` file from template
- Sets up app data directory

**`run_local.sh`** - Development runner:
- Automatically kills existing processes
- Starts FastAPI backend (port 8000)
- Starts Next.js frontend (port 3000)
- Graceful shutdown with Ctrl+C
- Colorful status output
- **MCP Server**: http://localhost:8001

### Environment Configuration

**API keys are configured exclusively through environment variables** - no manual key entry in the UI.

```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required Environment Variables:**

```bash
# Choose your LLM provider
LLM=openai  # or google, anthropic

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o

# Google Gemini Configuration  
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_MODEL=gemini-2.0-flash-exp

# Anthropic Claude Configuration (Optional)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Image Generation
IMAGE_PROVIDER=dall-e-3
PEXELS_API_KEY=your-pexels-api-key-here
PIXABAY_API_KEY=your-pixabay-api-key-here

# Optional Settings
CAN_CHANGE_KEYS=false  # Disable UI key changes for security
WEB_GROUNDING=false
DISABLE_ANONYMOUS_TELEMETRY=false
```

**Security Note:** API keys are never stored in the browser or local storage. They are only read from environment variables for maximum security.

## Generate Presentation over API

### Generate Presentation

Endpoint: `/api/v1/ppt/presentation/generate`

Method: `POST`

Content-Type: `application/json`

#### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| content | string | Yes | The content for generating the presentation |
| slides_markdown | string[] \| null | No | The markdown for the slides |
| instructions | string \| null | No | The instruction for generating the presentation |
| tone | string | No | The tone to use for the text (default: "default"). Available options: "default", "casual", "professional", "funny", "educational", "sales_pitch" |
| verbosity | string | No | How verbose the text should be (default: "standard"). Available options: "concise", "standard", "text-heavy" |
| web_search | boolean | No | Whether to enable web search (default: false) |
| n_slides | integer | No | Number of slides to generate (default: 8) |
| language | string | No | Language for the presentation (default: "English") |
| template | string | No | Template to use for the presentation (default: "general") |
| include_table_of_contents | boolean | No | Whether to include a table of contents (default: false) |
| include_title_slide | boolean | No | Whether to include a title slide (default: true) |
| files | string[] \| null | No | Files to use for the presentation. Use /api/v1/ppt/files/upload to upload files |
| export_as | string | No | Export format (default: "pptx"). Available options: "pptx", "pdf" |

#### Response

```json
{
    "presentation_id": "string",
    "path": "string",
    "edit_path": "string"
}
```

#### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/ppt/presentation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Introduction to Machine Learning",
    "n_slides": 5,
    "language": "English",
    "template": "general",
    "export_as": "pptx"
  }'
```

#### Example Response

```json
{
  "presentation_id": "d3000f96-096c-4768-b67b-e99aed029b57",
  "path": "/app_data/d3000f96-096c-4768-b67b-e99aed029b57/Introduction_to_Machine_Learning.pptx",
  "edit_path": "/presentation?id=d3000f96-096c-4768-b67b-e99aed029b57"
}
```

> **Note:** Make sure to prepend your server's root URL to the path and edit_path fields in the response to construct valid links.

For detailed info checkout [API documentation](https://docs.presenton.ai/using-presenton-api).

### API Tutorials
- [Generate Presentations via API in 5 minutes](https://docs.presenton.ai/tutorial/generate-presentation-over-api)
- [Create Presentations from CSV using AI](https://docs.presenton.ai/tutorial/generate-presentation-from-csv)
- [Create Data Reports Using AI](https://docs.presenton.ai/tutorial/create-data-reports-using-ai)

## Roadmap
- [x] Support for custom HTML templates by developers
- [x] Support for accessing custom templates over API
- [x] Implement MCP server
- [ ] Ability for users to change system prompt
- [X] Support external SQL database

## UI Features

### 1. Add prompt, select number of slides and language
![Demo](readme_assets/images/prompting.png)

### 2. Select theme
![Demo](readme_assets/images/select-theme.png)

### 3. Review and edit outline
![Demo](readme_assets/images/outline.png)

### 4. Select theme
![Demo](readme_assets/images/select-theme.png)

### 5. Present on app
![Demo](readme_assets/images/present.png)

### 6. Change theme
![Demo](readme_assets/images/change-theme.png)

### 7. Export presentation as PDF and PPTX
![Demo](readme_assets/images/export-presentation.png)

## Community
[Discord](https://discord.gg/9ZsKKxudNE)

## License

Apache 2.0# Slideo
