from uuid import uuid4, UUID
from google.cloud import discoveryengine
from google.longrunning import operations_proto

from facutools.agents.AgentManager import AgentManager
from facutools.datastores.DatastoreManager import DatastoreManager
from facutools.tools.ToolManager import ToolManager
from facutools.playbooks.PlaybookManager import PlaybookManager

class FacuamigoManager:
    def __init__(self, credentials, project_name: str = "guias-uba"):
        self.credentials = credentials
        self.datastore_manager = DatastoreManager(credentials=credentials)
        self.agent_manager = AgentManager(credentials=credentials, project_name=project_name)
        self.tool_manager = ToolManager(credentials=credentials)
        self.playbook_manager = PlaybookManager(credentials=credentials)

    def create_facuamigo_agent(self, subject_name: str, agent_name: str, project_name: str, data_store_name: str, initial_documents_path: str = None):
        info = {
            "subject_id": subject_name,
            "agent_name": None,
            "project_name": project_name,
            "data_store_name": None,
            "initial_documents_path": initial_documents_path
        }
        
        created_datastore: discoveryengine.DataStore = self.datastore_manager.create_datastore(
            project_name=project_name,
            data_store_name=data_store_name,
            data_store_display_name=data_store_name,
        )
        
        info["data_store_name"] = created_datastore.name
        print(f"Created datastore")
        
        if initial_documents_path:
            import_operation: operations_proto.Operation = self.datastore_manager.upload_pdf_to_datastore(
                data_store_name=created_datastore.name,
                pdf_path=initial_documents_path
            ).operation

            info["import_operation_name"] = import_operation.name

            print(f"Started importing documents to datastore")

        created_agent = self.agent_manager.create_agent(
            agent_name=agent_name,
            agent_display_name=agent_name,
            agent_default_language_code="es-419",
            agent_time_zone="America/Argentina/Buenos_Aires"
        )

        info["agent_name"] = created_agent.name
        print(f"Created Agent")

        created_tool = self.tool_manager.create_tool(
            agent=created_agent,
            tool_display_name=f"Subject Tool",
            tool_description=f"This tool is used every time a user asks any question. The datastore is used to answer the question that the user is asking.",
            datastore_name=created_datastore.name
        )

        print(f"Created Tool")

        created_playbook = self.playbook_manager.create_playbook(
            agent=created_agent,
            playbook_display_name=f"{subject_name} Playbook",
            playbook_subject_name=subject_name,
            tool=created_tool
        )

        print(f"Created Playbook")

        return info
    
    def delete_facuamigo_agent(self, subject_id: str):
        data_stores = self.datastore_manager.list_datastores(project_name='guias-uba')
        engines = self.datastore_manager.list_engines(project_name='guias-uba')

        for data_store in data_stores:
            data_store_path = data_store.name

            if subject_id in data_store_path:
                has_engine = False

                for engine in engines:
                    if data_store.display_name in engine.data_store_ids:
                        has_engine = True
                        break

                if has_engine:
                    self.datastore_manager.delete_engine(engine.name)

                self.datastore_manager.delete_datastore(data_store_path)

    def query_facuamigo_agent(self, agent_name: str, query_text: str, session_id: UUID):
        agent = self.agent_manager.get_agent(agent_name=agent_name)

        if not session_id:
            session_id = uuid4()
        else:
            print(f"Using existing session ID: {session_id}")
        
        response = self.agent_manager.detect_intent(
            agent=agent,
            session_id=session_id,
            texts=[query_text],
            language_code="es-419"
        )
        
        return response