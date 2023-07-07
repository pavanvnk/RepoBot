import os
import subprocess

from langchain.vectorstores import DeepLake
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader, NotebookLoader

repo_path = os.path.join(os.getcwd(), "cloned_repo")

def load_to_db(repo_link, db_path, al_token, embeddings):
    subprocess.run(['git', 'clone', repo_link, repo_path])
    docs = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in files:
            if filename.startswith('.'):
                continue
            if filename == 'package-lock.json':
                continue
            file_path = os.path.join(root, filename)
            try:
                if file_path.endswith('.ipynb'):
                    loader = NotebookLoader(file_path)
                else:
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs.extend(loader.load_and_split())
            except Exception as e:
                pass
            
    code_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=0)
    code = code_splitter.split_documents(docs)

    db = DeepLake(
        dataset_path=db_path,
        token=al_token,
        embedding_function=embeddings
    )

    db.add_documents(code)