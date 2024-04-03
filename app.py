import getpass
import os
import subprocess
import shlex
from openai import OpenAI

client = OpenAI()

# Set up the OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"

# Get the task from the user
task = input("Please enter a task: ")

# Invoke the chat model
response = client.chat.completions.create(model="gpt-3.5-turbo",
messages=[
      {"role": "system", "content": f'suggest a tool for arch linux {task}'},
  ])

# Extract the suggested tools from the result
tools = [tool.strip() for tool in response.choices[0].message.content.split(',')]

# Show the suggested tools to the user and ask them to select one
print("The suggested tools are:")
for i, tool in enumerate(tools, start=1):
    print(f"{i}. {tool}")
tool_index = int(input("Please select a tool to install (enter the number): ")) - 1

# Get the selected tool
tool_name = tools[tool_index]

# Escape special characters in the tool name
tool_name = shlex.quote(tool_name)

# Ask the user if they want to install the selected tool
install = input(f"Do you want to install {tool_name}? (yes/no): ")

if install.lower() == 'yes':
    # Ask for the user's password
    password = getpass.getpass()

    # Define the command to install the tool
    command = f"echo {password} | sudo -S pacman -Sy {tool_name}"

    # Run the command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
else:
    print("Installation cancelled.")