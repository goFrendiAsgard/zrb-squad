# Zrb Squad

A proof-of-concept extension for the zrb project to create multi-agent workflows.

## Overview

Zrb Squad allows you to define a squad of AI agents that run in parallel tmux panels, each with their own chat interface.

## Installation

This is a prototype extension. To use it:

1. Clone this repository
2. Ensure you have zrb installed
3. The `zrb_init.py` will be automatically loaded by zrb

## Usage

### Basic Example

```python
from zrb import Group, LLMChatTask, StrInput
from zrb_squad import define_squad, Member

# Create a group for your squad
squad_group = Group("my-squad", description="My agent squad")

# Create chat tasks for different roles
coder = LLMChatTask(
    name="coder",
    description="👨‍💻 Coder assistant",
    input=[StrInput("message", "Message")],
    message="{ctx.input.message}",
    ui_assistant_name="Coder Assistant",
)

tester = LLMChatTask(
    name="tester", 
    description="🧪 Tester assistant",
    input=[StrInput("message", "Message")],
    message="{ctx.input.message}",
    ui_assistant_name="Tester Assistant",
)

# Create squad members
members = [
    Member(name="coder", chat_task=coder),
    Member(name="tester", chat_task=tester),
]

# Define the squad
define_squad(
    squad_name="dev-team",
    members=members,
    group_description="My agent squad
)

```

### Running the Squad

Once defined, you can run your squad with:

```bash
zrb my-squad start
```

This will:
1. Create a new tmux session
2. Split it into multiple panes (one for each squad member)
3. Start each member's chat task in its own pane
4. Attach to the tmux session

## How It Works

The implementation:
1. Creates a unique tmux session name based on the squad name
2. Kills any existing session with the same name
3. Creates a new tmux session with the first member's chat task
4. Splits the window horizontally for each additional member
5. Sets pane titles to member names
6. Tiles the layout for equal pane sizes
7. Attaches to the session

## Example in zrb_init.py

See `zrb_init.py` for a complete working example with three agents:
- Coder Assistant
- Tester Assistant  
- Documentation Assistant

## Requirements

- Python 3.12+
- zrb 2.0+
- tmux 3.0+

## Limitations

- This is a prototype/POC
- Currently only supports horizontal splits
- All panes are created in a single window
- Error handling is basic