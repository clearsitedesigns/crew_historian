# CrewHistorian - AI-Powered Historical Research Crew

A sophisticated multi-agent AI system built with crewAI that conducts comprehensive historical research and generates visual documentation. CrewHistorian combines web search, historical analysis, and AI-generated visualizations to create complete research reports on any historical topic.

---

🌟 What CrewHistorian Does
CrewHistorian employs a team of specialized AI agents that work together to:

* Search for authentic historical visual materials and documents
* Analyze visual characteristics and artistic elements of historical periods
* Research comprehensive historical context and significance
* Synthesize findings into coherent research reports
* Generate final visualizations that capture the essence of the research

---

🏛️ Project Architecture

### Agents Overview

* **SearcherAgent**: Finds historical visual materials using optimized search queries (via SerpAPI)
* **VisionAgent**: Describes visual characteristics based on historical knowledge
* **HistorianAgent**: Provides comprehensive historical context and analysis
* **WriterAgent**: Synthesizes all research into compelling narratives
* **FinalVisualizationAgent**: Creates comprehensive visual representations

### Custom Tools

* **SerpApiSearchTool** *(new)*: Enhanced web search via SerpAPI (text + image queries)
* **MistralVisionTool**: Image analysis capabilities
* **MistralImageCreationTool**: AI-powered image generation

---

🚀 Quick Start Guide

### Prerequisites

* Python: Version 3.10, 3.11, or 3.12 (crewAI does not support 3.13+ yet)
* Operating System: Windows, macOS, or Linux

### Step 1: Install Python and UV

```bash
python --version  # Should show 3.10.x, 3.11.x, or 3.12.x
pip install uv
```

### Step 2: Install CrewAI

```bash
pip install crewai
# Or using UV:
uv add crewai
```

### Step 3: Clone and Setup Project

```bash
git clone https://github.com/your-repo/crew-historian
cd crew-historian
crewai install
# Or manually:
uv install
```

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
MISTRAL_API_KEY=your_mistral_api_key_here
SCRAPINGDOG_API_KEY=your_scrapingdog_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

> ✅ **Important**: Make sure your `.env` file is correctly placed in the root directory. When using macOS or Conda environments, and to ensure all environment variables and imports resolve correctly, you may need to run the script like this:

```bash
PYTHONPATH=src python src/crew_historian/main.py test "The Rise Of The Baroque Movement In Art"
```

---

### Getting API Keys

* **Mistral AI**: [Mistral Console](https://mistral.ai)
* **ScrapingDog**: [ScrapingDog Website](https://www.scrapingdog.com)
* **SerpAPI**: [SerpAPI Console](https://serpapi.com)

---

### Step 5: Test Installation

```bash
python main.py test "Renaissance art"
```

Expected Output:

* Agents being created and assigned tasks
* Search results found using SerpAPI
* Visual and historical analysis completed
* Final report and visualization created

---

📖 How to Use CrewHistorian

### Basic Usage

```bash
python main.py run "your historical topic here"
```

Examples:

```bash
python main.py run "Ancient Egyptian pyramids"
python main.py run "1960s counterculture movement"
```

### Using CrewAI Commands

```bash
crewai run  # Runs the crew based on main.py logic
```

---

### Advanced Usage in Code

```python
from crew_historian.crew import CrewHistorian

historian = CrewHistorian()
crew = historian.crew()
results = crew.kickoff(inputs={"topic": "Victorian era fashion"})
print(results)
```

---

📁 Project Structure

```
crew-historian/
├── src/crew_historian/
│   ├── config/
│   │   ├── agents.yaml
│   │   └── tasks.yaml
│   ├── tools/
│   │   ├── scraping_dog_search_tool.py
│   │   ├── serpapi_search_tool.py
│   │   ├── mistral_vision_tool.py
│   │   └── mistral_image_creation_tool.py
│   ├── crew.py
│   └── main.py
├── final_visualizations/
├── crew_historian.log
├── .env
├── .env.example
└── README.md
```

---

📊 Understanding the Output

**New Flow Summary:**
graph TD
    %% Style for the Agent subgraphs
    classDef agent fill:#f0f7ff,stroke:#0063a0,stroke-width:2px;

    %% Subgraph for the SearcherAgent
    subgraph "🔎 SearcherAgent: Historical Visual Materials Researcher"
        direction LR
        search_task["`search_task`: Find background & image URLs"]
    end

    %% Subgraph for the VisionAgent
    subgraph "👁️ VisionAgent: Visual Content Analyst"
        direction LR
        image_analysis_task["`image_analysis_task`: Describe visual elements"]
        vision_task["`vision_task`: Summarize image's contribution"]
    end

    %% Subgraph for the HistorianAgent
    subgraph "🏛️ HistorianAgent: Historical Context Specialist"
        direction LR
        history_context_task["`history_context_task`: Provide deeper historical context"]
    end

    %% Subgraph for the WriterAgent
    subgraph "✍️ WriterAgent: Research Synthesis Writer"
        direction LR
        writeup_task["`writeup_task`: Write a cohesive article"]
    end

    %% Subgraph for the FinalVisualizationAgent
    subgraph "🎨 FinalVisualizationAgent: Research Synthesis Visualizer"
        direction LR
        final_visualization_task["`final_visualization_task`: Generate a custom visual summary"]
    end

    %% Define the workflow connections between tasks
    search_task --> image_analysis_task;
    image_analysis_task --> vision_task;

    %% Historian and Writer use multiple inputs
    search_task --> history_context_task;
    vision_task --> history_context_task;
    history_context_task --> writeup_task;
    vision_task --> writeup_task;

    %% Final visualization is based on the writeup
    writeup_task --> final_visualization_task;

    %% Assign class to all subgraphs
    class search_task,image_analysis_task,vision_task,history_context_task,writeup_task,final_visualization_task agent;

    

🛠️ Troubleshooting

| Issue                       | Fix                                               |
| --------------------------- | ------------------------------------------------- |
| `MISTRAL_API_KEY not found` | Ensure `.env` exists with the correct key         |
| No search results found     | Validate your SerpAPI key and internet connection |
| Agent creation failed       | Check Python version and dependencies             |
| Image generation failed     | Confirm Mistral API has image rights              |

---

🔗 Resources

* [CrewAI GitHub](https://github.com/joaomdmoura/crewAI)
* [Mistral AI](https://mistral.ai/)
* [ScrapingDog](https://www.scrapingdog.com/)
* [SerpAPI](https://serpapi.com)
* [CrewAI Discord](https://discord.gg/crewai)

---

© Preston McCauley 2025 – Agent Con 2025
