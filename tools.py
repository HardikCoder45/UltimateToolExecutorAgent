import subprocess
import os
import psutil
import webbrowser
import time
from pydantic import BaseModel, Field
from crewai import LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type,Optional
from crewai_tools import SerperDevTool
from openai import OpenAI
from image_processor import add_grid_to_image
import pyautogui

OPENROUTER_API_KEY=os.getenv('OPENROUTER_API_KEY')

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

 
llm = LLM(
    model="openrouter/meta-llama/llama-3.3-70b-instruct",
    temperature=0.7,
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

 
# Enhanced Search Tools with proper configuration
search_tool = SerperDevTool(
    search_url="https://google.serper.dev/search",
    description="Search the web for general information and websites",
    api_key=os.getenv("SERPER_API_KEY")
)

search_images_tool = SerperDevTool(
    search_url="https://google.serper.dev/images",
    description="Search for images across the web",
    api_key=os.getenv("SERPER_API_KEY")
)

news_search_tool = SerperDevTool(
    search_url="https://google.serper.dev/news",
    description="Search for current news articles and headlines",
    api_key=os.getenv("SERPER_API_KEY")
)

web_search_tool = SerperDevTool(
    search_url="https://scrape.serper.dev",
    description="Scrape website content for detailed information",
    api_key=os.getenv("SERPER_API_KEY")
)

class FileSchema(BaseModel):
    name: str = Field(description="The name of the file")
    content: str = Field(description="The content to write to the file")

class FileMakerTool(BaseTool):
    name: str = "fileMaker"
    description: str = "Create a file and add content to it"
    args_schema: Type[BaseModel] = FileSchema

    def _run(self, name: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname('./test/'+name), exist_ok=True)
            with open("./test/"+name, 'w', encoding='utf-8') as file:
                file.write(content)
            return f"File '{name}' created successfully with the provided content."
        except Exception as e:
            return f"Error creating file: {str(e)}"

# Command Execution Tool
class CommandSchema(BaseModel):
    command: str = Field(description="The command to execute")

class CommandTool(BaseTool):
    name: str = "commandRunner"
    description: str = "Execute system commands"
    args_schema: Type[BaseModel] = CommandSchema

    def _run(self, command: str) -> str:
        
            working_dir = r"C:/Users/inno/Desktop/Hardik_coder_all_files/CodingAgenticAi/test"
        
            os.chdir(working_dir)
            try:
                # Run the command in a new cmd.exe process
                result = subprocess.run(
                    f'cmd.exe /c {command}',
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=working_dir
                )
                
                # Return the output or error message
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Command failed with code {result.returncode}: {result.stderr}"
            except Exception as e:
                return f"Error executing command: {str(e)}"

# Process Management Tool
class ProcessSchema(BaseModel):
    process_name: str = Field(description="Name of the process to manage")

class ProcessTool(BaseTool):
    name: str = "processManager"
    description: str = "Start, stop, or check running processes"
    args_schema: Type[BaseModel] = ProcessSchema

    def _run(self, process_name: str, action: str = "check") -> str:
        try:
            
            if action == "start":
                subprocess.Popen(process_name)
                return f"Started process: {process_name}"
            elif action == "stop":
                for proc in psutil.process_iter():
                    if proc.name() == process_name:
                        proc.kill()
                        return f"Stopped process: {process_name}"
                return f"Process not found: {process_name}"
            else:
                running = [p.name() for p in psutil.process_iter()]
                return f"Running processes: {', '.join(running)}"
        except Exception as e:
            return f"Error managing process: {str(e)}"

# Web Browser Tool
class BrowserSchema(BaseModel):
    url: str = Field(description="The URL to open in browser")

class BrowserTool(BaseTool):
    name: str = "webBrowser"
    description: str = "Open URLs in web browser"
    args_schema: Type[BaseModel] = BrowserSchema

    def _run(self, url: str) -> str:
        try:
            webbrowser.open(url)
            return f"Opened URL: {url}"
        except Exception as e:
            return f"Error opening browser: {str(e)}"

# System Information Tool
class SystemInfoTool(BaseTool):
    name: str = "systemInfo"
    description: str = "Get system information and status"

    def _run(self) -> str:
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            uptime = time.time() - psutil.boot_time()
            return f"System Status:\nCPU: {cpu}%\nMemory: {memory}%\nDisk: {disk}%\nUptime: {uptime//3600} hours"
        except Exception as e:
            return f"Error getting system info: {str(e)}"

# File Search Tool
class SearchSchema(BaseModel):
    pattern: str = Field(description="The file pattern to search for")

class FileSearchTool(BaseTool):
    name: str = "fileSearch"
    description: str = "Search for files in the system"
    args_schema: Type[BaseModel] = SearchSchema

    def _run(self, pattern: str) -> str:
        try:
            matches = []
            for root, dirs, files in os.walk('.'):
                for name in files:
                    if pattern in name:
                        matches.append(os.path.join(root, name))
            return f"Found files: {', '.join(matches)}" if matches else "No files found"
        except Exception as e:
            return f"Error searching files: {str(e)}"

# Keyboard Control Tool
class KeyboardSchema(BaseModel):
    text: str = Field(description="The text to type")

class KeyboardTool(BaseTool):
    name: str = "keyboardControl"
    description: str = "Control keyboard to type text anywhere"
    args_schema: Type[BaseModel] = KeyboardSchema

    def _run(self, text: str) -> str:
        try:
            import pyautogui
            pyautogui.write(text)
            return f"Typed text: {text}"
        except Exception as e:
            return f"Error controlling keyboard: {str(e)}"

# Mouse Control Tool
class MouseSchema(BaseModel):
    action: str = Field(description="Mouse action to perform (move, click, scroll)")
    x: Optional[int] = Field(description="X coordinate for move/click")
    y: Optional[int] = Field(description="Y coordinate for move/click")
    direction: Optional[str] = Field(description="Scroll direction (up/down)")

class MouseTool(BaseTool):
    name: str = "mouseControl"
    description: str = "Control mouse movements and clicks"
    args_schema: Type[BaseModel] = MouseSchema

    def _run(self, action: str, x: Optional[int] = None, y: Optional[int] = None, direction: Optional[str] = None) -> str:
        try:
            import pyautogui
            if action == "move":
                pyautogui.moveTo(x, y)
                return f"Moved mouse to ({x}, {y})"
            elif action == "click":
                pyautogui.click(x, y)
                return f"Clicked at ({x}, {y})"
            elif action == "scroll":
                pyautogui.scroll(120 if direction == "up" else -120)
                return f"Scrolled {direction}"
            return "Invalid mouse action"
        except Exception as e:
            return f"Error controlling mouse: {str(e)}"

# Application Control Tool
class AppSchema(BaseModel):
    app_name: str = Field(description="Name of application to open/control")

class AppControlTool(BaseTool):
    name: str = "appControl"
    description: str = "Open and control applications"
    args_schema: Type[BaseModel] = AppSchema

    def _run(self, app_name: str) -> str:
        try:
            import os
            os.startfile(app_name)
            return f"Opened application: {app_name}"
        except Exception as e:
            return f"Error opening application: {str(e)}"
 

# Browser Navigation Tool
class BrowserNavSchema(BaseModel):
    query: str = Field(description="Search query to navigate")

class BrowserNavTool(BaseTool):
    name: str = "browserNavigation"
    description: str = "Search and navigate in browser"
    args_schema: Type[BaseModel] = BrowserNavSchema

    def _run(self, query: str) -> str:
        try:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Navigated to search results for: {query}"
        except Exception as e:
            return f"Error navigating browser: {str(e)}"

class VisionSchema(BaseModel):
    action:str =Field(description="Here you have to add the all actions you want to do related to this image, describe and give any type of action to do")

vision_prompt=""                     """This image shows the current display of the computer. Please respond in the following format:\n"
                        "The objective is: [put the objective here]\n"
                        "On the screen, I see: [an extensive list of everything that might be relevant to the objective including windows, icons, menus, apps, and UI elements]\n"
                        "This means the objective is: [complete|not complete]\n\n"
                        "(Only continue if the objective is not complete.)\n"
                        "The next step is to [click|type|run the shell command] [put the next single step here] in order to [put what you expect to happen here].",
                          """
class VisionTool(BaseTool):
    name: str = "VisionTool"
    description: str = "It will help you in the case of the image processing you can be able to perform acccurate actions with this , just you have to tell the image url and path and it will give out you the all details of the image and where and when to take action"
    args_schema:Type[BaseModel] = VisionSchema
    
    def _run(self,action:str) -> str:
        try:
               
   
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')
            filename = f"../screenshots/screenshot.png"
            pyautogui.screenshot(filename)
            grid_image = add_grid_to_image(image_path=filename)
             
            response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"""
                             {vision_prompt}
                                 
                                 Tell Me what To do in the computer, for these actions:{action}  and also describe the image you recieved in th e 
                                 very detail , tell me where to move the mouse with the x and y  coordinates"""},
                                {"type": "image_url", "image_url": {"url": grid_image}}
                            ]
                        }
                    ],
                    max_tokens=6900
                )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
 