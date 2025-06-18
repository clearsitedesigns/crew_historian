import os
import sys
import requests
from dotenv import load_dotenv
from mistralai import Mistral
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_and_save_image(client: Mistral, file_id: str, file_name: str) -> str:
    """Download and save the generated image"""
    try:
        print(f"Downloading image: {file_name} (ID: {file_id})")
        
        # Get the file content from Mistral
        file_response = client.files.retrieve(file_id=file_id)
        
        # Handle different response types
        file_data = None
        
        # Check if it has model_dump method (Pydantic model)
        if hasattr(file_response, 'model_dump'):
            response_dict = file_response.model_dump()
            print(f"Response dict keys: {response_dict.keys()}")
            
            # Look for the bytes data in the response
            if 'bytes' in response_dict and response_dict['bytes']:
                file_data = response_dict['bytes']
                # If it's a string representation, we need to decode it
                if isinstance(file_data, str):
                    import base64
                    try:
                        file_data = base64.b64decode(file_data)
                    except:
                        print("Could not decode base64 data")
                        file_data = None
        
        # If no bytes found, try different methods
        if file_data is None:
            print("No bytes found in response, trying alternative methods...")
            
            # Try to access bytes attribute directly
            if hasattr(file_response, 'bytes'):
                file_data = file_response.bytes
                if isinstance(file_data, str):
                    import base64
                    try:
                        file_data = base64.b64decode(file_data)
                    except:
                        pass
            
            # If still no data, try direct API call
            if file_data is None:
                print("Attempting direct file download via HTTP...")
                import requests
                
                # Get API key from environment
                api_key = os.getenv("MISTRAL_API_KEY")
                if not api_key:
                    raise Exception("API key not found in environment")
                
                # Try the content endpoint
                file_url = f"https://api.mistral.ai/v1/files/{file_id}/content"
                headers = {"Authorization": f"Bearer {api_key}"}
                
                response = requests.get(file_url, headers=headers)
                print(f"HTTP response status: {response.status_code}")
                
                if response.status_code == 200:
                    file_data = response.content
                    print(f"Downloaded {len(file_data)} bytes via HTTP")
                else:
                    print(f"HTTP error: {response.text}")
                    raise Exception(f"HTTP request failed: {response.status_code}")
        
        if file_data is None or len(file_data) == 0:
            raise Exception("No file data could be retrieved")
        
        # Create images directory if it doesn't exist
        images_dir = "generated_images"
        os.makedirs(images_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = file_name.replace(" ", "_").replace("/", "_")
        local_filename = f"{timestamp}_{safe_name}.png"
        local_path = os.path.join(images_dir, local_filename)
        
        # Save the file
        with open(local_path, 'wb') as f:
            f.write(file_data)
        
        print(f"✅ Image saved to: {local_path}")
        print(f"📁 File size: {len(file_data)} bytes")
        return local_path
        
    except Exception as e:
        print(f"❌ Failed to download image {file_id}: {e}")
        print(f"Error type: {type(e)}")
        
        # Debug: Let's see what the actual response looks like
        try:
            file_response = client.files.retrieve(file_id=file_id)
            print(f"Debug - Response type: {type(file_response)}")
            if hasattr(file_response, 'model_dump'):
                response_dict = file_response.model_dump()
                print(f"Debug - Full response: {response_dict}")
        except:
            pass
            
        return None

def display_image_info(image_path: str):
    """Display information about the saved image"""
    try:
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"📁 File size: {file_size} bytes ({file_size/1024:.1f} KB)")
            print(f"📂 Full path: {os.path.abspath(image_path)}")
            
            # Try to get image dimensions if PIL is available
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    print(f"🖼️  Dimensions: {img.width}x{img.height} pixels")
                    print(f"🎨 Mode: {img.mode}")
            except ImportError:
                print("💡 Install Pillow to see image dimensions: pip install Pillow")
            except Exception as e:
                print(f"⚠️  Could not read image details: {e}")
                
        else:
            print(f"❌ Image file not found: {image_path}")
            
    except Exception as e:
        print(f"❌ Error checking image: {e}")

