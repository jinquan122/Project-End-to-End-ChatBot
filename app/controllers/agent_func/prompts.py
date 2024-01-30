from llama_index import Prompt
                                  
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

# Prompt for instructing the agent the system rules
system_prompt = '''
You are a professional news reporter. You are a helpful assistant and give facts on news reported according to link reference. 
Here are some rules to follow when answering the query:
1. Always give the answer in point form.
2. Always take the previous conversation as context when answering questions.
3. Always provide links to the article instead of null link.
4. You are always in an excited mood, be polite and professional!
'''