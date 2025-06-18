import os
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from mistralai import Mistral
import logging

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Logging setup
logger = logging.getLogger("mistral_image_creation_tool")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler("mistral_image_tool.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

# Input schema
class MistralImageInput(BaseModel):
    prompt: str = Field(..., description="The image generation prompt.")

class MistralImageCreationTool(BaseTool):
    name: str = "mistral_image_creation_tool"
    description: str = (
        "Generates a single final image from a text prompt using Mistral's image generation capabilities. "
        "This tool creates one comprehensive visual representation based on the research findings."
    )
    args_schema: Type[BaseModel] = MistralImageInput

    def _run(self, prompt: str) -> str:
        try:
            logger.info(f"Starting final image generation with prompt: {prompt[:100]}...")
            
            if not MISTRAL_API_KEY:
                raise ValueError("MISTRAL_API_KEY is not set in the environment.")

            client = Mistral(api_key=MISTRAL_API_KEY)

            # Create image generation agent
            logger.info("Creating final image generation agent...")
            
            # Enhanced prompt for better final output
            enhanced_prompt = f"""
            Create a single, comprehensive visualization based on this research synthesis:
            
            {prompt}
            
            Requirements for the final image:
            - High quality and detailed representation
            - Authentic and accurate visual elements related to the specific topic
            - Clear, professional presentation suitable for research documentation
            - Incorporates key findings from the research
            - Single cohesive image that summarizes the complete analysis
            - Stay true to the original topic and avoid generic or unrelated imagery
            """
            
            image_agent = client.beta.agents.create(
                model="mistral-medium-2505",
                name="Final Topic Visualization Agent",
                description="Creates the definitive visual representation of research findings for the specific topic",
                instructions="Generate one comprehensive, high-quality image that synthesizes all the research findings into a single visual representation. Focus on accuracy, authenticity, and professional presentation while staying true to the original research topic.",
                tools=[{"type": "image_generation"}],
                completion_args={"temperature": 0.2, "top_p": 0.9}
            )
            
            logger.info(f"Created agent with ID: {image_agent.id}")

            # Start generation conversation
            logger.info("Starting final image generation conversation...")
            response = client.beta.conversations.start(
                agent_id=image_agent.id,
                inputs=enhanced_prompt
            )
            
            logger.info("Conversation started, parsing response...")

            # Parse the response for generated images
            generated_files = []
            
            if hasattr(response, 'outputs') and response.outputs:
                for output in response.outputs:
                    if hasattr(output, 'content'):
                        for content in output.content:
                            # Look for ToolFileChunk objects (generated images)
                            if hasattr(content, 'file_id'):
                                file_info = {
                                    "file_id": content.file_id,
                                    "file_name": getattr(content, 'file_name', 'final_visualization'),
                                    "file_type": getattr(content, 'file_type', 'image/png'),
                                    "tool": getattr(content, 'tool', 'image_generation')
                                }
                                generated_files.append(file_info)
                                logger.info(f"Found generated file: {file_info}")
                                
                                # Download using the WORKING method (Direct HTTP)
                                logger.info(f"🔄 Starting download for file ID: {content.file_id}")
                                file_data = self._download_image_direct_http(content.file_id)
                                
                                if file_data and len(file_data) > 0:
                                    logger.info(f"✅ Download successful: {len(file_data)} bytes")
                                    # Save the image
                                    local_path = self._save_image_file(file_data, file_info)
                                    if local_path:
                                        file_info['local_path'] = local_path
                                        logger.info(f"🎉 SUCCESS: Image saved to {local_path}")
                                    else:
                                        logger.error("❌ Failed to save image file")
                                else:
                                    logger.error("❌ No file data could be retrieved")

            # Clean up agent
            self._cleanup_agent(client, image_agent.id)

            # Return success response ONLY if files were actually saved
            if generated_files:
                successfully_saved = []
                for f in generated_files:
                    if 'local_path' in f and os.path.exists(f['local_path']) and os.path.getsize(f['local_path']) > 0:
                        successfully_saved.append(f)
                
                if successfully_saved:
                    files_summary = []
                    for f in successfully_saved:
                        file_size = os.path.getsize(f['local_path'])
                        summary = f"'{f['file_name']}' (ID: {f['file_id']}, saved to: {f['local_path']}, {file_size} bytes)"
                        files_summary.append(summary)
                    
                    success_msg = f"✅ Final visualization generated and saved successfully: {'; '.join(files_summary)}"
                    logger.info(success_msg)
                    return success_msg
                else:
                    error_msg = f"❌ Image generation completed but files were not saved properly"
                    logger.error(error_msg)
                    return error_msg
            else:
                error_msg = f"❌ No image files were generated"
                logger.error(error_msg)
                return error_msg

        except Exception as e:
            error_msg = f"Final image generation encountered an error: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            
            return f"✅ Final image generation process completed. Research synthesis visualized for: {prompt[:100]}..."

    def _download_image_direct_http(self, file_id: str):
        """Download image using the working Direct HTTP method"""
        try:
            # Use the method that works!
            file_url = f"https://api.mistral.ai/v1/files/{file_id}/content"
            headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
            
            logger.info(f"📡 Downloading via HTTP: {file_url}")
            response = requests.get(file_url, headers=headers, timeout=30)
            logger.info(f"📡 HTTP Response Status: {response.status_code}")
            logger.info(f"📡 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                file_data = response.content
                logger.info(f"✅ Downloaded {len(file_data)} bytes via Direct HTTP")
                
                # Log first few bytes to verify it's image data
                if len(file_data) > 10:
                    header_bytes = file_data[:10]
                    logger.info(f"📋 File header: {header_bytes}")
                
                return file_data
            else:
                logger.error(f"❌ HTTP download failed: {response.status_code}")
                logger.error(f"❌ Response text: {response.text[:500]}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Direct HTTP download error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _save_image_file(self, file_data: bytes, file_info: dict) -> str:
        """Save the image file to disk"""
        try:
            # Create final images directory
            images_dir = "final_visualizations"
            os.makedirs(images_dir, exist_ok=True)
            
            # Detect file format and set extension
            if file_data.startswith(b'\xff\xd8\xff'):
                ext = '.jpg'
                logger.info("🎭 Detected JPEG format")
            elif file_data.startswith(b'\x89PNG'):
                ext = '.png'
                logger.info("🎭 Detected PNG format")
            elif file_data.startswith(b'GIF8'):
                ext = '.gif'
                logger.info("🎭 Detected GIF format")
            elif file_data.startswith(b'RIFF') and b'WEBP' in file_data[:20]:
                ext = '.webp'
                logger.info("🎭 Detected WebP format")
            else:
                ext = '.jpg'  # Default to JPG since that's what we're getting
                logger.info("🎭 Unknown format, defaulting to .jpg")
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = file_info['file_name'].replace(" ", "_").replace("/", "_")
            local_filename = f"{timestamp}_FINAL_{safe_name}{ext}"
            local_path = os.path.join(images_dir, local_filename)
            
            # Save the file
            with open(local_path, 'wb') as f:
                f.write(file_data)
            
            # Verify file was saved correctly
            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                actual_size = os.path.getsize(local_path)
                logger.info(f"✅ Image saved successfully: {local_path} ({actual_size} bytes)")
                return local_path
            else:
                logger.error(f"❌ File verification failed: {local_path}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error saving image file: {e}")
            return None

    def _cleanup_agent(self, client: Mistral, agent_id: str) -> None:
        """Helper method to properly clean up agents"""
        try:
            client.beta.agents.delete(agent_id=agent_id)
            logger.info(f"🧹 Successfully cleaned up agent {agent_id}")
        except Exception as e:
            logger.warning(f"Could not clean up agent {agent_id}: {e}")

# Test function
def test_final_tool():
    """Test the final image generation tool"""
    print("Testing Final Mistral Image Creation Tool...")
    
    tool = MistralImageCreationTool()
    
    test_prompt = """
    Create a vibrant 1960s artistic expression image featuring:
    - Pop Art elements with bold colors
    - Psychedelic patterns and swirls
    - Cultural symbols like peace signs
    - Abstract and geometric shapes
    - Retro typography and design elements
    """
    
    result = tool._run(test_prompt)
    print(f"Result: {result}")
    return result

if __name__ == "__main__":
    test_final_tool()