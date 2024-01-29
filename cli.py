import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer
from assistant import OpenAIAssistant
from langchain_openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
from tfquery.tfstate import parse_resources
from langchain_openai import ChatOpenAI
from langchain.schema.document import Document
import glob
from langchain.memory import ConversationBufferMemory
from yaspin import yaspin
from langchain.llms import Replicate
from langchain.callbacks.base import BaseCallbackHandler
import atexit
from langchain.prompts import PromptTemplate
from langchain.globals import set_debug


#set_debug(True)



REPLICATE_CODE_LLAMA_ENDPOINT = "meta/codellama-34b-instruct:b17fdb44c843000741367ae3d73e2bb710d7428a662238ddebbf4302db2b5422"

class StreamHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        print(token, end ="")
        
def create_qa_chain(args, files: list[str]):
    llm = ChatOpenAI(model_name='gpt-4-1106-preview', temperature=0, streaming=True, callbacks=[StreamHandler()])
    if args.model_id == "codellama":
        llm = Replicate(streaming=True, model=REPLICATE_CODE_LLAMA_ENDPOINT, model_kwargs={
                        "temperature": 0, "max_length": 5000}, callbacks=[StreamHandler()])
    docs = []
    for f in files:
        for r in parse_resources(f):
            docs.append(Document(page_content=str(r)))
        
    vectordb = Chroma.from_documents(documents=docs,embedding=OpenAIEmbeddings())
    
    template = """Use the following pieces of context to answer the question at the end. Try to answer the question in as much natural language as possible. 
                  {context}
                  Question: {question}
                  Helpful Answer:"""
    
    return ConversationalRetrievalChain.from_llm(llm=llm,
            #retriever=vectordb.as_retriever(),
            retriever=vectordb.as_retriever(search_kwargs={"k":10}),
            # combine_docs_chain_kwargs={"prompt": PromptTemplate.from_template(template)},
            memory=ConversationBufferMemory(memory_key="chat_history",return_messages=True))  
 

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--open-ai-assistant', action='store_true')
    group.add_argument('-m', '--model-id', type=str, choices=["gpt-4", "codellama"])
    
    parser.add_argument('-d', '--infra-dir', type=str,required=True)
    args = parser.parse_args()
    
    files = glob.glob(args.infra_dir + '/**/*.backup', recursive = True)
    
    if args.open_ai_assistant:
        assistant = OpenAIAssistant()
        atexit.register(assistant.cleanup)
        assistant.upload_files(files)
    else:
        qa_chain = create_qa_chain(args, files=files)
        
    
    prompt_session = PromptSession(lexer=PygmentsLexer(SqlLexer))
    query = prompt_session.prompt('Welcome!\nPlease specify what you would like to ask from your terraform templates. >')
    
    while True:
        try:
            while len(query.strip()) == 0:
                query = prompt_session.prompt('> ')
            if args.open_ai_assistant:
                with yaspin(text="generating answer", color="yellow"):
                    user_msg = assistant.create_user_msg(prompt=query)
                    print("\n")
                    print(assistant.get_reply(user_msg.id))
            else:
                qa_chain({"question": query})
                print("")
            query = prompt_session.prompt('> ')
        except KeyboardInterrupt:
            break
        except EOFError:
            break
   


if __name__ == '__main__':
    main()
