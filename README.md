# Zrb Squad

A proof-of-concept extension for the zrb project to create multi-agent workflows.

## Overview

Zrb Squad allows you to define a squad of AI agents that run in parallel tmux panels, each with their own chat interface. It also includes a kanban board system (`AnyBoard`) for task coordination between squad members, with built-in tools and triggers for agent interaction.

## Installation

This is a prototype extension. To use it:

1. Clone this repository
2. Ensure you have zrb installed
3. The `zrb_init.py` will be automatically loaded by zrb

## Usage

### Using the Squad Class (Recommended)

```python
from zrb import Group, LLMChatTask, StrInput
from zrb_squad import Squad, Member

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

# Create and serve the squad
squad = Squad(
    name="dev-team",
    members=members,
    group_description="My agent squad"
)
squad.serve()
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

### Using the Kanban Board System

The `AnyBoard` system provides task coordination between squad members. The board is now organized as a Python package (`zrb_squad.board`) with the following structure:

```
zrb_squad/board/
├── __init__.py          # Package exports
├── story.py             # Story class
├── any_board.py         # Abstract base class
├── file_board.py        # File-based implementation
└── factory.py           # Factory functions
```

#### Basic Board Usage

```python
from zrb_squad import create_board, Story

# Create a shared board for the squad
board = create_board("squad_tasks.json")

# Assign tasks to squad members
task1 = board.assign("alice", "bob", "API Endpoint", "Create new REST API endpoint")
task2 = board.assign("alice", "charlie", "UI Component", "Build responsive component")

# Check assigned tasks
bob_tasks = board.get_by_assignee("bob")
charlie_tasks = board.get_by_assignee("charlie")

# Complete a task
board.complete(task1.task_id, "bob")

# Get pending tasks
pending_tasks = board.get_pending_by_assignee("charlie")

# Get all tasks assigned by someone
alice_assignments = board.get_by_assigner("alice")
```

#### Agent Tools and Triggers

The board system now includes methods to create tools and triggers for agents:

```python
# Create tools for an agent
agent_tools = board.create_tools("bob")
# Returns: [
#   {"name": "assign_task_to_agent", ...},  # Assign task to other agent
#   {"name": "list_my_tasks", ...},         # List tasks assigned to Bob
#   {"name": "complete_my_task", ...}       # Complete a task assigned to Bob
# ]

# Create triggers for an agent
agent_triggers = board.create_triggers("alice")
# Returns: [
#   lambda: board._trigger_new_task_for_me("alice"),      # Check for new tasks assigned to Alice
#   lambda: board._trigger_task_completed_by_me("alice")  # Check for tasks completed by Alice (as assigner)
# ]

# Use a tool (example)
assign_tool = agent_tools[0]
result = assign_tool['function']("charlie", "Test task", "This is a test task")
# Result: {"success": True, "message": "Task assigned to charlie", ...}

# Check triggers (example)
for trigger in agent_triggers:
    result = trigger()
    # Result: {"has_new_tasks": True, "message": "You have 1 pending task(s)", ...}
```

## Package Structure

The zrb_squad module is organized as follows:

```
zrb_squad/
├── __init__.py          # Main module exports
├── squad.py             # Squad and Member classes
└── board/               # Kanban board package
    ├── __init__.py      # Board package exports
    ├── story.py         # Story class
    ├── any_board.py     # Abstract base class with tools and triggers
    ├── file_board.py    # File-based implementation
    └── factory.py       # Factory functions
```

## API Reference

### `Squad` Class

The main class for creating and managing squads:

```python
class Squad:
    def __init__(
        self,
        name: str,
        members: list[Member],
        group_name: str | None = None,
        group_description: str | None = None,
    ):
        """
        Initialize a new squad.
        
        Args:
            name: Name of the squad
            members: List of Member objects, each with a name and chat_task
            group_name: Optional name for the group (defaults to kebab-case of squad name)
            group_description: Optional description for the group
        """
    
    def serve(self) -> AnyTask:
        """
        Create and register the squad task.
        
        Returns:
            The created squad task
        """
    
    @property
    def task(self) -> Optional[AnyTask]:
        """Get the squad task (only available after serve() is called)."""
```

### `Member` Class

```python
class Member:
    def __init__(self, name: str, chat_task: LLMChatTask):
        """
        Represents a member in a squad.
        
        Args:
            name: Name of the member (displayed in tmux pane title)
            chat_task: The LLMChatTask instance for this member
        """
