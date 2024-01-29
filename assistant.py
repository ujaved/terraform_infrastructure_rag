from openai import OpenAI
import os
import shutil

import time

class OpenAIAssistant:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.assistant = self.client.beta.assistants.create(
            name="Terraform Tutor",
            instructions="Your job is to answer questions in natural language related to the attached terraform resources.",
            model="gpt-4-1106-preview",
            tools=[{"type": "retrieval"}],
        )
        self.thread = self.client.beta.threads.create()
        self.file_ids = {}
        
    def wait_on_run(self, run):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run
        
    def cleanup(self):
        for f_id, filename in self.file_ids.items():
            self.client.files.delete(file_id=f_id)
            os.remove(filename)
        self.client.beta.assistants.delete(assistant_id=self.assistant.id)

    def upload_files(self, filenames: list[str]):
        for filename in filenames:
            # rename file to have .json extension
            new_filename = filename.split(".")[0] + ".json"
            shutil.copy(filename, new_filename)
            
            f = self.client.files.create(file=open(new_filename,"rb"),purpose="assistants")
            self.file_ids[f.id] = new_filename
        self.assistant = self.client.beta.assistants.update(self.assistant.id,file_ids=list(self.file_ids.keys()))
        
    def create_user_msg(self, prompt: str):
        m = self.client.beta.threads.messages.create(thread_id=self.thread.id,role="user",content=prompt)
        run = self.client.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.assistant.id)
        self.wait_on_run(run)
        return m
    
    def get_reply(self, after_msg_id) -> str:
        m = self.client.beta.threads.messages.list(thread_id=self.thread.id, after=after_msg_id, order="asc")
        return m.data[0].content[0].text.value
        