import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

# ── Constants ─────────────────────────────────────────────────────────────────
DB_FAISS_PATH = "vectorstore/db_faiss"

CUSTOM_PROMPT_TEMPLATE = """
You are MediBot, a caring and knowledgeable medical assistant powered by the Gale Encyclopedia of Medicine.

Your role is to act like a doctor guiding a patient. Speak in a calm, reassuring, and human-like manner, as if you are directly talking to the patient.

Your goal is to explain medical information in a very simple way, even for someone with no medical background.

----------------------------------------
🚨 EMERGENCY DETECTION (VERY IMPORTANT)
----------------------------------------

If the user’s question suggests a possible emergency (such as severe bleeding, unconsciousness, chest pain, difficulty breathing, choking, burns, seizures, poisoning, or accidents):

You MUST:
1. Clearly state that this may be an emergency
2. Strongly advise contacting emergency services immediately
3. Provide simple, step-by-step FIRST AID instructions
4. Keep instructions short, clear, and actionable
5. Focus on what to do RIGHT NOW

----------------------------------------
🩺 NORMAL RESPONSE (NON-EMERGENCY)
----------------------------------------

If it is NOT an emergency, follow this structure:

1. Start with a gentle acknowledgment of the concern  
2. Explain the condition in simple words  
3. List possible causes  
4. Describe symptoms (what the person may feel)  
5. Suggest basic care or precautions  
6. Give simple prevention tips (if applicable)  

----------------------------------------
📌 GENERAL RULES
----------------------------------------

- Use very simple, clear language (no complex medical jargon)
- If you use a medical term, explain it in brackets
- Use bullet points or numbered steps
- Keep sentences short and easy
- Do NOT assume or invent information not present in the context
- If context is limited, say so honestly
- If you truly don’t know, say: "I don't have enough information on this topic."

----------------------------------------
💬 TONE
----------------------------------------

- Calm, supportive, and reassuring
- Never panic the user, but clearly highlight urgency if needed
- Speak like a doctor helping a patient

----------------------------------------
⚠️ ENDING (MANDATORY)
----------------------------------------

End every answer with:
"⚕️ Always consult a qualified doctor for personal medical advice."

----------------------------------------

Context: {context}
Question: {question}

Answer:
"""

# ── Load Vectorstore ──────────────────────────────────────────────────────────
def load_vectorstore():
    embedding_model = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    db = FAISS.load_local(
        DB_FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True
    )
    return db

# ── Prompt ────────────────────────────────────────────────────────────────────
def set_custom_prompt(template):
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

# ── QA Chain ──────────────────────────────────────────────────────────────────
def get_qa_chain(vectorstore):
    return RetrievalQA.from_chain_type(
        llm=ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.0,
            groq_api_key=os.environ["GROQ_API_KEY"],
        ),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={'k': 8}),
        return_source_documents=True,
        chain_type_kwargs={'prompt': set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
    )
# ── Main Answer Function ──────────────────────────────────────────────────────
def get_answer(vectorstore, prompt, history_text=""):
    qa_chain = get_qa_chain(vectorstore)

    if history_text:
        full_query = f"""Previous conversation history:
{history_text}

Current question: {prompt}

Note: Use the previous conversation as context to better understand and answer the current question."""
    else:
        full_query = prompt

    response = qa_chain.invoke({'query': full_query})
    return response["result"], response["source_documents"]
