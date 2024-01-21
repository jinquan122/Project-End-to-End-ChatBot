from llama_index import Prompt

# Step 1.
# Prompt for generating search query. Takes conversation history and the last mesage
# from Human. Rewrites the message to be a standalone question that captures all relevant
# context from the whole conversation.
condense_question_prompt = Prompt("""\
Given a conversation (between Human and Assistant) and a follow up message from Human, \
rewrite the message to be a standalone question that captures all relevant context \
from the conversation.

<Chat History> 
{chat_history}

<Follow Up Message>
{question}

<Standalone question>
""")
                                  
# TODO: Work on this pompt so the answer is more natural instead of:
# "Yes, based on the information provided, there is news about Zelenskiy. The article states that Ukrainian President Volodymyr ..."

# Step 2.
# Prompt for submitting the query results along with the original question to the
# LLM to generate an answer.                             
text_qa_template = Prompt("""\
"Matching article information is below.\n"
"---------------------\n"
"{context_str}\n"
"---------------------\n"
"Given the above information about the articles and not prior knowledge, "
"answer the question: {query_str}\n"
""")

# Step 3. (optional)                     
# If there are too many chunks to stuff in one prompt, “create and refine”
# an answer by going through multiple compact prompts.
refine_template = Prompt("""\
"The original question is as follows: {query_str}\n"
"We have provided an existing answer: {existing_answer}\n"
"We have the opportunity to refine the existing answer "
"(only if needed) with some more context below.\n"
"------------\n"
"{context_msg}\n"
"------------\n"
"Given the new context, refine the original answer to better "
"answer the question. "
"If the context isn't useful, return the original answer."
"Make sure the existing answer match with original questions correctly. Remove unrelevant context."
""")
                         
# Prompt for the initial system guidance and instructions to follow to generate follow up questions                        
followup_template = """\
You are given some text. Your task is to analyze the given text, identify any areas of confusion or missing information, and generate three follow-up questions based on these issues. Please ensure the questions are not hallucinatory and is anchored in real, factual, and verifiable information.Your response must follow the logical structure of the bellow JSON schema:

``` 
{
      "follow_up_questions": {
      "description": "Array of follow up questions",
      "type": "array",
      "items": {
        "type": "string"
      }
}
```
"""

# Prompt for instructing the agent the system rules
# system_prompt = '''
# As a financial crime expert, you are to respond to inquiries regarding financial crime. Please adhere to the following protocol when engaging with user questions:

# 1. Determine if the user's question is related to recent news or events:
#    - If the question is news-related, proceed to the next step.
#    - If the question does not pertain to news, respond with: "I am trained to answer financial crime-related questions only. Do you have any questions about financial crime?"
# 2. Identify the necessary facts within the prompt that will enable you to deliver an informed response to the question.
# 3. Evaluate whether the supplied text contains all the facts required to answer the question accurately. 
# 4. Consider potential responses based on the information you have. If you lack sufficient facts, reply with: "I'm not sure."
# 5. Formulate your response:
#    - Do not start your answer with "Based on information provided..."
#    - Refrain from using phrases like "the articles discuss..."
# 6. Use bullet points to present your answer if that format would enhance the clarity or conciseness of the response.

# Follow these steps systematically to ensure each user question is addressed appropriately.
# '''

# Prompt for instructing the agent the system rules
system_prompt = '''
You are an expert in due diligence in the context of financial crime. Use the following rules when responding to user questions:

- Evaluate whether the supplied text contains all the facts required to answer the question accurately. 
- Consider potential responses based on the information you have. If you lack sufficient facts, reply with: "I'm not sure." or "Could you please provide more information?"
-  Avoid conjecture and hypothesis. Only associate your answers with facts found in the articles.
'''