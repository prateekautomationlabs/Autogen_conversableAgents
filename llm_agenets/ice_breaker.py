from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

information = """
Elon Reeve Musk is a businessman known for his key roles in the space company SpaceX and the automotive company Tesla, Inc. He is also known for his ownership of X Corp., a
nd his role in the founding of the Boring Company, xAI, Neuralink, and OpenAI.
"""
if __name__ == "__main__":
    load_dotenv()
    print("Hello LangChain")
    summary_template = """
    given the information {information} about a person I want you to create:
    1. A short summary
    2. two interesting facts about them
    3. Mention in bullet points
    """
    summary_prompt_template = PromptTemplate(
        input_variables=["information"], template=summary_template
    )
   # llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    #llm =ChatOllama(temperature=0, model="mistral")
    llm = ChatOllama(temperature=0, model="llama3")
    #It chains the prompt template with the language model to create a pipeline.
    chain = summary_prompt_template | llm | StrOutputParser()
    # linkedin_data = scrape_linkedin_profile(
    #     linkedin_profile_url="https://www.linkedin.com/in/eden-marco/"
    # )
    res = chain.invoke(input={"information": information})

    print(res)