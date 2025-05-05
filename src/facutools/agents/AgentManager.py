from google.cloud import dialogflowcx_v3beta1 as dfcx3
from uuid import UUID

class AgentManager:
    def __init__(self, credentials, project_name):
        self.credentials = credentials
        self.project_name = project_name
        self.agent_client = dfcx3.AgentsClient(credentials=credentials)
        self.session_client = dfcx3.SessionsClient(credentials=credentials)

    def create_agent(self, agent_name: str, agent_display_name: str, agent_default_language_code: str, agent_time_zone: str):
        agent = dfcx3.Agent()
        agent.display_name = agent_display_name
        agent.default_language_code = agent_default_language_code
        agent.time_zone = agent_time_zone
        agent.advanced_settings.logging_settings.enable_interaction_logging = True

        request = dfcx3.CreateAgentRequest(
            parent=f"projects/{self.project_name}/locations/global",
            agent=agent,
        )

        response = self.agent_client.create_agent(request=request)

        return response
    
    def get_agent(self, agent_name: str):
        request = dfcx3.GetAgentRequest(
            name=agent_name,
        )

        return self.agent_client.get_agent(request=request)
    
    def list_agents(self):
        request = dfcx3.ListAgentsRequest(
            parent=f"projects/{self.project_name}/locations/global",
        )

        return self.agent_client.list_agents(request=request)
    
    def delete_agent(self, agent_name: str):
        request = dfcx3.DeleteAgentRequest(
            name=agent_name,
        )

        return self.agent_client.delete_agent(request=request)
    
    def update_agent(self, agent: dfcx3.Agent):
        request = dfcx3.UpdateAgentRequest(
            agent=agent,
        )

        return self.agent_client.update_agent(request=request)
    
    def restore_agent(self, agent_name: str):
        request = dfcx3.RestoreAgentRequest(
            name=agent_name,
        )

        return self.agent_client.restore_agent(request=request)
    
    def detect_intent(self, agent: dfcx3.Agent, session_id: UUID, texts: list[str], language_code: str = "es-419"):
        session_path = f"{agent.name}/sessions/{session_id}"
        agent_components = self.agent_client.parse_agent_path(agent.name)

        responses = []

        for text in texts:
            text_input = dfcx3.TextInput(text=text)
            query_input = dfcx3.QueryInput(text=text_input, language_code=language_code)
            request = dfcx3.DetectIntentRequest(
                session=session_path,
                query_input=query_input,
            )

            response = self.session_client.detect_intent(request=request)

            response_messages = [
                " ".join(msg.text.text) for msg in response.query_result.response_messages
            ]

            
            responses.append({
                "text": text,
                "response": response_messages
            })

        return responses
