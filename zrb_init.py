from zrb import CFG, BoolInput, Group, LLMChatTask, StrInput, cli
from zrb.llm.prompt import (
    PromptManager,
    get_mandate_prompt,
    get_persona_prompt,
    new_prompt,
    system_context,
)
from zrb.llm.tool import list_files, read_file, run_shell_command, write_file

from zrb_squad import Member, Squad

# Define the development squad using the new Squad class
dev_squad = Squad(
    name="dev-team",
    members=[
        Member(
            name="tech-lead",
            chat_task=LLMChatTask(
                name="tech-lead",
                ui_ascii_art="default",
                ui_jargon="Leading the tech revolution",
                ui_assistant_name="Tech Lead",
                prompt_manager=PromptManager(
                    prompts=[
                        new_prompt(get_persona_prompt("Tech Lead")),
                        new_prompt(get_mandate_prompt()),
                        system_context,
                    ]
                ),
                tools=[read_file, list_files, write_file, run_shell_command],
            ),
        ),
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
                tools=[read_file, list_files, write_file, run_shell_command],
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
                tools=[read_file, list_files, write_file, run_shell_command],
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
                tools=[read_file, list_files, write_file, run_shell_command],
            ),
        ),
    ],
    main_agent="tech-lead",
    group_description="🤝 Multi-agent squad workflows",
)
dev_squad_task = dev_squad.serve()
