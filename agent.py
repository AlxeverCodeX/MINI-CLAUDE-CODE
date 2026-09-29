import json
import os
import subprocess

from openai import OpenAI

# Load .env if python-dotenv is installed (optional, no hard dependency)
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ImportError:
    pass

client = OpenAI(
    api_key=os.getenv("CLEANAPIS_API_KEY"),
    base_url=os.getenv("CLEANAPIS_BASE_URL", "https://cleanapis.com/v1"),
)
MODEL = os.getenv("MODEL", "claude-opus-4.8")

if not client.api_key:
    print(
        "Warning: CLEANAPIS_API_KEY is not set. "
        "Set it in your environment or in a .env file. "
        "See .env.example"
    )

SYSTEM_PROMPT = """You are a coding agent running in the user's terinal.You can lsit files,read files, write files,  and run shell commands
Use your tools to complete the user's task, then briefly summarize what you did.
The working directory is the folder the user launched you from."""

def list_files(path="."):
    entries = []
    for entry in os.scandir(path):
        entries.append(entry.name + ("/" if entry.is_dir() else ""))
    return "\n".join(sorted(entries)) or "(empty directory)"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved {path} ({len(content)} characters)"

def run_command(command):
    answer = input(f" Run '{command}' ? [y/n]")
    if answer.strip().lower() != "y":
        return "The user declined to run this command."
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=120
    )
    output = (result.stdout + result.stderr).strip()
    return output or f"(no output, exit code {result.returncode})"

TOOLS = {
    "list_files": list_files,
    "read_file" : read_file,
    "write_file" : write_file,
    "run_command" : run_command,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function":{
            "name": "read_file",
            "description": "Read a text file and return its contentes.",
            "parameters": {
                "type": "object",
                "properties":{
                    "path": {"type": "string", "description": "path of the file to read"},

                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the files in a directory. Folders end with /.",
            "parameters": {
                "type": "object",
                "properties":{
                    "path": {"type": "string", "description": "Directory to list, e.g. '."},

                },
                "required": ["path"],
            },

        },

    },
    {
     "type": "function",
            "function": {
                "name": "write_file",
                "description": "Create or overwrite a text file with the given content.",
                "parameters": {
                    "type": "object",
                    "properties":{
                        "path": {"type": "string", "description": "Path of the file to write"},
                        "content": {"type": "string", "description": "Full contents of the file"},
                    },
                    "required": ["path", "content"],
                },
    
            },
    
    },
    {
         "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Run a shell command and return its output.The user approves it first",
                    "parameters": {
                        "type": "object",
                        "properties":{
                            "command": {"type": "string", "description": "The shell command to run"},
                        },
                        "required": ["command"],
                    },
        
                },
        
        },
]

def run_tool(tool_call):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    print(f" tool: {name} ({args})")
    try:
        return str(TOOLS[name](**args))
    except Exception as error:
        return f"Error: {error}"


def run_agent(messages):
    while True:
        response = client.chat.completions.create(
            model = MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )
        message = response.choices[0].message
        messages.append(message)

        #No tool calls means the model is done and answered in plain text
        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            result = run_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            } )



def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Mini agent ready.Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            break
        messages.append({"role": "user", "content": user_input})
        reply = run_agent(messages)
        print(f"\nAgent: {reply}")

if __name__ == '__main__':
    main()
