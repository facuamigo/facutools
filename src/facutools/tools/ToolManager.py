from google.cloud import dialogflowcx_v3beta1 as dfcx3

from facutools.datastores import DatastoreManager

class ToolManager:
    def __init__(self, credentials):
        self.credentials = credentials
        self.client = dfcx3.ToolsClient(credentials=credentials)
        self.datastore_manager: DatastoreManager = DatastoreManager(credentials=credentials)

    def create_tool(self, agent: dfcx3.Agent, tool_display_name: str, tool_description: str, datastore_name: str):
        data_store_spec = dfcx3.Tool.DataStoreTool(
            data_store_connections = [
                dfcx3.DataStoreConnection(
                    data_store_type=dfcx3.DataStoreType.UNSTRUCTURED,
                    data_store=datastore_name,
                    document_processing_mode=dfcx3.DocumentProcessingMode.DOCUMENTS
                )
            ]
        )

        tool = dfcx3.Tool(
            tool_type=dfcx3.Tool.ToolType.CUSTOMIZED_TOOL,
            display_name=tool_display_name,
            description=tool_description,
            data_store_spec=data_store_spec
        )

        request = dfcx3.CreateToolRequest(parent=agent.name, tool=tool)
        response = self.client.create_tool(request=request)
        return response