from zrb import LLMChatTask
from zrb.llm.prompt import (
    PromptManager,
    new_prompt,
)
from zrb.llm.tool import list_files, read_file, run_shell_command, write_file

from zrb_squad import Member, Squad

# Define the development squad using the new Squad class
dev_squad = Squad(
    name="dev-team",
    members=[
        Member(
            name="alice",
            chat_task=LLMChatTask(
                name="manager",
                ui_ascii_art="hello-kitty",
                ui_jargon="Boss",
                ui_assistant_name="alice",
                prompt_manager=PromptManager(
                    role="orchestrator",
                    assistant_name="alice",
                    prompts=[
                        new_prompt(
                            "**IMPORTANT** \n"
                            "- Once requirement is clear, ask bob (The Planner) to create plan\n"
                            "- Bob will come up with plan, If you are okay with it, assign charlie and diaz\n"
                            "- If you are not okay with the plan, ask bob to revise the plan and get assign back to you for approval\n"
                            "- When assigning tasks to charlie and diaz, be mindful, one task at a time for each of them\n"
                        )
                    ],
                ),
                tools=[read_file, list_files, write_file, run_shell_command],
                yolo=True,
            ),
        ),
        Member(
            name="bob",
            chat_task=LLMChatTask(
                name="techlead",
                ui_ascii_art="clover",
                ui_jargon="Pasti ada jalan",
                ui_assistant_name="bob",
                prompt_manager=PromptManager(
                    role="planner",
                    assistant_name="bob",
                    prompts=[
                        new_prompt(
                            "**IMPORTANT** \n"
                            "- Assign alice (Orchestrator) to approve your plan\n"
                            "- Your plan should be detailed and broken down into actionable tasks, "
                            "You should also mention who should be responsible to do the task (i.e., charlie for coding, diaz for documenting)\n"
                        )
                    ],
                ),
                tools=[read_file, list_files, write_file, run_shell_command],
                yolo=True,
            ),
        ),
        Member(
            name="charlie",
            chat_task=LLMChatTask(
                name="coder",
                ui_ascii_art="batman",
                ui_jargon="Kerja kerja kerja",
                ui_assistant_name="charlie",
                prompt_manager=PromptManager(
                    role="executor",
                    assistant_name="charlie",
                    prompts=[
                        new_prompt(
                            "**IMPORTANT** \n"
                            "- You are a senior software engineer\n"
                            "- Do every task alice assigned to you\n"
                        )
                    ]
                ),
                tools=[read_file, list_files, write_file, run_shell_command],
            ),
        ),
        Member(
            name="diaz",
            chat_task=LLMChatTask(
                name="documenter",
                ui_ascii_art="cat",
                ui_jargon="Sie dokumentasi",
                ui_assistant_name="diaz",
                prompt_manager=PromptManager(
                    role="executor",
                    assistant_name="diaz",
                    prompts=[
                        new_prompt(
                            "**IMPORTANT** \n"
                            "- You are an expert tech writer\n"
                            "- Do every task alice assigned to you\n"
                        )
                    ]
                ),
                tools=[read_file, list_files, write_file, run_shell_command],
            ),
        ),
    ],
    main_agent="alice",
    group_description="🤝 Multi-agent squad workflows",
)
dev_squad_task = dev_squad.serve()