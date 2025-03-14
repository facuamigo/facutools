from uuid import UUID
from facutools.facuamigo.FacuamigoManager import FacuamigoManager
import os
import json
from dotenv import load_dotenv
from google.oauth2 import service_account

from facutools.facuamigo.FacuamigoManager import FacuamigoManager
from facutools.agents.AgentManager import AgentManager

load_dotenv()

service_account_string = os.getenv('SERVICE_ACCOUNT')
service_account_json = json.loads(service_account_string, strict=False)
credentials = service_account.Credentials.from_service_account_info(service_account_json)

fmanager = FacuamigoManager(credentials=credentials)
amanager = AgentManager(credentials=credentials, project_name="guias-uba")

# facuamigo = fmanager.create_facuamigo_agent(
#     subject_name="Sociedad y Estado",
#     agent_name="facuamigo-icse24a-7",
#     project_name="guias-uba",
#     data_store_name="facuamigo-icse24a-7",
#     initial_documents_path="gs://facuamigo/icse24a/documents/*.pdf"
# )

# print(json.dumps(facuamigo, indent=4))

facuamigo = {
    "agent_name": "projects/guias-uba/locations/global/agents/3c3b006a-aa73-4d70-8529-9a4a50cadd26"
}

# session_id = None

session_id = UUID("16ec92c7-2a69-406f-a4dd-5d43e586cb38")

response = fmanager.query_facuamigo_agent(agent_name=facuamigo["agent_name"], query_text="¿Y del otro libro?", session_id=session_id)

print(response)


