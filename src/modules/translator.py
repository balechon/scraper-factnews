from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

import pandas as pd
from dotenv import load_dotenv
load_dotenv()

class SpeechOutputParser(BaseModel):
    translate: str = Field(description="Translated speech")

class GeneratorOutputParser(BaseModel):
    translate: str = Field(description="Prompt generado")





def llm_translate(llm, text):
    template = """
Translate the following text from English to Spanish. 
Ensure that you maintain the original meaning, tone, and style of the text. 
Adapt idiomatic and cultural expressions when necessary to sound natural in Spanish. 
If there are any technical or specialized terms, provide the most accurate and commonly accepted translation. 
Return ONLY the translation, without any additional comments, explanations, or attributions.
Here's the text to translate:

{speech}

{format_instructions}
    """
    # text= text[:1000]
    parser = JsonOutputParser(pydantic_object=SpeechOutputParser)
    promt = PromptTemplate(template=template, input_variables=["speech"],partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = promt|llm|parser
    response = chain.invoke({"speech":text})
    return response['translate']

# if __name__=="__main__":
#     # llm = Ollama(model="llama3",temperature=0)

#     df = pd.read_json("data/Speeches_corpus.json")
    
#     seed = 0
#     df_sample = df.sample(random_state=seed, n=2)
#     df_sample["translated_speech"] = df_sample["transcript"].apply(lambda x: llm_translate(llm, x))  
#     df_sample.to_excel("data/Speeches_corpus_translated.xlsx", index=False) 


def llm_promt_generator(llm, description, autor_profile, tags):
    template = """Actúa como un experto en simplificar y reformular ideas. Te proporcionaré la descripción de una conferencia o charla, que puede incluir nombres de oradores y sus profesiones. Tu tarea es transformar esa descripción en una solicitud en español simple y directa para crear un discurso, como si estuvieras pidiéndole a un asistente de IA que genere el contenido.

Sigue estas pautas:
1. Identifica los temas principales de la descripción.
2. Si se mencionan nombres de personas, ignóralos y céntrate en su profesión o área de experiencia.
3. Resume los temas principales en una o dos frases concisas.
4. Formula la solicitud como "Crea un discurso al estilo TED-Talk que suene como si fuera dado por un experto en [profesión o área de experiencia] y que trate sobre [temas principales]".
5. Si hay aspectos específicos o enfoques mencionados en la descripción, inclúyelos brevemente.
6. Mantén la solicitud breve y al grano, idealmente en no más de 5-6 frases.

Descripción de la conferencia:
{text}

Profesión del autor (si se menciona):
{profession}

Tags:
{tags}

Transforma esta descripción en una solicitud simple para crear un discurso, enfocándote en la experiencia relevante y los temas principales.
{format_instructions}
"""	
    parser = JsonOutputParser(pydantic_object=GeneratorOutputParser)
    promt = PromptTemplate(template=template, input_variables=["text", "profession", "tags"],partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = promt|llm|parser
    response = chain.invoke({"text":description, "profession":autor_profile, "tags":tags})
    return response['translate']