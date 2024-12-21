import os
from dotenv import load_dotenv
from autogen.agentchat.contrib.retrieve_assistant_agent import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent


load_dotenv()


config_list_claude = [
    {
        "model": "claude-3-5-sonnet-20240620",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "api_type": "anthropic",
    }
]

llm_config = {
    "request_timeout": 600,
    "config_list": config_list_claude,
    "temperature": 0
}

customer_proxy_agent = autogen.ConversableAgent(
    name="customer_proxy_agent",
    llm_config=False,
    code_execution_config=False,
    human_input_mode="ALWAYS",
    is_termination_msg=lambda msg: "terminate" in msg.get("content").lower(),
)


onboarding_agent = autogen.ConversableAgent(
    name="onboarding_coordinator_agent",
    system_message="You are a banking onboarding coordinator agent and you need to get the required information from a customer that wants to open an account"
                    " You need to get his firstt name, his last name, his address, his birth date, his nationality, his residence permit."
                    "Once you have all the information required please reply terminate",
    llm_config=llm_config,
    human_input_mode="NEVER",
    code_execution_config=False
)




import chainlit as cl

@cl.on_chat_start
async def main():
    cl.user_session.set("user_id", str(uuid.uuid4()))
    cl.user_session.set("session_id", str(uuid.uuid4()))
    cl.user_session.set("chat_history", [])
    await cl.Message(
            content="Welcome to the interactive Multi-Agent system. Type 'quit' to exit.",
        ).send()

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("session_id")
    chat_history = cl.user_session.get("chat_history", [])
    user_input=message.content
    if user_input.lower() == 'quit':
            print("Exiting the program. Goodbye!")
            sys.exit()
    response= asyncio.run(handle_request(orchestrator, user_input, user_id, session_id, chat_history))
    # Send a response back to the user
    await cl.Message(
        content=response,
    ).send()



    



