import autogen
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

llm_config = {
    "functions": [
        {
            "name": "retrieve_content",
            "description": "Access previous conversations for question answering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Refined message which keeps the original meaning and can be used to retrieve content for question answering.",
                    }
                },
                "required": ["message"],
            },
        },
    ],
    "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST")
}


def retrieve_content(message):
        update_context_case1, update_context_case2 = boss_aid._check_update_context(message)
        if (update_context_case1 or update_context_case2) and boss_aid.update_context:
            boss_aid.problem = message if not hasattr(boss_aid, "problem") else boss_aid.problem
            _, ret_msg = boss_aid._generate_retrieve_user_reply(message)
        else:
            ret_msg = boss_aid.generate_init_message(message)
        return ret_msg if ret_msg else message



boss = autogen.UserProxyAgent(
    name="Boss",
    system_message="The boss who ask questions and give tasks"
)

boss_aid = RetrieveUserProxyAgent(
    name="BossAssistant",
    system_message="Assistant who has content retrieval abilities",
    retrieve_config={
        "task": "qa",
        "docs_path": "data.txt"
    }
)

agent = autogen.AssistantAgent(
    name="SupportAgent",
    system_message="Assistant who has content retrieval abilities for previous conversations",
    llm_config=llm_config,
    function_map={"retrieve_content": retrieve_content}
)

supervisor = autogen.AssistantAgent(
    name="Supervisor",
    system_message="Boss of the support agent. Responsible for checking the qualitiy of the agents answers"
    llm_config=llm_config,
    function_map={"retrieve_content": retrieve_content}
)

groupchat = autogen.GroupChat(
    agents=[boss, supervisor, agent], messages=[]
)

boss.reset()

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": autogen.config_list_from_json("OAI_CONFIG_LIST")})

boss.initiate_chat(
    manager, 
    message="Please answer the customer query: Are there current discounts?"
)