"""
File-based implementation of the kanban board.
"""

import fcntl  # For file locking to prevent race conditions
import json
import os
import time
from typing import Any, Callable, Dict, List

from zrb import to_infinite_stream

from .any_board import AnyBoard
from .story import Story


class FileBoard(AnyBoard):
    """
    File-based implementation of the kanban board.

    Uses a JSON file for storage with file locking to prevent race conditions
    when accessed by multiple processes.
    """

    def __init__(self, file_path: str = "zrb_squad_board.json"):
        """
        Initialize the file-based board.

        Args:
            file_path: Path to the JSON file for storage
        """
        self.file_path = os.path.expanduser(file_path)
        self._valid_members: list[str] = []
        self._ensure_file_exists()

    def set_valid_members(self, members: list[str]) -> None:
        """Set the list of valid member names for validation."""
        self._valid_members = members

    def _ensure_file_exists(self) -> None:
        """Ensure the storage file exists with proper permissions."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)
            os.chmod(self.file_path, 0o644)  # Read/write for owner, read for others

    def _acquire_lock(self, file_obj) -> bool:
        """
        Acquire an exclusive lock on the file.

        Args:
            file_obj: The file object to lock

        Returns:
            True if lock was acquired, False otherwise
        """
        try:
            fcntl.flock(file_obj, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            return False

    def _release_lock(self, file_obj) -> None:
        """Release the lock on the file."""
        fcntl.flock(file_obj, fcntl.LOCK_UN)

    def _read_stories(self) -> List[Story]:
        """Read all stories from the file with locking."""
        max_retries = 10
        retry_delay = 0.1  # seconds

        for attempt in range(max_retries):
            try:
                # Check if file exists and has content
                if (
                    not os.path.exists(self.file_path)
                    or os.path.getsize(self.file_path) == 0
                ):
                    return []

                with open(self.file_path, "r") as f:
                    if self._acquire_lock(f):
                        try:
                            data = json.load(f)
                            return [Story.from_dict(item) for item in data]
                        finally:
                            self._release_lock(f)
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        raise RuntimeError(
                            f"Could not acquire lock on {self.file_path} after {max_retries} attempts"
                        )
            except json.JSONDecodeError as e:
                # If the file contains invalid JSON, log and return empty list
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                # Try to backup the corrupted file and start fresh
                backup_path = self.file_path + ".corrupted"
                try:
                    os.rename(self.file_path, backup_path)
                except OSError:
                    pass
                return []
            except IOError as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise RuntimeError(f"Failed to read stories from {self.file_path}: {e}")

        return []  # Should never reach here

    def _write_stories(self, stories: List[Story]) -> None:
        """Write all stories to the file with locking."""
        max_retries = 10
        retry_delay = 0.1  # seconds

        for attempt in range(max_retries):
            try:
                # Ensure the directory exists (if file path includes directories)
                dir_path = os.path.dirname(self.file_path)
                if dir_path:  # Only create directory if path includes directories
                    os.makedirs(dir_path, exist_ok=True)

                # Write to a temporary file first
                temp_path = self.file_path + ".tmp"
                with open(temp_path, "w") as f:
                    if self._acquire_lock(f):
                        try:
                            json.dump(
                                [story.to_dict() for story in stories], f, indent=2
                            )
                            f.flush()
                            os.fsync(f.fileno())
                        finally:
                            self._release_lock(f)

                # Atomically replace the original file
                os.replace(temp_path, self.file_path)
                return

            except (IOError, OSError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise RuntimeError(f"Failed to write stories to {self.file_path}: {e}")

    def assign(
        self, assigner: str, assignee: str, task_name: str, description: str
    ) -> Story:
        """Assign a new task to a squad member."""
        # Validate assigner and assignee are valid member names
        if self._valid_members:
            if assigner not in self._valid_members:
                raise ValueError(
                    f"Invalid assigner '{assigner}'. "
                    f"Must be one of: {', '.join(self._valid_members)}"
                )
            if assignee not in self._valid_members:
                raise ValueError(
                    f"Invalid assignee '{assignee}'. "
                    f"Must be one of: {', '.join(self._valid_members)}"
                )

        full_description = f"{task_name}: {description}"
        story = Story(
            assignee=assignee, assigner=assigner, description=full_description
        )

        stories = self._read_stories()
        stories.append(story)
        self._write_stories(stories)

        return story

    def get_by_assignee(self, assignee: str) -> List[Story]:
        """Get all tasks assigned to a specific squad member."""
        stories = self._read_stories()
        return [story for story in stories if story.assignee == assignee]

    def get_by_assigner(self, assigner: str) -> List[Story]:
        """Get all tasks assigned by a specific squad member."""
        stories = self._read_stories()
        return [story for story in stories if story.assigner == assigner]

    def complete(self, task_id: str, assignee: str) -> bool:
        """Mark a task as completed."""
        stories = self._read_stories()

        for story in stories:
            if (
                story.task_id == task_id
                and story.assignee == assignee
                and not story.is_completed
            ):
                story.complete()
                self._write_stories(stories)
                return True

        return False

    def get_all(self) -> List[Story]:
        """Get all tasks in the board."""
        return self._read_stories()

    def get_pending_by_assignee(self, assignee: str) -> List[Story]:
        """Get pending (incomplete) tasks assigned to a specific squad member."""
        stories = self._read_stories()
        return [
            story
            for story in stories
            if story.assignee == assignee and not story.is_completed
        ]

    def get_completed_by_assignee(self, assignee: str) -> List[Story]:
        """Get completed tasks assigned to a specific squad member."""
        stories = self._read_stories()
        return [
            story
            for story in stories
            if story.assignee == assignee and story.is_completed
        ]

    def delete(self, task_id: str, assigner: str) -> bool:
        """
        Delete a task from the board.

        Args:
            task_id: The ID of the task to delete
            assigner: The assigner (for verification)

        Returns:
            True if the task was successfully deleted, False otherwise
        """
        stories = self._read_stories()

        for i, story in enumerate(stories):
            if story.task_id == task_id and story.assigner == assigner:
                del stories[i]
                self._write_stories(stories)
                return True

        return False

    def clear_completed(self, assignee: str) -> int:
        """
        Clear all completed tasks for a specific assignee.

        Args:
            assignee: The assignee whose completed tasks should be cleared

        Returns:
            Number of tasks cleared
        """
        stories = self._read_stories()
        initial_count = len(stories)

        # Keep only incomplete tasks or tasks not assigned to this assignee
        stories = [
            story
            for story in stories
            if not (story.assignee == assignee and story.is_completed)
        ]

        cleared_count = initial_count - len(stories)
        if cleared_count > 0:
            self._write_stories(stories)

        return cleared_count

    def create_tools(self, agent_name: str) -> List[callable]:
        """
        Create a list of tools for an agent to interact with the board.

        Args:
            agent_name: The name of the agent that will use these tools

        Returns:
            List of tool functions that can be added to an LLMChatTask
        """
        return [
            self._create_assign_task_tool(agent_name),
            self._create_list_my_tasks_tool(agent_name),
            self._create_complete_my_task_tool(agent_name),
        ]

    def create_triggers(self, agent_name: str) -> List[Callable]:
        """
        Create triggers that check for board events relevant to the agent.

        Args:
            agent_name: The name of the agent that will use these triggers

        Returns:
            List of trigger functions that can be added to an LLMChatTask
        """
        return [
            self._create_new_task_trigger(agent_name),
            self._create_task_completed_trigger(agent_name),
        ]

    def _assign_task_tool(
        self, assigner: str, assignee: str, task_name: str, description: str
    ) -> Dict[str, Any]:
        """Tool implementation for assigning a task."""
        try:
            story = self.assign(assigner, assignee, task_name, description)
            return {
                "success": True,
                "message": f"Task assigned to {assignee}",
                "task_id": story.task_id,
                "task": story.to_dict(),
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to assign task: {str(e)}"}

    def _list_my_tasks_tool(self, agent_name: str) -> Dict[str, Any]:
        """Tool implementation for listing tasks assigned to the agent."""
        try:
            tasks = self.get_by_assignee(agent_name)
            pending = self.get_pending_by_assignee(agent_name)
            completed = self.get_completed_by_assignee(agent_name)

            return {
                "success": True,
                "total_tasks": len(tasks),
                "pending_tasks": len(pending),
                "completed_tasks": len(completed),
                "tasks": [task.to_dict() for task in tasks],
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to list tasks: {str(e)}"}

    def _complete_my_task_tool(self, task_id: str, agent_name: str) -> Dict[str, Any]:
        """Tool implementation for completing a task."""
        try:
            success = self.complete(task_id, agent_name)
            if success:
                return {
                    "success": True,
                    "message": f"Task {task_id} marked as completed",
                }
            else:
                return {
                    "success": False,
                    "message": f"Task {task_id} not found or not assigned to you",
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to complete task: {str(e)}"}

    def _create_assign_task_tool(self, agent_name: str) -> callable:
        """Create a tool for assigning tasks to other agents."""

        def assign_task_to_agent(
            assignee: str, task_name: str, description: str
        ) -> Dict[str, Any]:
            """
            Assign a new task to another agent.

            Args:
                assignee: The agent to assign the task to
                task_name: Short name/identifier for the task
                description: Detailed description of what needs to be done

            Returns:
                Dictionary with success status and task information
            """
            return self._assign_task_tool(
                assigner=agent_name,
                assignee=assignee,
                task_name=task_name,
                description=description,
            )

        # Add metadata to the function for tool registration
        assign_task_to_agent.__name__ = f"assign_task_to_agent"
        assign_task_to_agent.__doc__ = (
            f"Assign a new task to another agent. You are {agent_name}."
        )
        return assign_task_to_agent

    def _create_list_my_tasks_tool(self, agent_name: str) -> callable:
        """Create a tool for listing tasks assigned to the current agent."""

        def list_my_tasks() -> Dict[str, Any]:
            """
            List all tasks assigned to you.

            Returns:
                Dictionary with task information
            """
            return self._list_my_tasks_tool(agent_name)

        # Add metadata to the function for tool registration
        list_my_tasks.__name__ = f"list_my_tasks"
        list_my_tasks.__doc__ = f"List all tasks assigned to you ({agent_name})."
        return list_my_tasks

    def _create_complete_my_task_tool(self, agent_name: str) -> callable:
        """Create a tool for completing tasks assigned to the current agent."""

        def complete_my_task(task_id: str) -> Dict[str, Any]:
            """
            Complete a task that is assigned to you.

            Args:
                task_id: The ID of the task to complete

            Returns:
                Dictionary with success status
            """
            return self._complete_my_task_tool(task_id, agent_name)

        # Add metadata to the function for tool registration
        complete_my_task.__name__ = f"complete_my_task"
        complete_my_task.__doc__ = (
            f"Complete a task that is assigned to you ({agent_name})."
        )
        return complete_my_task

    def _create_new_task_trigger(self, agent_name: str) -> Callable:
        """
        Create a trigger that checks for new tasks assigned to this agent.

        This trigger should be added to an LLMChatTask with to_infinite_stream().
        """
        # Track which tasks we've already notified about
        notified_tasks = set()

        def check_new_tasks() -> str:
            """
            Check for new tasks assigned to this agent.

            Returns:
                A message if there are new tasks, empty string otherwise
            """
            try:
                # Get pending tasks assigned to this agent
                pending_tasks = self.get_pending_by_assignee(agent_name)

                # Find tasks we haven't notified about yet
                new_tasks = []
                for task in pending_tasks:
                    if task.task_id not in notified_tasks:
                        new_tasks.append(task)
                        notified_tasks.add(task.task_id)

                if new_tasks:
                    if len(new_tasks) == 1:
                        task = new_tasks[0]
                        return f"📋 New task assigned to you by {task.assigner}: {task.description}"
                    else:
                        return (
                            f"📋 You have {len(new_tasks)} new task(s) assigned to you"
                        )
                return ""
            except Exception as e:
                # Don't crash the trigger on error
                return f"Error checking for new tasks: {str(e)}"

        check_new_tasks.__name__ = f"check_new_tasks_{agent_name}"
        return to_infinite_stream(check_new_tasks)

    def _create_task_completed_trigger(self, agent_name: str) -> Callable:
        """
        Create a trigger that checks for tasks completed by this agent (as assigner).

        This trigger should be added to an LLMChatTask with to_infinite_stream().
        """
        # Track which completed tasks we've already notified about
        notified_completions = set()

        def check_completed_tasks() -> str:
            """
            Check for tasks completed by this agent (as assigner).

            Returns:
                A message if there are completed tasks, empty string otherwise
            """
            try:
                # Get all tasks assigned by this agent
                my_assigned_tasks = self.get_by_assigner(agent_name)

                # Find completed tasks we haven't notified about yet
                new_completions = []
                for task in my_assigned_tasks:
                    if task.is_completed and task.task_id not in notified_completions:
                        new_completions.append(task)
                        notified_completions.add(task.task_id)

                if new_completions:
                    if len(new_completions) == 1:
                        task = new_completions[0]
                        return (
                            f"✅ Task completed by {task.assignee}: {task.description}"
                        )
                    else:
                        return f"✅ {len(new_completions)} task(s) you assigned have been completed"
                return ""
            except Exception as e:
                # Don't crash the trigger on error
                return f"Error checking for completed tasks: {str(e)}"

        check_completed_tasks.__name__ = f"check_completed_tasks_{agent_name}"
        return to_infinite_stream(check_completed_tasks)
