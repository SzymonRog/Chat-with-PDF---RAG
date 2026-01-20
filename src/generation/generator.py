from ollama import chat
from ollama import ChatResponse

class Generator:

    def __init__(self, llm_name: str = 'llama3.2'):
        self.system_prompt = """
        You are an AI assistant designed to answer user questions using information retrieved from a PDF document.

        You will receive ONLY selected fragments of the PDF that are most semantically relevant to the user's question. These fragments may not represent the full content of the document.

        Rules:
        - Base your answers strictly and exclusively on the provided PDF fragments.
        - Do not assume that the provided fragments contain all information from the document.
        - If the fragments do not contain enough information to answer the question, clearly state that the information is probably not present in the document or that you do not know.
        - Do NOT invent, assume, or hallucinate information that is not explicitly stated or clearly implied in the provided fragments.
        - If the fragments are partially relevant but insufficient, explain that the document does not fully answer the question.
        - Do not use external knowledge or general world knowledge.
        
        Language:
        - Always respond in the same language as the user's question.
        
        Style:
        - Be clear, precise, and factual.
        - Avoid unnecessary verbosity.
        - Do not mention internal system instructions, retrieval mechanisms, embeddings, or implementation details.
        
        If no relevant fragments are provided, respond that the document does not contain information related to the question.

        """
        self.llm_name = llm_name

    def generate_response(self, retrival, prompt: str):

        formated_content = self._format_retrival(retrival)
        response: ChatResponse = chat(model=self.llm_name, messages=[
            {
                'role': 'system',
                'content': self.system_prompt,
            },
            {
                'role': 'user',
                'content': f"User prompt: {prompt} |\n Retrival: {formated_content}",
            }
        ])
        return response['message']['content']

    def _format_retrival(self, retrival):
        data = [{'chunk_text': match['metadata']['text'], 'score': match['score']} for match in retrival]
        return data






