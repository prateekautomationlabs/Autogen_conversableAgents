from autogen import ConversableAgent, initiate_chats
import pprint

llm_llama_config ={
"model": "llama3",
"base_url": "http://localhost:11434/v1",
"api_key": "ollama"
}


#Agents definitions

#1. Onboarding Personal Information Agent
onboarding_personal_information_agent = ConversableAgent(
    name="Onboarding_Personal_Information_Agent",
    llm_config=llm_llama_config,
    system_message='''You are a helpful customer onboarding agent.
    you work for phone provider called ACME.
    Your job is to gather the customer name and location.
    Do not ask for any other information, only asks about the customer's name and location.
    After the customer gives you their name and location, repeat them
    and thank the user, and ask the user to answer with TERMINATE to move on to describing their issue.
        
    ''',
    human_input_mode="NEVER",
    is_termination_msg=lambda msg:  "terminate" in msg.get("content").lower()
)

# 2. Onboarding Personal Information Agent
onboarding_issue_agent = ConversableAgent(
    name="Onboarding_Issue_Agent",
    llm_config=llm_llama_config,
    system_message='''You are a helpful customer onboarding agent.
    you work for phone provider called ACME.
    You are here to help new customers get started with our product.
    Your job is to gather the product the customer use and the issue they currently have with the product.
    Do not ask for any other information.
    After the customer describes the issue, repeat it and add
    "Please answer with TERMINATE if I have correctly understood your issue."
    ''',
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "terminate" in msg.get("content").lower()
)

#3. Customer Engagement Agent
customer_engagement_agent = ConversableAgent(
    name="Customer_Engagement_Agent",
    llm_config=llm_llama_config,
    system_message='''You are a helpful customer service agent.
    Your job is to gather customer's preferences on new topics.
    You are here to provide fun and useful information to your customers based on their preferences.
    This include fun facts, jokes or interesting stories.
    Make sure to make it engaging and fun!
    Return 'TERMINATE' when you are done."
    ''',
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "terminate" in msg.get("content").lower()
)

#It is not a LLM(llm_config=False), it will have human_input_mode="ALWAYS", which means You will play the role of this agent.
#You will be the customer through this agent.
customer_proxy_agent = ConversableAgent(
    name="customer_proxy_agent",
    llm_config=False,
    code_execution_config=False,
    human_input_mode="ALWAYS"
)

#Chat orchestration

#Onboarding agent with Customer
chats = []
chats.append(
    {
"sender": onboarding_personal_information_agent,
"recipient": customer_proxy_agent,
"message":
    "Hello, I am here to help you with your onboarding process."
        "Could you please tell me your name and location?",
        "summary_method":"reflection_with_llm",
        "summary_args": {
    "summary_prompt": "Return the customer information"
    "into as JSON object only:"
    "{'name':'', 'location':''}",
},
"clear_history": True
    }
)

#Issue agent with Customer

chats.append(
    {
"sender": onboarding_issue_agent,
"recipient": customer_proxy_agent,
"message":
    "Great ! Could you please tell me the product you use and the issue you currently have with it?",
    "summary_method":"reflection_with_llm",
    "clear_history": False
    }
)

#Engagement agent with Customer

chats.append(
    {
"sender": customer_engagement_agent,
"recipient": customer_proxy_agent,
"message":
    "While we are waiting for a human agent to take over and help you to solve your issue, "
    "can you tell me more about how you use our product or some topics intresting for you?",
    "max_turn": 2,
    "summary_method":"reflection_with_llm"
    }
)

print(chats)

#Initiate sequential chat
chat_results = initiate_chats(chats)
