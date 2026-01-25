from zrb import AnyTask, AnyGroup, CmdTask, LLMChatTask, cli, Group, CFG
from zrb.util.string.conversion import to_kebab_case


class Member:
    """Represents a member in a squad"""
    def __init__(self, name: str, chat_task: LLMChatTask):
        self.name = name
        self.chat_task = chat_task


def define_squad(
    squad_name: str,
    members: list[Member],
    group_name: str | None = None,
    group_description: str | None = None,
) -> AnyTask:
    """
    Define a squad of AI agents that run in parallel tmux panels
    
    Args:
        squad_name: Name of the squad
        members: List of Member objects, each with a name and chat_task
        group: The group to add the squad task to
    
    Returns:
        The created squad task
    """
    # Validate inputs
    _validate_members(members)
    # Create a unique session name for tmux
    session_name = _generate_session_name(squad_name)
    group_name = to_kebab_case(group_name) if group_name is not None else to_kebab_case(squad_name)
    # Create the main group
    group = cli.add_group(Group(name=group_name, description=group_description))
    # Create the squad task
    squad_task = _create_squad_task(squad_name, session_name, group_name, members)
    # Add the task to the group
    group.add_task(squad_task, alias="start")
    for member in members:
        group.add_task(member.chat_task)
    return squad_task


def _validate_members(members: list[Member]) -> None:
    """Validate that the squad has at least one member."""
    if not members:
        raise ValueError("Squad must have at least one member")


def _generate_session_name(squad_name: str) -> str:
    """Generate a unique tmux session name for the squad."""
    return f"zrb-squad-{squad_name}"


def _create_squad_task(
    squad_name: str,
    session_name: str,
    group_name: str,
    members: list[Member],
) -> CmdTask:
    """Create the CmdTask that starts the squad."""
    full_cmd = _build_tmux_commands(session_name, group_name, members)
    return CmdTask(
        name=f"start-{squad_name}",
        description=f"Start {squad_name} squad with {len(members)} members",
        cmd=full_cmd,
        is_interactive=True,
        render_cmd=False
    )


def _build_tmux_commands(session_name: str, group_name: str, members: list[Member]) -> str:
    """Build the complete tmux command script."""
    cmd_parts = []
    
    # Check if we're inside a tmux session
    cmd_parts.append('if [ -n "$TMUX" ]; then')
    cmd_parts.append('  # Inside tmux, create a new window in current session')
    cmd_parts.append('  current_session=$(tmux display-message -p "#S")')
    cmd_parts.append(f'  # Check if window already exists')
    cmd_parts.append(f'  if tmux list-windows -t ${{current_session}} -F "#W" | grep -q "^{session_name}$"; then')
    cmd_parts.append(f'    echo "Error: Window \'{session_name}\' already exists in session \'${{current_session}}\'"')
    cmd_parts.append(f'    echo "Please close the existing window first or use a different squad name"')
    cmd_parts.append(f'    exit 0')
    cmd_parts.append(f'  fi')
    cmd_parts.extend(_build_new_window_commands(session_name, group_name, members))
    cmd_parts.append('else')
    cmd_parts.append('  # Not inside tmux, create a new session')
    # Kill any existing session with the same name
    cmd_parts.append(_build_kill_session_command(session_name))
    cmd_parts.extend(_build_detached_session_commands(session_name, group_name, members))
    cmd_parts.append('fi')
    
    # Join all commands with newlines for the if/else structure
    return "\n".join(cmd_parts)


def _build_kill_session_command(session_name: str) -> str:
    """Build command to kill any existing session with the same name."""
    return f"tmux kill-session -t {session_name} 2>/dev/null || true"


