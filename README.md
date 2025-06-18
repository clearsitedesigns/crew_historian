# CrewHistorian - AI-Powered Historical Research Crew

A sophisticated multi-agent AI system built with [crewAI](https://crewai.com) that conducts comprehensive historical research and generates visual documentation. CrewHistorian combines web search, historical analysis, and AI-generated visualizations to create complete research reports on any historical topic.

## 🎯 What CrewHistorian Does

CrewHistorian employs a team of specialized AI agents that work together to:

1. **Search** for authentic historical visual materials and documents
2. **Analyze** visual characteristics and artistic elements of historical periods
3. **Research** comprehensive historical context and significance
4. **Synthesize** findings into coherent research reports
5. **Generate** final visualizations that capture the essence of the research

## 🏗️ Project Architecture

### Agents Overview

- **SearcherAgent**: Finds historical visual materials using optimized search queries
- **VisionAgent**: Describes visual characteristics based on historical knowledge
- **HistorianAgent**: Provides comprehensive historical context and analysis
- **WriterAgent**: Synthesizes all research into compelling narratives
- **FinalVisualizationAgent**: Creates comprehensive visual representations

### Custom Tools

- **ScrapingDogSearchTool**: Web search for historical materials
- **MistralVisionTool**: Image analysis capabilities
- **MistralImageCreationTool**: AI-powered image generation

## 🚀 Quick Start Guide

### Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 (crewAI does not support 3.13+ yet)
- **Operating System**: Windows, macOS, or Linux

### Step 1: Install Python and UV

First, ensure you have Python installed:

```bash
python --version  # Should show 3.10.x, 3.11.x, or 3.12.x
```

Install UV (modern Python package manager):

```bash
pip install uv
```

### Step 2: Install CrewAI

Install crewAI globally:

```bash
pip install crewai
```

Or using UV:

```bash
uv add crewai
```

### Step 3: Clone and Setup Project

```bash
# Clone or download this project
cd crew-historian

# Install project dependencies
crewai install

# Or manually with UV
uv install
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required: Mistral AI API key (for LLM and image generation)
MISTRAL_API_KEY=your_mistral_api_key_here

# Required: ScrapingDog API key (for web search)
SCRAPINGDOG_API_KEY=your_scrapingdog_api_key_here
```

#### Getting API Keys

**Mistral AI API Key:**
1. Visit [Mistral AI Console](https://console.mistral.ai/)
2. Create an account and navigate to API Keys
3. Generate a new API key
4. Note: This project uses Mistral for both LLM processing and image generation

**ScrapingDog API Key:**
1. Visit [ScrapingDog](https://scrapingdog.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Note: Free tier available for testing

### Step 5: Test Installation

Run a quick test to ensure everything is working:

```bash
python main.py test "Renaissance art"
```

If successful, you should see:
- Agents being created and assigned tasks
- Search results being found
- Historical analysis being generated
- Final report and visualization being created

## 📖 How to Use CrewHistorian

### Basic Usage

Run research on any historical topic:

```bash
# Using the main script
python main.py run "your historical topic here"

# Examples
python main.py run "Ancient Egyptian pyramids"
python main.py run "1960s counterculture movement"
python main.py run "Medieval castle architecture"
python main.py run "Industrial Revolution inventions"
```

### Using CrewAI Commands

```bash
# Run with default topic
crewai run

# The crew will process the topic defined in main.py
```

### Advanced Usage

You can also import and use CrewHistorian in your own Python scripts:

```python
from crew_historian.crew import CrewHistorian

# Create and run the crew
historian = CrewHistorian()
crew = historian.crew()

# Run research on a specific topic
results = crew.kickoff(inputs={"topic": "Victorian era fashion"})
print(results)
```

## 📁 Project Structure

```
crew-historian/
├── src/crew_historian/
│   ├── config/
│   │   ├── agents.yaml      # Agent definitions and roles
│   │   └── tasks.yaml       # Task descriptions and workflows
│   ├── tools/
│   │   ├── scraping_dog_search_tool.py    # Web search functionality
│   │   ├── mistral_vision_tool.py         # Image analysis
│   │   └── mistral_image_creation_tool.py # Image generation
│   ├── crew.py             # Main crew orchestration
│   └── main.py             # Entry point and CLI
├── final_visualizations/   # Generated images output here
├── crew_historian.log      # Application logs
├── .env                    # Your API keys (create this)
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔧 Customization Guide

### Modifying Agents

Edit `src/crew_historian/config/agents.yaml` to customize agent behavior:

```yaml
SearcherAgent:
  name: "SearcherAgent"
  role: "Historical Visual Materials Researcher"
  goal: "Find authentic historical visual materials using short, focused search queries"
  backstory: "Your custom backstory here..."
```

### Modifying Tasks

Edit `src/crew_historian/config/tasks.yaml` to change task workflows:

```yaml
search_task:
  description: >
    Your custom task description here...
  expected_output: >
    Your expected output format here...
  agent: SearcherAgent
```

### Adding New Tools

Create new tools by extending the BaseTool class:

```python
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class YourCustomTool(BaseTool):
    name: str = "Your Tool Name"
    description: str = "What your tool does"
    args_schema: Type[BaseModel] = YourInputSchema

    def _run(self, argument: str) -> str:
        # Your tool logic here
        return "Tool output"
```

## 📊 Understanding the Output

CrewHistorian generates several types of output:

### 1. Console Output
Real-time progress updates showing:
- Agent activities and decisions
- Search results and findings
- Task completion status

### 2. Log Files
- `crew_historian.log`: Detailed application logs
- `mistral_image_tool.log`: Image generation logs

### 3. Generated Files
- `final_visualizations/`: AI-generated images
- Research reports (displayed in console)

### 4. Research Flow
1. **Search Phase**: Finds relevant historical materials
2. **Analysis Phase**: Examines visual and cultural elements  
3. **Context Phase**: Provides historical background
4. **Synthesis Phase**: Combines all findings
5. **Visualization Phase**: Creates final visual representation

## 🛠️ Troubleshooting

### Common Issues

**"MISTRAL_API_KEY not found"**
- Ensure your `.env` file exists and contains the API key
- Check that the key is correctly formatted (no extra spaces)

**"No search results found"**
- Verify your ScrapingDog API key is valid
- Check your internet connection
- Try a different search topic

**"Agent creation failed"**
- Verify all dependencies are installed: `crewai install`
- Check Python version compatibility (3.10-3.12)

**"Image generation failed"**
- Ensure Mistral API key has image generation permissions
- Check the logs in `mistral_image_tool.log` for details

### Getting Help

1. **Check Logs**: Review `crew_historian.log` for detailed error information
2. **Verify Environment**: Ensure all API keys are set correctly
3. **Test Components**: Run individual tools to isolate issues

## 🔗 Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewai)
- [Mistral AI Documentation](https://docs.mistral.ai/)
- [CrewAI Discord Community](https://discord.com/invite/X4JWnZnxPb)

## 📝 Example Research Topics

Try these topics to see CrewHistorian in action:

- "Ancient Roman architecture"
- "1920s Art Deco movement"
- "Medieval illuminated manuscripts"
- "Japanese woodblock printing"
- "American Civil War photography"
- "Renaissance sculpture techniques"
- "Egyptian hieroglyphic art"
- "Pre-Columbian Aztec artifacts"

## 🤝 Contributing

Feel free to contribute to this project by:
- Adding new tools and capabilities
- Improving agent prompts and behaviors
- Enhancing the research workflow
- Adding support for new data sources

## 📄 License

This project is open source. Please check the license file for details.

---

**Ready to explore history with AI?** Start your first research with:

```bash
python main.py run "your favorite historical topic"
```

Copyright Preston McCauley 2025 - Agent Con 2025