"""
Story class representing a single task in the kanban board.
"""
import time
import uuid
from datetime import datetime
from typing import Optional


class Story:
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
        self.task_id = task_id or str(uuid.uuid4())
        self.assignee = assignee
        self.assigner = assigner
        self.description = description
        self.is_completed = is_completed
        self.created_at = created_at or time.time()
        self.completed_at = completed_at
        
    def complete(self) -> None:
        """Mark the story as completed."""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = time.time()
    
    def to_dict(self) -> dict:
        """Convert the story to a dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "assignee": self.assignee,
            "assigner": self.assigner,
            "description": self.description,
            "is_completed": self.is_completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Story":
        """Create a Story instance from a dictionary."""
        return cls(
            task_id=data["task_id"],
            assignee=data["assignee"],
            assigner=data["assigner"],
            description=data["description"],
            is_completed=data["is_completed"],
            created_at=data["created_at"],
            completed_at=data.get("completed_at")
        )
    
    def __repr__(self) -> str:
        status = "✓" if self.is_completed else "○"
        created = datetime.fromtimestamp(self.created_at).strftime("%Y-%m-%d %H:%M")
        if self.is_completed and self.completed_at:
            completed = datetime.fromtimestamp(self.completed_at).strftime("%Y-%m-%d %H:%M")
            return f"Story({self.task_id[:8]}... {status} '{self.description[:30]}...' → {self.assignee} by {self.assigner} | Created: {created} | Completed: {completed})"
        return f"Story({self.task_id[:8]}... {status} '{self.description[:30]}...' → {self.assignee} by {self.assigner} | Created: {created})"