def _build_new_window_commands(
    session_name: str, 
    group_name: str,
    members: list[Member]
) -> list[str]:
    """Build commands for creating a new window in current tmux session."""
    commands = []
    first_member = members[0]
    first_cmd = _build_member_command(group_name, first_member)
    
    # Get current session name to create window in the same session
    commands.append('  current_session=$(tmux display-message -p "#S")')
    
    # Create new window with first member
    commands.append(f'  # Creating new window in current session')
    commands.append(f'  tmux new-window -n "{session_name}" "{first_cmd}"')
    
    # Wait a bit for the window to be ready
    commands.append('  sleep 0.5')
    
    # Get the window ID
    commands.append('  window_id=$(tmux display-message -p "#I")')
    
    # Create panes for remaining members
    for i, member in enumerate(members[1:], 1):
        cmd = _build_member_command(group_name, member)
        commands.append(f'  tmux split-window -t ${{current_session}}:${{window_id}} -h "{cmd}"')
    
    # Set pane titles for all members
    for i, member in enumerate(members):
        commands.append(f'  tmux select-pane -t ${{current_session}}:${{window_id}}.{i} -T "{member.name}"')
    
    # Tile the layout
    commands.append(f'  tmux select-layout -t ${{current_session}}:${{window_id}} tiled')
    
    # Switch to the new window
    commands.append(f'  tmux select-window -t ${{current_session}}:${{window_id}}')
    
    return commands


def _build_new_session_commands(
    session_name: str, 
    group_name: str,
    members: list[Member],
    switch_to_session: bool = True
) -> list[str]:
    """Build commands for creating a new tmux session."""
    commands = []
    first_member = members[0]
    first_cmd = _build_member_command(group_name, first_member)
    
    commands.append(f'  # Creating new session and switching to it')
    commands.append(f'  tmux new-session -d -s {session_name} -n "{session_name}" "{first_cmd}"')
    
    # Wait a bit for the session to be ready
    commands.append('  sleep 0.5')
    
    # Create panes for remaining members
    for i, member in enumerate(members[1:], 1):
        cmd = _build_member_command(group_name, member)
        commands.append(f'  tmux split-window -t {session_name} -h "{cmd}"')
    
    # Set pane titles for all members
    for i, member in enumerate(members):
        commands.append(f'  tmux select-pane -t {session_name}:0.{i} -T "{member.name}"')
    
    # Tile the layout
    commands.append(f'  tmux select-layout -t {session_name} tiled')
    
    if switch_to_session:
        # Try to switch to the new session, fall back to attaching if switch fails
        commands.append(f'  # Try to switch to the new session')
        commands.append(f'  if tmux switch-client -t {session_name} 2>/dev/null; then')
        commands.append(f'    echo "Switched to session: {session_name}"')
        commands.append(f'  else')
        commands.append(f'    echo "Could not switch, attaching to session: {session_name}"')
        commands.append(f'    tmux attach-session -t {session_name}')
        commands.append(f'  fi')
    
    return commands


def _build_detached_session_commands(
    session_name: str, 
    group_name: str,
    members: list[Member]
) -> list[str]:
    """Build commands for creating a detached tmux session when not inside tmux."""
    commands = []
    first_member = members[0]
    first_cmd = _build_member_command(group_name, first_member)
    
    commands.append(f'  # Not inside tmux, use normal detached session with attach')
    commands.append(f'  tmux new-session -d -s {session_name} -n "{first_member.name}" "{first_cmd}"')
    
    # Create panes for remaining members
    for i, member in enumerate(members[1:], 1):
        cmd = _build_member_command(group_name, member)
        commands.append(f'  tmux split-window -t {session_name} -h "{cmd}"')
    
    # Set pane titles for all members
    for i, member in enumerate(members):
        commands.append(f'  tmux select-pane -t {session_name}:0.{i} -T "{member.name}"')
    
    # Tile the layout
    commands.append(f'  tmux select-layout -t {session_name} tiled')
    
    # Attach to the session
    commands.append(f'  tmux attach-session -t {session_name}')
    
    return commands


def _build_member_command(group_name: str, member: Member) -> str:
    """Build the shell command to run a member's chat task."""
    # Wrap command to keep shell alive even if command exits
    # Use $SHELL if available, otherwise fall back to bash
    return f"{CFG.ROOT_GROUP_NAME} {group_name} {member.chat_task.name}; exec ${{SHELL:-bash}} -i"


