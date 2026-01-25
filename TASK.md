# Background

Zrb squad is a POC of @~/zrb project extension to create a multi-agent workflow.

# Requirement

## Public API

Zrb squad expose a single public function: `define_squad` with the following parameters:
- `squad_name: str`
- `members: list[Member]`
    - A Member is a traditional python class containing:
        - `name: str`
        - `chat_task: LLMChatTask` (See @~/zrb/src/zrb/llm/task/llm_chat_task.py)
- `group: AnyGroup` (See @~/zrb/src/zrb/group/any_group.py)

When executed, the `define_squad` function will:
- Create a task named `start` under the `group`
- When the task is executed, it creates new tmux panel, each with the name of member, and start the respective chat_task

# Task

- Implement the prototype under zrb_squad folder
- At zrb_init.py, create a simple use case of zrb squad, call `define_squad`, make a simple and verifiable example
