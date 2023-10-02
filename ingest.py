from typing import Any, Dict

import streamlit as st
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from pydantic import BaseModel


class Config(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 0
    docs_dir: str = "docs/"
    docs_glob: str = "**/*.md"


class DocumentProcessor:
    def __init__(self, config: Config):
        self.loader = DirectoryLoader(config.docs_dir, glob=config.docs_glob)
        self.text_splitter = CharacterTextSplitter(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key="OPENAI_API_KEY")


def run():
    config = Config()
    doc_processor = DocumentProcessor(config)
    result = doc_processor.process()
    return result


if __name__ == "__main__":
    run()
