from google.cloud import dialogflowcx_v3beta1 as dfcx3

from facutools.datastores import DatastoreManager
from facutools.agents import AgentManager

class PlaybookManager:
    def __init__(self, credentials):
        self.credentials = credentials
        self.client = dfcx3.PlaybooksClient(credentials=credentials)
        self.datastore_manager: DatastoreManager = DatastoreManager(credentials=credentials)
        self.agent_manager: AgentManager = AgentManager(credentials=credentials, project_name="guias-uba")

    def create_playbook(self, agent: dfcx3.Agent, playbook_display_name: str, playbook_subject_name: str, tool: dfcx3.Tool):
        playbook = dfcx3.Playbook()
        playbook.display_name = "AI Assistant Playbook"
        playbook.goal = f'Your goal is to help the user by answering his questions about a subject called "{playbook_subject_name}" based on your knowledge. You have to always answer in Spanish and only to questions related to the specified subject.'
        
        steps = [
            playbook.Step(text="Greet the users, then ask how you can help them today."),
            playbook.Step(text=f"Use ${f'TOOL:{tool.display_name}'} to help the user with their task."),
            playbook.Step(
                text="Summarize the user's request and ask them to confirm that you understood correctly.",
                steps=[
                    playbook.Step(text="If necessary, seek clarifying details.")
                ]
            )
        ]

        playbook.instruction = dfcx3.Playbook.Instruction(steps=steps)
        playbook.referenced_tools = [tool.name]

        request = dfcx3.CreatePlaybookRequest(parent=agent.name, playbook=playbook)

        response = self.client.create_playbook(request=request)

        agent.start_playbook = response.name

        self.agent_manager.update_agent(agent=agent)

        return response