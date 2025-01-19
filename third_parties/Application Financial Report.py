import autogen
from autogen import ConversableAgent, initiate_chats
import pprint
import streamlit as st

llm_llama_config ={
"model": "llama3",
"base_url": "http://localhost:11434/v1",
"api_key": "ollama"
}

#Goals of our App

#1. Financial and Research task
'''
The first task will be to get  the financial data about the chosen assets and compute some of their performance metrics, second task
will be to investigate reasons for this performance based on news headlines.
'''

from datetime import datetime
date_str = datetime.now().strftime("%Y-%m-%d")
assets = st.text_input("Enter the assets you want to analyze(provide the tickers) :")
hit_button = st.button("Start Analysis")

if hit_button:
    financial_tasks =[
        f"""Today is the {date_str}
        what are the current stock prices for {assets}, and how is the performance over the past 6 months in terms of percentage change ?
        Start by retrieving the full name of each stack and use it for all future requests.
        Prepare a figure of the normalized price of these stocks and save it to a file named normalized_prices.png.
        Include information about, if applicable 
        * P/E ratio
        * P/B ratio
        * Forward P/E
        * Dividends
        *Price to book
        *Debt/Eq
        *ROE
        *Analyze the correlation between the stocks.
        Do not use solution that requires an API key.
        If some of the data does not make sense, such a price of 0, change the query and retry.
    """,
        """Investigate possible reasons ofthe stock performance leveraging market news headlines from Bing News or Google News.
        Retrieve the news headlines using python and return them. Use the full name stocks to retrieve headlines.Retrieve 
        atleast 10 headlines per stock.Do not use solution that requires an API key.
        """
    ]

    financial_assistant = autogen.AssistantAgent(
        name ="Financial_Assistant",
        llm_config=llm_llama_config
    )

    research_assistant = autogen.AssistantAgent(
        name ="Researcher",
        llm_config=llm_llama_config
    )

    """
    At the end of this task, we will have price data, 
    performance metrics and a chart that shows normalized price evolution for the specified stocks.
    
    """

    writing_tasks =[
    """
    Develop an engaging financial report using all information provided , include the normalized_prices.png figure, and others figures if provided.
    Mainly rely on the information provided.
    Create a table comparing all the fundamental ratios and data.
    Provide comments and description of all the fundamental ratios and data.
    Compare the stocks, consider their correlation and risks, provide a comparative analysis of the stocks.
    Provide summary of the recent news about each stock.
    Ensure you comment and summarize the recent news headlines for each stock, provide a comprehensive analysis of the news.
    Provide connections between the news headlines provided and the fundamental ratios.
    Provide an analysis of possible future scenarios.
    """
    ]
    writer = autogen.AssistantAgent(
        name ="Writer",
        llm_config=llm_llama_config,
        system_message="""
        you are a professional writer , known for your insightful and engaging finance reports.
        You transform complex concepts into compelling narratives.
        Include all metrics provided to you as context in your analysis.
        Only answer with the financial report written in markdown directly, do not include a markdown language blocks indicator.
        Only return your final work without any additional comments.
        """
    )

    critic = autogen.AssistantAgent(
        name ="Critic",
        llm_config=llm_llama_config,
        system_message="""
        You are a professional critic. You review the work of the writer and provide constructive feedback to improve the quality of the content.
        """,
        is_termination_msg=lambda x:x.get("content","").find("TERMINATE")>=0
    )

    legal_reviewer = autogen.AssistantAgent(
        name ="Legal_Reviewer",
        llm_config=llm_llama_config,
        system_message="""
        You are a legal reviewer,known for your ability to ensure that content is legally complaint
        and free from any potential legal issues.
        Make sure your suggestion is concise (within 3 bullet points), concrete and to the point.
        Begin the review by stating your role.
        """,
        is_termination_msg=lambda x:x.get("content","").find("TERMINATE")>=0
    )

    consistency_reviewer = autogen.AssistantAgent(
        name ="Consistency_Reviewer",
        llm_config=llm_llama_config,
        system_message="""
        You are a consistency reviewer,known for your ability to ensure that content is cosntistent throughout the report. 
        Refer numbers and data in the report to determine which version should be chosen in case of contradictions.
        Make sure your suggestion is concise (within 3 bullet points), concrete and to the point.
        Begin the review by stating your role.
        """,
        is_termination_msg=lambda x:x.get("content","").find("TERMINATE")>=0
    )

    textalignment_reviewer = autogen.AssistantAgent(
        name ="TextAlignment_Reviewer",
        llm_config=llm_llama_config,
        system_message="""
        You are a text data alignment reviewer,known for your ability to ensure that the meaning of the written content is aligned
        with the numbers written in the text.
        You must ensure that the text clearly describes the numbers in the text. 
        Make sure your suggestion is concise (within 3 bullet points), concrete and to the point.
        Begin the review by stating your role.
        """,
        is_termination_msg=lambda x:x.get("content","").find("TERMINATE")>=0
    )

    completion_reviewer = autogen.AssistantAgent(
        name ="Completion_Reviewer",
        llm_config=llm_llama_config,
        system_message="""
        You are a content completion reviewer,known for your ability to ensure that the financial reports contain all the required elements.
        You always verify that the report contains: a news report about each asset,
        a description of different ratios and prices,
        a description of possible future scenarios, a table comparing fundamental ratios and atleast a single figure.
        Make sure your suggestion is concise (within 3 bullet points), concrete and to the point.
        Begin the review by stating your role.
        """,
        is_termination_msg=lambda x:x.get("content","").find("TERMINATE")>=0
    )

    meta_reviewer = autogen.AssistantAgent(
        name ="Meta_Reviewer",
        llm_config=llm_llama_config,
        system_message="""
        You are a meta reviewer,you aggregate and review the work of the other reviewers
        and give a final suggestion on the content.
        """,
        is_termination_msg=lambda x:x.get("content","").find("TERMINATE")>=0
    )

    exporting_task =[""" Save the blogpost and only the blogpost to a .md file using a python script."""]
    export_assistant =autogen.AssistantAgent(
        name = "Exporter",
        llm_config=llm_llama_config,
    )

    user_proxy_auto = autogen.UserProxyAgent(
        name="user_proxy_agent",
        human_input_mode="NEVER",
        is_termination_msg=lambda x:x.get("content","") and x.get("content","").rstrip().endswith("TERMINATE"),
        code_execution_config={
            "last_n_messages":3,
            "work_did":"coding",
            "use_docker": False
        }
    )

    # Agentic Flow
    #Nested chat flow for writing the blogpost/report
    #This chat will be triggered when the writer will contact the critic
    def reflection_message(recipient, messages, sender, config):
        return f''' Review the following content.
    \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

    review_chats = [
        {
            "recipient": legal_reviewer, "message": reflection_message,
            "summary_method": "reflection_with_llm",
            "summary_args":{
                "summary_prompt": "Return review into a JSON object only:"
                "{'Reviever':'','Review':''}.",},
            "max_turns":1},
        {
            "recipient": textalignment_reviewer, "message": reflection_message,
            "summary_method": "reflection_with_llm",
            "summary_args":{
                "summary_prompt": "Return review into a JSON object only:"
                "{'Reviever':'','Review':''}.",},
            "max_turns":1},
    {
            "recipient": consistency_reviewer, "message": reflection_message,
            "summary_method": "reflection_with_llm",
            "summary_args":{
                "summary_prompt": "Return review into a JSON object only:"
                "{'Reviever':'','Review':''}.",},
            "max_turns":1},
    {
            "recipient": completion_reviewer, "message": reflection_message,
            "summary_method": "reflection_with_llm",
            "summary_args":{
                "summary_prompt": "Return review into a JSON object only:"
                "{'Reviever':'','Review':''}.",},
            "max_turns":1},
    {
            "recipient": meta_reviewer, "message": reflection_message,
            "message":"Aggregate the feedback from all reviewers and give final suggestions on the writing",
            "max_turns":1}
            ]

    critic.register_nested_chats(
        review_chats, trigger=writer
    )

    with st.spinner("Agent Working on the analysis..."):
        chat_results= autogen.initiate_chats(
            [
        {
                "sender": user_proxy_auto,
                "recipient": financial_assistant, "message": financial_tasks[0],
                "summary_method": "reflection_with_llm",
                "silent": False,
                "summary_args":{
                    "summary_prompt": "Return the stock prices of the stocks, their performance and all other metrics"
                                      "into a JSON object only. Provide the name of all figure files created. Provide full name of each stock."},
                   "clear_history": False,
                   "carryover": "Wait for confirmation of code execution before terminating the conversation. Verify that the "
                                "data is not completely composed of NaN values. Reply TERMINATE in the end when everything is done."
        },
        {
                "sender": user_proxy_auto,
                "recipient": research_assistant, "message": financial_tasks[1],
                "summary_method": "reflection_with_llm",
                "silent": False,
                "summary_args":{
                        "summary_prompt": "Provide the news headlines as a paragraph for each stock, be precise but do not consider news events that are vague,return results"
                                      "into a JSON object only."},
                   "clear_history": False,
                   "carryover": "Wait for confirmation of code execution before terminating the conversation.Reply TERMINATE in the end when everything is done."
        },

                {
                    "sender": critic,
                    "recipient": writer, "message": writing_tasks[0],
                    "carryover": "I want to include a figure and a table of the provided data in the financial report.",
                    "max_turns":2,
                    "summary_method": "last_msg",
                },
        {
                    "sender": user_proxy_auto,
                    "recipient": export_assistant, "message": exporting_task[0],
                    "carryover": "Wait for confirmation of code execution before terminating the conversation.Reply TERMINATE in the end when everything is done."

                }

            ]


        )

        st.image("./coding/normalized_prices.png")
        st.markdown(chat_results[1-1].chat_history[-1]["content"])