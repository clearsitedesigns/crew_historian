import sys
from loguru import logger
from crew_historian.crew import CrewHistorian

logger.info("=== Crew Historian CLI Started ===")
logger.debug(f"Command received: {sys.argv}")

def run(topic: str):
    try:
        historian = CrewHistorian()
        crew = historian.crew()
        crew.kickoff(inputs={"topic": topic})
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def replay():
    logger.info("Replay mode not implemented yet.")

def train():
    logger.info("Training mode not implemented yet.")

def test(prompt="Describe the Great Wall of China"):
    logger.info("Running test mode...")
    run(prompt)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [run|test|train|replay] [optional:topic]")
        sys.exit(1)

    command = sys.argv[1]
    topic = sys.argv[2] if len(sys.argv) > 2 else "A historical topic"

    if command == "run":
        run(topic)
    elif command == "test":
        test(topic)
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    else:
        logger.error(f"Unknown command: {command}")
        print("Valid commands: run, test, train, replay")
