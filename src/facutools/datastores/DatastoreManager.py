from google.cloud import discoveryengine
import google.longrunning.operations_proto


class DatastoreManager:
    def __init__(self, credentials):
        self.credentials = credentials
        self.datastore_client = discoveryengine.DataStoreServiceClient(
            credentials=credentials)
        self.documents_client = discoveryengine.DocumentServiceClient(
            credentials=credentials)
        self.engines_client = discoveryengine.EngineServiceClient(
            credentials=credentials)

    def create_datastore(self, project_name: str, data_store_name: str, data_store_display_name: str):
        data_store = discoveryengine.DataStore()
        data_store.display_name = data_store_display_name
        data_store.industry_vertical = discoveryengine.IndustryVertical.GENERIC
        data_store.solution_types = [
            discoveryengine.SolutionType.SOLUTION_TYPE_CHAT]
        data_store.content_config = discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
        data_store.document_processing_config = discoveryengine.DocumentProcessingConfig(
            default_parsing_config=discoveryengine.DocumentProcessingConfig.ParsingConfig(
                ocr_parsing_config=discoveryengine.DocumentProcessingConfig.ParsingConfig.OcrParsingConfig()
            )
        )

        request = discoveryengine.CreateDataStoreRequest(
            parent=f"projects/{project_name}/locations/global/collections/default_collection",
            data_store=data_store,
            data_store_id=data_store_name,
        )

        operation = self.datastore_client.create_data_store(request=request)

        try:
            response = operation.result()
        except Exception as e:
            raise e

        metadata = discoveryengine.CreateDataStoreMetadata(operation.metadata)

        return response

    def get_datastore(self, data_store_name: str):
        request = discoveryengine.GetDataStoreRequest(
            name=data_store_name,
        )

    def get_datastore_path(self, project_name: str, data_store_name: str, location: str = 'global'):
        return self.datastore_client.data_store_path(project=project_name, location=location, data_store=data_store_name)

    def list_datastores(self, project_name: str):
        request = discoveryengine.ListDataStoresRequest(
            parent=f"projects/{project_name}/locations/global",
        )

        return self.datastore_client.list_data_stores(request=request)

    def delete_datastore(self, data_store_name: str):
        request = discoveryengine.DeleteDataStoreRequest(
            name=data_store_name,
        )

        return self.datastore_client.delete_data_store(request=request)

    def update_datastore(self, data_store: discoveryengine.DataStore):
        request = discoveryengine.UpdateDataStoreRequest(
            data_store=data_store,
        )

        return self.datastore_client.update_data_store(request=request)

    def upload_pdf_to_datastore(self, data_store_name: str, pdf_path: str):
        parent = f'{data_store_name}/branches/default_branch'
        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            gcs_source=discoveryengine.GcsSource(
                input_uris=[pdf_path],
                data_schema="content"
            ),
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
        )

        operation = self.documents_client.import_documents(request=request)

        return operation

    def list_engines(self, project_name: str):
        request = discoveryengine.ListEnginesRequest(
            parent=f'projects/{project_name}/locations/global/collections/default_collection',
        )

        return self.engines_client.list_engines(request=request)

    def delete_engine(self, engine_name: str):
        request = discoveryengine.DeleteEngineRequest(
            name=engine_name,
        )

        return self.engines_client.delete_engine(request=request)
