from zrb import CFG, AnyGroup, AnyTask, CmdTask, Group, LLMChatTask, cli
from zrb.util.string.conversion import to_kebab_case

from .board.any_board import AnyBoard
from .board.factory import create_board


class Member:
    """Represents a member in a squad"""

    def __init__(self, name: str, chat_task: LLMChatTask):
        self.name = name
        self.chat_task = chat_task


class Squad:
    """
    A squad of AI agents that run in parallel tmux panels.

    Example:
        ```python
        squad = Squad(
            name="dev-team",
            members=[
                Member("coder", coder),
                Member("tester", tester),
                Member("documenter", documenter)
            ],
            group_name="dev-team",
            group_description="Development team squad"
        )
        squad.serve()
        ```
    """

    def __init__(
        self,
        name: str,
        members: list[Member],
        board: AnyBoard | None = None,
        main_agent: str | None = None,
        group_name: str | None = None,
        group_description: str | None = None,
    ):
        """
        Initialize a new squad.

        Args:
            name: Name of the squad
            members: List of Member objects, each with a name and chat_task
            board: Optional board instance (defaults to FileBoard if None)
            main_agent: Name of the main agent (defaults to first member if None)
            group_name: Optional name for the group (defaults to kebab-case of squad name)
            group_description: Optional description for the group
        """
        self.name = name
        self.members = members
        self.board = board if board is not None else create_board()
        self.main_agent = main_agent if main_agent is not None else members[0].name
        self.group_name = (
            to_kebab_case(group_name) if group_name is not None else to_kebab_case(name)
        )
        self.group_description = group_description
        self.session_name = f"zrb-squad-{name}"

        # Validate inputs
        self._validate_members()

        # Initialize task as None, will be created when serve() is called
        self._task: AnyTask | None = None

    def serve(self) -> AnyTask:
        """
        Create and register the squad task.

        Returns:
            The created squad task
        """
        # Add board tools and triggers to each member
        self._add_board_tools_and_triggers()

        # Add squad member list tool to each member
        self._add_squad_member_tool()

        # Create the main group
        main_group = cli.add_group(
            Group(name=self.group_name, description=self.group_description)
        )
        member_group = main_group.add_group(
            Group(name="member", description="Agent related tasks")
        )

        # Create the squad task
        self._task = self._create_squad_task()

        # Add the task to the group
        main_group.add_task(self._task, alias="start")

        # Add individual member tasks to the group
        for member in self.members:
            member_group.add_task(member.chat_task)

        return self._task

    @property
    def task(self) -> AnyTask | None:
        """Get the squad task (only available after serve() is called)."""
        return self._task

    def _validate_members(self) -> None:
        """Validate that the squad has at least one member."""
        if not self.members:
            raise ValueError("Squad must have at least one member")

        # Validate main_agent exists in members
        member_names = [member.name for member in self.members]
        if self.main_agent not in member_names:
            raise ValueError(
                f"Main agent '{self.main_agent}' not found in squad members: {member_names}"
            )

    def _add_board_tools_and_triggers(self) -> None:
        """Add board tools and triggers to each member's chat task."""
        for member in self.members:
            # Add board tools
            board_tools = self.board.create_tools(member.name)
            for tool in board_tools:
                member.chat_task.add_tool(tool)

            # Add board triggers
            board_triggers = self.board.create_triggers(member.name)
            for trigger in board_triggers:
                member.chat_task.add_trigger(trigger)

    def _add_squad_member_tool(self) -> None:
        """Add a tool to each member that lists all squad members."""
        member_names = [member.name for member in self.members]
        squad_name = self.name
        main_agent = self.main_agent

        # Add this tool to each member
        for member in self.members:
            # Create a tool specific to this member using a factory function
            # that captures the current member's name in a closure
            member_tool = self._create_squad_member_tool_for_agent(
                agent_name=member.name,
                squad_name=squad_name,
                main_agent=main_agent,
                all_members=member_names,
            )
            member.chat_task.add_tool(member_tool)

    def _create_squad_member_tool_for_agent(
        self, agent_name: str, squad_name: str, main_agent: str, all_members: list[str]
    ) -> callable:
        """Create a squad member listing tool for a specific agent."""

        def list_squad_members() -> dict:
            """
            List all members in your squad.

            Returns:
                Dictionary with squad information
            """
            return {
                "success": True,
                "squad_name": squad_name,
                "main_agent": main_agent,
                "your_name": agent_name,
                "members": all_members,
                "total_members": len(all_members),
            }

        list_squad_members.__name__ = f"list_squad_members"
        list_squad_members.__doc__ = (
            f"List all members in your squad. You are {agent_name}."
        )
        return list_squad_members

    def _create_squad_task(self) -> CmdTask:
        """Create the CmdTask that starts the squad."""
        full_cmd = self._build_tmux_commands()

        # Add a message about assigning initial task
        cmd_with_message = self._add_initial_task_message(full_cmd)

        return CmdTask(
            name=f"start-{self.name}",
            description=f"Start {self.name} squad with {len(self.members)} members",
            cmd=cmd_with_message,
            is_interactive=True,
            render_cmd=False,
        )

    def _add_initial_task_message(self, original_cmd: str) -> str:
        """Add a message about assigning initial task to the main agent."""
        message = f'echo "🚀 Starting {self.name} squad with {len(self.members)} members..."\n'
        return message + original_cmd

    def _build_tmux_commands(self) -> str:
        """Build the complete tmux command script."""
        cmd_parts = []

        # Check if we're inside a tmux session
        cmd_parts.append('if [ -n "$TMUX" ]; then')
        cmd_parts.append("  # Inside tmux, create a new window in current session")
        cmd_parts.append('  current_session=$(tmux display-message -p "#S")')
        cmd_parts.append(f"  # Check if window already exists")
        cmd_parts.append(
            f'  if tmux list-windows -t ${{current_session}} -F "#W" | grep -q "^{self.session_name}$"; then'
        )
        cmd_parts.append(
            f"    echo \"Error: Window '{self.session_name}' already exists in session '${{current_session}}'\""
        )
        cmd_parts.append(
            f'    echo "Please close the existing window first or use a different squad name"'
        )
        cmd_parts.append(f"    exit 0")
        cmd_parts.append(f"  fi")
        cmd_parts.extend(self._build_new_window_commands())
        cmd_parts.append("else")
        cmd_parts.append("  # Not inside tmux, create a new session")
        # Kill any existing session with the same name
        cmd_parts.append(self._build_kill_session_command())
        cmd_parts.extend(self._build_detached_session_commands())
        cmd_parts.append("fi")

        # Join all commands with newlines for the if/else structure
        return "\n".join(cmd_parts)

    def _build_kill_session_command(self) -> str:
        """Build command to kill any existing session with the same name."""
        return f"tmux kill-session -t {self.session_name} 2>/dev/null || true"

    def _build_new_window_commands(self) -> list[str]:
        """Build commands for creating a new window in current tmux session."""
        commands = []
        first_member = self.members[0]
        first_cmd = self._build_member_command(first_member)

        # Get current session name to create window in the same session
        commands.append('  current_session=$(tmux display-message -p "#S")')

        # Create new window with first member
        commands.append(f"  # Creating new window in current session")
        commands.append(f'  tmux new-window -n "{self.session_name}" "{first_cmd}"')

        # Wait a bit for the window to be ready
        commands.append("  sleep 0.5")

        # Get the window ID
        commands.append('  window_id=$(tmux display-message -p "#I")')

        # Create panes for remaining members
        for i, member in enumerate(self.members[1:], 1):
            cmd = self._build_member_command(member)
            commands.append(
                f'  tmux split-window -t ${{current_session}}:${{window_id}} -h "{cmd}"'
            )

        # Set pane titles for all members
        for i, member in enumerate(self.members):
            commands.append(
                f'  tmux select-pane -t ${{current_session}}:${{window_id}}.{i} -T "{member.name}"'
            )

        # Tile the layout
        commands.append(
            f"  tmux select-layout -t ${{current_session}}:${{window_id}} tiled"
        )

        # Switch to the new window
        commands.append(f"  tmux select-window -t ${{current_session}}:${{window_id}}")

        return commands

    def _build_new_session_commands(self, switch_to_session: bool = True) -> list[str]:
        """Build commands for creating a new tmux session."""
        commands = []
        first_member = self.members[0]
        first_cmd = self._build_member_command(first_member)

        commands.append(f"  # Creating new session and switching to it")
        commands.append(
            f'  tmux new-session -d -s {self.session_name} -n "{self.session_name}" "{first_cmd}"'
        )

        # Wait a bit for the session to be ready
        commands.append("  sleep 0.5")

        # Create panes for remaining members
        for i, member in enumerate(self.members[1:], 1):
            cmd = self._build_member_command(member)
            commands.append(f'  tmux split-window -t {self.session_name} -h "{cmd}"')

        # Set pane titles for all members
        for i, member in enumerate(self.members):
            commands.append(
                f'  tmux select-pane -t {self.session_name}:0.{i} -T "{member.name}"'
            )

        # Tile the layout
        commands.append(f"  tmux select-layout -t {self.session_name} tiled")

        if switch_to_session:
            # Try to switch to the new session, fall back to attaching if switch fails
            commands.append(f"  # Try to switch to the new session")
            commands.append(
                f"  if tmux switch-client -t {self.session_name} 2>/dev/null; then"
            )
            commands.append(f'    echo "Switched to session: {self.session_name}"')
            commands.append(f"  else")
            commands.append(
                f'    echo "Could not switch, attaching to session: {self.session_name}"'
            )
            commands.append(f"    tmux attach-session -t {self.session_name}")
            commands.append(f"  fi")

        return commands

    def _build_detached_session_commands(self) -> list[str]:
        """Build commands for creating a detached tmux session when not inside tmux."""
        commands = []
        first_member = self.members[0]
        first_cmd = self._build_member_command(first_member)

        commands.append(f"  # Not inside tmux, use normal detached session with attach")
        commands.append(
            f'  tmux new-session -d -s {self.session_name} -n "{self.session_name}" "{first_cmd}"'
        )

        # Create panes for remaining members
        for i, member in enumerate(self.members[1:], 1):
            cmd = self._build_member_command(member)
            commands.append(f'  tmux split-window -t {self.session_name} -h "{cmd}"')

        # Set pane titles for all members
        for i, member in enumerate(self.members):
            commands.append(
                f'  tmux select-pane -t {self.session_name}:0.{i} -T "{member.name}"'
            )

        # Tile the layout
        commands.append(f"  tmux select-layout -t {self.session_name} tiled")

        # Attach to the session
        commands.append(f"  tmux attach-session -t {self.session_name}")

        return commands

    def _build_member_command(self, member: Member) -> str:
        """Build the shell command to run a member's chat task."""
        # Wrap command to keep shell alive even if command exits
        # Use $SHELL if available, otherwise fall back to bash
        return f"{CFG.ROOT_GROUP_NAME} {self.group_name} member {member.chat_task.name}; exec ${{SHELL:-bash}} -i"