def test_complete_image_generation():
    """Test complete image generation with download and display"""
    
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    
    if not api_key:
        print("❌ MISTRAL_API_KEY not found")
        return False
    
    client = Mistral(api_key=api_key)
    
    print("=== Complete Image Generation Test ===")
    
    # Test prompt
    test_prompt = "Create a historical map of California showing mountains in brown, rivers in blue, and cities as red dots"
    
    try:
        print(f"🎯 Generating image with prompt: {test_prompt}")
        
        # Create image generation agent with the correct model
        print("Creating image generation agent...")
        image_agent = client.beta.agents.create(
            model="mistral-medium-2505",  # Using the correct model
            name="Historical Map Generator",
            description="Generates historical maps and geographical visualizations",
            instructions="Create detailed historical maps based on user descriptions. Use appropriate colors and symbols for geographical features.",
            tools=[{"type": "image_generation"}],
            completion_args={"temperature": 0.3, "top_p": 0.95}
        )
        
        print(f"✅ Created agent: {image_agent.id}")

        # Start conversation
        print("Starting image generation conversation...")
        response = client.beta.conversations.start(
            agent_id=image_agent.id,
            inputs=test_prompt
        )
        
        print("✅ Conversation started")

        # Parse response and download images
        generated_images = []
        
        if hasattr(response, 'outputs') and response.outputs:
            print(f"📋 Processing {len(response.outputs)} outputs...")
            
            for i, output in enumerate(response.outputs):
                print(f"Output {i}: {type(output)}")
                
                if hasattr(output, 'content'):
                    for j, content in enumerate(output.content):
                        print(f"  Content {j}: {type(content)}")
                        
                        # Check if this is a generated file
                        if hasattr(content, 'file_id'):
                            file_id = content.file_id
                            file_name = getattr(content, 'file_name', f'generated_image_{j}')
                            file_type = getattr(content, 'file_type', 'unknown')
                            
                            print(f"🎨 Found generated file:")
                            print(f"   📄 Name: {file_name}")
                            print(f"   🆔 ID: {file_id}")
                            print(f"   📂 Type: {file_type}")
                            
                            # Download the image
                            local_path = download_and_save_image(client, file_id, file_name)
                            if local_path:
                                generated_images.append(local_path)
                                display_image_info(local_path)
                        
                        # Also check for text content
                        elif hasattr(content, 'text'):
                            text_content = content.text
                            if text_content and len(text_content) > 50:
                                print(f"📝 Text content preview: {text_content[:100]}...")

        # Clean up agent
        try:
            client.beta.agents.delete(agent_id=image_agent.id)
            print("✅ Agent cleaned up")
        except Exception as cleanup_error:
            print(f"⚠️  Agent cleanup warning: {cleanup_error}")

        # Summary
        print(f"\n🎉 Generation complete!")
        print(f"📊 Generated {len(generated_images)} image(s)")
        
        if generated_images:
            print("\n📁 Generated files:")
            for img_path in generated_images:
                print(f"   • {img_path}")
            
            print(f"\n💡 To view your images:")
            print(f"   • Open the 'generated_images' folder")
            print(f"   • Or use an image viewer to open the files directly")
            
            # Try to open the first image if on macOS/Windows/Linux
            if generated_images:
                first_image = generated_images[0]
                print(f"\n🖼️  Attempting to open: {first_image}")
                
                try:
                    import subprocess
                    import platform
                    
                    system = platform.system()
                    if system == "Darwin":  # macOS
                        subprocess.run(["open", first_image])
                    elif system == "Windows":
                        subprocess.run(["start", first_image], shell=True)
                    elif system == "Linux":
                        subprocess.run(["xdg-open", first_image])
                    
                    print("✅ Image opened in default viewer")
                    
                except Exception as e:
                    print(f"💡 Couldn't auto-open image: {e}")
                    print(f"   Please manually open: {first_image}")
        
        return len(generated_images) > 0
        
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return False

def test_your_crewai_tool():
    """Test your actual CrewAI tool"""
    
    print("\n=== Testing Your CrewAI Tool ===")
    
    try:
        # Import your actual tool
        sys.path.append('src')
        from crew_historian.tools.mistral_image_creation_tool import MistralImageCreationTool
        
        tool = MistralImageCreationTool()
        
        test_prompt = "Generate a historical map showing the Great Wall of China with surrounding terrain"
        
        print(f"🧪 Testing tool with prompt: {test_prompt}")
        result = tool._run(test_prompt)
        
        print(f"🔄 Tool result: {result}")
        
        # Extract file IDs from the result if present
        if "file_id" in result:
            print("🎯 Tool generated images! Check the result above for file IDs.")
        
        return True
        
    except Exception as e:
        print(f"❌ CrewAI tool test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Mistral Image Generation Testing")
    print("=" * 50)
    
    # Test 1: Complete image generation with download
    success1 = test_complete_image_generation()
    
    # Test 2: Your CrewAI tool
    success2 = test_your_crewai_tool()
    
    print("\n" + "=" * 50)
    print("📊 FINAL SUMMARY:")
    print(f"   Complete generation test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"   CrewAI tool test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1:
        print(f"\n🎉 SUCCESS! Check the 'generated_images' folder for your files!")
    else:
        print(f"\n💡 If tests failed, check your API key and network connection.")