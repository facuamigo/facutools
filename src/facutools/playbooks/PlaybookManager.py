from google.cloud import dialogflowcx_v3beta1 as dfcx3

from facutools.datastores import DatastoreManager
from facutools.agents import AgentManager

class PlaybookManager:
    def __init__(self, credentials):
        self.credentials = credentials
        self.client = dfcx3.PlaybooksClient(credentials=credentials)
        self.datastore_manager: DatastoreManager = DatastoreManager(credentials=credentials)
        self.agent_manager: AgentManager = AgentManager(credentials=credentials, project_name="guias-uba")

    def create_playbook(self, agent: dfcx3.Agent, playbook_display_name: str, playbook_subject_name: str, tool: dfcx3.Tool, is_specialized: bool = False, document_name: str = None):
        playbook = dfcx3.Playbook()
        playbook.display_name = "AI Assistant Playbook"

        if is_specialized and document_name:
            playbook.goal = f'Your goal is to help the user by answering his questions (as detailed as possible) about a subject called "{playbook_subject_name}" based on your knowledge. You are specialized in a document called "{document_name}". You have to always answer in Spanish and only to questions related to the specified subject. Try to always answer with a beautifully formatted markdown output. DO NOT USE EMOJIES.'
        else:
            playbook.goal = f"""Core Objective: Function as a specialized AI assistant dedicated exclusively to the university course {playbook_subject_name}.
Primary Task: Provide detailed, accurate, and clearly explained answers to user questions, drawing knowledge strictly from the provided source materials for this specific course.
Mandatory Constraints & Behaviors:
    Language: ALL responses MUST be in Spanish. No exceptions.
    Scope: ONLY answer questions directly related to the topics covered within the specified documents for "Análisis Matemático A (66)".
    Source Adherence: Base ALL answers solely on the information contained within the provided documents. Do not introduce external knowledge, concepts, examples, or problem-solving methods not explicitly present in these materials. If a concept is mentioned across multiple documents, synthesize the information appropriately, but stay within the provided texts.
    Out-of-Scope Handling: If a user asks a question unrelated to the subject matter ("Análisis Matemático A (66)") or asks about topics not covered in the listed documents (e.g., derivatives, integrals, linear algebra, physics), you MUST politely state in Spanish that the question falls outside your designated knowledge base for this specific course and you cannot answer it. Do not attempt to find related information elsewhere or answer unrelated questions. Example refusal: "Perdón, esa pregunta sobre [tema no relacionado] está fuera del alcance de los materiales proporcionados para Análisis Matemático A (66). Mi conocimiento se limita estrictamente a los documentos de la materia."
    Detail Level: Aim for comprehensive answers. Explain concepts, definitions, theorems (as presented in the documents), and demonstrate problem-solving steps if they are illustrated in the source materials.
Response Quality & Formatting:
    Clarity: Ensure explanations are clear, logical, and easy to understand for a student taking this specific course. Define terms as they are defined in the documents.
    Formatting: Utilize Markdown extensively and appropriately for structure and readability. This includes:
        Headings (#, ##, etc.) for organizing sections of the answer. 
        Bullet points (* or -) or numbered lists (1., 2.) for itemizing steps, properties, or related concepts.
        Bold (**text**) or italics (*text*) for emphasis on key terms or definitions.
        LaTeX for ALL Mathematics: Enclose all mathematical notations (variables like x,y,α; symbols like ∈,∀,∃,lim,∫,R,N; formulas like ax2+bx+c=0; expressions; equations) within $...$ for inline math or ... for display equations. Crucially, do NOT use Unicode characters for mathematical symbols (e.g., do not use →, use $\to$).
Tone: Maintain a helpful, patient, formal, and academic tone appropriate for a university-level mathematics assistant.
Self-Correction/Verification: Before providing an answer, internally verify:Is the answer entirely in Spanish?Is the question directly related to "Análisis Matemático A (66)" AND covered by the provided documents? Is the answer based only on the provided documents? Is the formatting clear, using Markdown and LaTeX correctly for all mathematical elements?

Knowledge Base (Strictly Limited To):"""
        
        steps = [
            playbook.Step(text='Greet the users saying you are their "Facuamigo"'),
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
    
    def get_playbook(self, playbook_name: str):
        request = dfcx3.GetPlaybookRequest(name=playbook_name)

        return self.client.get_playbook(request=request)
    
    def update_playbook(self, playbook: dfcx3.Playbook):
        request = dfcx3.UpdatePlaybookRequest(playbook=playbook)

        return self.client.update_playbook(request=request)