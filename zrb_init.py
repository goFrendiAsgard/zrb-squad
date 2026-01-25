from zrb import cli, Group, LLMChatTask, StrInput, BoolInput, CFG
from zrb.llm.prompt import PromptManager, new_prompt, get_mandate_prompt, get_persona_prompt, system_context
from zrb.llm.tool import run_shell_command, read_file, list_files, write_file
from zrb_squad import define_squad, Member


# Create squad members
members = [
    Member(
        name="coder",
        chat_task=LLMChatTask(
            name="coder",
            ui_ascii_art="panda",
            ui_jargon="Ngoding sampai mati",
            ui_assistant_name="Coder",
            prompt_manager=PromptManager(
                prompts=[
                    new_prompt(get_persona_prompt("Coder")),
                    new_prompt(get_mandate_prompt()),
                    system_context,
                ]
            ),
            tools=[read_file, list_files, write_file, run_shell_command]
        ),
    ),
    Member(
        name="tester",
        chat_task=LLMChatTask(
            name="tester",
            ui_ascii_art="rose",
            ui_jargon="Bunga didatangi bug",
            ui_assistant_name="Tester",
            prompt_manager=PromptManager(
                prompts=[
                    new_prompt(get_persona_prompt("Tester")),
                    new_prompt(get_mandate_prompt()),
                    system_context,
                ]
            ),
            tools=[read_file, list_files, write_file, run_shell_command]
        ),
    ),
    Member(
        name="documenter",
        chat_task=LLMChatTask(
            name="documenter",
            ui_ascii_art="cat",
            ui_jargon="Miawww",
            ui_assistant_name="Documenter",
            prompt_manager=PromptManager(
                prompts=[
                    new_prompt(get_persona_prompt("Documenter")),
                    new_prompt(get_mandate_prompt()),
                    system_context,
                ]
            ),
            tools=[read_file, list_files, write_file, run_shell_command]
        ),
    ),
]

# Define the development squad
dev_squad_task = define_squad(
    squad_name="dev-team",
    members=members,
    group_description="🤝 Multi-agent squad workflows",
)