import os
from dotenv import load_dotenv
from loguru import logger
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew

# Load environment variables
load_dotenv()

# Logging
logger.add("crew_historian.log", rotation="1 MB", retention="10 days", level="DEBUG")
logger.info("Loguru logger initialized.")

# Load API key
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY not found in .env")

# Initialize LLM with ONLY valid parameters
llm = LLM(
    model="mistral/mistral-small-latest",
    temperature=0.4,
    api_key=MISTRAL_API_KEY
)
logger.info("Mistral LLM initialized.")

# Custom tools
from crew_historian.tools.scraping_dog_search_tool import ScrapingDogSearchTool
from crew_historian.tools.mistral_image_creation_tool import MistralImageCreationTool
from crew_historian.tools.mistral_vision_tool import MistralVisionTool

scraping_tool = ScrapingDogSearchTool()
image_gen_tool = MistralImageCreationTool()
vision_tool = MistralVisionTool()
logger.info("Custom tools initialized.")

@CrewBase
class CrewHistorian:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        self.llm = llm

    @agent
    def SearcherAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["SearcherAgent"],
            llm=self.llm,
            tools=[scraping_tool],
            verbose=True
        )

    @agent
    def VisionAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["VisionAgent"],
            llm=self.llm,
            tools=[vision_tool],
            verbose=True
        )

    @agent
    def HistorianAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["HistorianAgent"],
            llm=self.llm,
            tools=[],
            verbose=True
        )

    @agent
    def WriterAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["WriterAgent"],
            llm=self.llm,
            tools=[],
            verbose=True
        )

    @agent
    def FinalVisualizationAgent(self) -> Agent:
        return Agent(
            config=self.agents_config["FinalVisualizationAgent"],
            llm=self.llm,
            tools=[image_gen_tool],
            verbose=True
        )

    @task
    def search_task(self) -> Task:
        return Task(
            config=self.tasks_config["search_task"], 
            agent=self.SearcherAgent()
        )

    @task
    def vision_task(self) -> Task:
        return Task(
            config=self.tasks_config["vision_task"], 
            agent=self.VisionAgent(), 
            dependencies=[self.search_task()]
        )

    @task
    def history_context_task(self) -> Task:
        return Task(
            config=self.tasks_config["history_context_task"], 
            agent=self.HistorianAgent(), 
            dependencies=[self.vision_task()]
        )

    @task
    def writeup_task(self) -> Task:
        return Task(
            config=self.tasks_config["writeup_task"], 
            agent=self.WriterAgent(), 
            dependencies=[self.history_context_task()]
        )

    @task
    def final_visualization_task(self) -> Task:
        return Task(
            config=self.tasks_config["final_visualization_task"], 
            agent=self.FinalVisualizationAgent(), 
            dependencies=[self.writeup_task()]
        )

    @crew
    def crew(self) -> Crew:
        logger.info("Constructing the full crew with all agents and tasks.")
        return Crew(
            agents=[
                self.SearcherAgent(),
                self.VisionAgent(),
                self.HistorianAgent(),
                self.WriterAgent(),
                self.FinalVisualizationAgent()
            ],
            tasks=[
                self.search_task(),
                self.vision_task(),
                self.history_context_task(),
                self.writeup_task(),
                self.final_visualization_task()
            ],
            process=Process.sequential,
            verbose=True
        )