```

### `AnyBoard` Abstract Base Class

The abstract base class for kanban board implementations:

```python
class AnyBoard(ABC):
    @abstractmethod
    def assign(self, assigner: str, assignee: str, task_name: str, description: str) -> Story:
        """Assign a new task to a squad member."""
    
    @abstractmethod
    def get_by_assignee(self, assignee: str) -> List[Story]:
        """Get all tasks assigned to a specific squad member."""
    
    @abstractmethod
    def get_by_assigner(self, assigner: str) -> List[Story]:
        """Get all tasks assigned by a specific squad member."""
    
    @abstractmethod
    def complete(self, task_id: str, assignee: str) -> bool:
        """Mark a task as completed."""
    
    @abstractmethod
    def get_all(self) -> List[Story]:
        """Get all tasks in the board."""
    
    @abstractmethod
    def get_pending_by_assignee(self, assignee: str) -> List[Story]:
        """Get pending (incomplete) tasks assigned to a specific squad member."""
    
    @abstractmethod
    def get_completed_by_assignee(self, assignee: str) -> List[Story]:
        """Get completed tasks assigned to a specific squad member."""
    
    def create_tools(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        Create a list of tools for an agent to interact with the board.
        
        Args:
            agent_name: The name of the agent that will use these tools
        
        Returns:
            List of tool definitions that can be used by the agent
        """
    
    def create_triggers(self, agent_name: str) -> List[Callable]:
        """
        Create triggers that activate when certain board events occur.
        
        Args:
            agent_name: The name of the agent that will use these triggers
        
        Returns:
            List of trigger functions that can be registered
        """
```

### `FileBoard` Class

File-based implementation with race condition protection:

```python
class FileBoard(AnyBoard):
    def __init__(self, file_path: str = "zrb_squad_board.json"):
        """
        Initialize the file-based board.
        
        Args:
            file_path: Path to the JSON file for storage
        """
    
    # Implements all AnyBoard abstract methods
    # Uses file locking (fcntl) to prevent race conditions
```

### `Story` Class

Represents a single task in the kanban board:

```python
class Story:
    def __init__(
        self,
        assignee: str,
        assigner: str,
        description: str,
        task_id: Optional[str] = None,
        is_completed: bool = False,
        created_at: Optional[float] = None,
        completed_at: Optional[float] = None
    ):
        """
        A single task/story in the kanban board.
        
        Attributes:
            task_id: Unique identifier for the task
            assignee: Who the task is assigned to
            assigner: Who assigned the task
            description: Description of the task
            is_completed: Whether the task is completed
            created_at: When the task was created (timestamp)
            completed_at: When the task was completed (timestamp, None if not completed)
        """
    
    def complete(self) -> None:
        """Mark the story as completed."""
    
    def to_dict(self) -> dict:
        """Convert the story to a dictionary for serialization."""
    
    @classmethod
    def from_dict(cls, data: dict) -> "Story":
        """Create a Story instance from a dictionary."""
```

### Convenience Functions

```python
def create_board(file_path: str = "zrb_squad_board.json") -> AnyBoard:
    """Create a default file-based board."""

def define_squad(
    squad_name: str,
    members: list[Member],
    group_name: str | None = None,
    group_description: str | None = None,
) -> AnyTask:
    """
    Define a squad of AI agents that run in parallel tmux panels.
    
    This is a backward compatibility function. For new code, use the Squad class.
    """
```

## How It Works

### Squad Implementation
1. Creates a unique tmux session name based on the squad name
2. Kills any existing session with the same name
3. Creates a new tmux session with the first member's chat task
4. Splits the window horizontally for each additional member
5. Sets pane titles to member names
6. Tiles the layout for equal pane sizes
7. Attaches to the session

### Board Implementation
1. Uses JSON file storage for simplicity
2. Implements file locking (`fcntl`) to prevent race conditions
3. Handles corrupted files gracefully
4. Provides atomic write operations with temporary files
5. Supports multiple concurrent processes accessing the same board

## Example in zrb_init.py

See `zrb_init.py` for a complete working example with three agents:
- Coder Assistant
- Tester Assistant  
- Documentation Assistant

## Creating Custom Board Implementations

You can create custom implementations by extending `AnyBoard`:

```python
from zrb_squad import AnyBoard, Story
from typing import List
import sqlite3

class SQLiteBoard(AnyBoard):
    def __init__(self, db_path: str = "squad_board.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        # Initialize database schema
        pass
    
    def assign(self, assigner: str, assignee: str, task_name: str, description: str) -> Story:
        # Implement assignment logic
        pass
    
    # Implement all other abstract methods...
```

## Requirements

- Python 3.12+
- zrb 2.0+
- tmux 3.0+

## Race Condition Protection

The `FileBoard` implementation uses `fcntl` file locking to prevent race conditions when multiple processes access the same board file. This ensures that:
- Concurrent reads are safe
- Concurrent writes are serialized
- File corruption is prevented
- Multiple squad members can access the board simultaneously

## Limitations

- This is a prototype/POC
- Currently only supports horizontal splits for tmux
- All panes are created in a single window
- Error handling is basic
- FileBoard requires `fcntl` (available on Unix-like systems)