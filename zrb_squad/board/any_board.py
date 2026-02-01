"""
Abstract base class for a kanban board.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List

from .story import Story


class AnyBoard(ABC):
    """
    Abstract base class for a kanban board.

    This provides a common interface for different board implementations
    (file-based, database-based, etc.).
    """

    @abstractmethod
    def set_valid_members(self, members: list[str]) -> None:
        """Set the list of valid member names for validation."""
        pass

    @abstractmethod
    def assign(
        self, assigner: str, assignee: str, task_name: str, description: str
    ) -> Story:
        """
        Assign a new task to a squad member.

        Args:
            assigner: Who is assigning the task
            assignee: Who the task is assigned to
            task_name: Name/identifier for the task
            description: Detailed description of the task

        Returns:
            The created Story object
        """
        pass

    @abstractmethod
    def get_by_assignee(self, assignee: str) -> List[Story]:
        """
        Get all tasks assigned to a specific squad member.

        Args:
            assignee: The squad member to get tasks for

        Returns:
            List of Story objects assigned to the member
        """
        pass

    @abstractmethod
    def get_by_assigner(self, assigner: str) -> List[Story]:
        """
        Get all tasks assigned by a specific squad member.

        Args:
            assigner: The squad member who assigned the tasks

        Returns:
            List of Story objects assigned by the member
        """
        pass

    @abstractmethod
    def complete(self, task_id: str, assignee: str) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: The ID of the task to complete
            assignee: The assignee (for verification)

        Returns:
            True if the task was successfully completed, False otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Story]:
        """
        Get all tasks in the board.

        Returns:
            List of all Story objects
        """
        pass

    @abstractmethod
    def get_pending_by_assignee(self, assignee: str) -> List[Story]:
        """
        Get pending (incomplete) tasks assigned to a specific squad member.

        Args:
            assignee: The squad member to get pending tasks for

        Returns:
            List of pending Story objects assigned to the member
        """
        pass

    @abstractmethod
    def get_completed_by_assignee(self, assignee: str) -> List[Story]:
        """
        Get completed tasks assigned to a specific squad member.

        Args:
            assignee: The squad member to get completed tasks for

        Returns:
            List of completed Story objects assigned to the member
        """
        pass

    @abstractmethod
    def create_tools(self, agent_name: str) -> List[callable]:
        """
        Create a list of tools for an agent to interact with the board.

        Args:
            agent_name: The name of the agent that will use these tools

        Returns:
            List of tool functions that can be added to an LLMChatTask
        """
        pass

    @abstractmethod
    def create_triggers(self, agent_name: str) -> List[Callable]:
        """
        Create triggers that check for board events relevant to the agent.

        Args:
            agent_name: The name of the agent that will use these triggers

        Returns:
            List of trigger functions that can be added to an LLMChatTask
        """
        pass
