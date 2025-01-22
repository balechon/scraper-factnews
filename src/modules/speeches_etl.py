import pandas as pd
import json
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from src.modules.millercenter_speeches import download_data
from langchain_openai import ChatOpenAI
from src.modules.translator import llm_translate
load_dotenv()

# def llm_translator(text) -> str:
#     llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)
#     text_translated = llm_translate(llm, text)
#     return text_translated

class MillercenterSpeeches:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        if self.file_path.is_file():
            return pd.read_json(self.file_path)
        else:
            return pd.DataFrame(download_data(self.file_path))

    def __getattr__(self, name):
        return getattr(self.data, name)

class TedSpeeches:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        if self.file_path.is_file():
            return pd.read_csv(self.file_path)
        else:
            raise FileNotFoundError(f"File not found: {self.file_path}")

    def __getattr__(self, name):
        return getattr(self.data, name)

class SpeechesETL:
    def __init__(self, data_path: Path, output_path: Path):
        self.data_path = data_path
        self.output_path = output_path
        self.millercenter = MillercenterSpeeches(self.data_path / "millercenter_speeches.json")
        self.ted = TedSpeeches(self.data_path / "ted_speech_clean.csv")
        self.output_file = self.output_path / "Speeches_corpus.json"
        self.progress_file = self.output_path / "translation_progress.json"
        self.final_data = None
        self.load_progress()

    def preprocess(self):
        millercenter_data = self.millercenter.data[['title', 'transcript']]
        millercenter_data['origin'] = 'us politics speeches'
        ted_data = self.ted.data[['title', 'transcript']]
        ted_data['origin'] = 'ted talks'
        self.final_data = pd.concat([millercenter_data, ted_data]).reset_index(drop=True)

    def load_progress(self):
        if self.output_file.is_file():
            self.final_data = pd.read_json(self.output_file, lines=True)
        else:
            self.preprocess()
        
        if self.progress_file.is_file():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {"last_translated_index": -1}

    def save_progress(self, index):
        self.progress["last_translated_index"] = index
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f)

    def translate(self):
        if "translated_speech" not in self.final_data.columns:
            self.final_data["translated_speech"] = None

        start_index = self.progress["last_translated_index"] + 1
        
        for i in tqdm(range(start_index, len(self.final_data))):
            transcript = self.final_data.loc[i, "transcript"]
            llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)
            translated = llm_translate(llm, transcript)
            self.final_data.loc[i, "translated_speech"] = translated
            
            # Guardar progreso cada 10 traducciones
            if i % 10 == 0:
                self.final_data.to_json(self.output_file, orient="records", lines=True)
                self.save_progress(i)

        # Guardar el progreso final
        self.final_data.to_json(self.output_file, orient="records", lines=True)
        self.save_progress(len(self.final_data) - 1)

