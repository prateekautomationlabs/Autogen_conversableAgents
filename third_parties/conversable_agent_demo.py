from autogen import ConversableAgent
import pprint

llm_llama_config ={
"model": "llama3",
"base_url": "http://localhost:11434/v1",
"api_key": "ollama"
}

# Single chat conversation
# agent = ConversableAgent(
#     name="chatbot",
#     llm_config=llm_llama_config,
#     human_input_mode="NEVER"
# )
#
# reply =agent.generate_reply(
#     messages=[{"content":"Tell me a fun fact about money","role":"user"}]
# )
#
# print(reply)


# Multi-agent conversation
bret = ConversableAgent(
    name="bret",
    llm_config=llm_llama_config,
    system_message="Your name is Bret and you are a stand-up comedian in a two-person comedy show."
                   "When you are ready to end the conversation, say 'I gotta go'.",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg:  "I gotta go" in msg["content"]
)

jasmine = ConversableAgent(
    name="jasmine",
    llm_config=llm_llama_config,
    system_message="Your name is Jasmine and you are a stand-up comedian in a two-person comedy show."
    "When you are ready to end the conversation, say 'I gotta go'.",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg:  "I gotta go" in msg["content"]
)
#and now we have our agents we can start a chat between them. This time we will use initiate_chat instead of generate_reply.
#This function will require a receiver and an initiation message.We will also specify a number of turns after what the
# conversation will stop
result = bret.initiate_chat(jasmine,message="I'm Bret. Jasmine, can you share interesting facts about money.",
                            summary_method="reflection_with_llm", #can be "last_message" (Default) or "reflection_with_llm"
                            summary_prompt="Summarize the conversation so far" #we  specify the prompt used to summarize the chat
                            )

#exloring the Chat results

#Printing chat history, this gives us whole exchange in a structured format that can be exported.
#pprint.pprint(result.chat_history)

#Summary of how much this chat has cost us.
pprint.pprint(result.cost)

print("Printing summary is: ")
#print the last message
pprint.pprint(result.summary)