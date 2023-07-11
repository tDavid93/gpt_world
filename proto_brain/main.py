from kafka import KafkaConsumer
from logging import log

from langchain import LLMMathChain
from langchain.callbacks.manager import (AsyncCallbackManagerForToolRun,
                                         CallbackManagerForToolRun)
from langchain.chat_models import ChatOpenAI
from langchain.experimental.plan_and_execute import (PlanAndExecute,
                                                     load_agent_executor,
                                                     load_chat_planner)
from langchain.tools import BaseTool
from langchain.agents import AgentType, initialize_agent

from kafka import KafkaProducer, KafkaConsumer
import datetime
import json
from kafka.errors import KafkaError
from typing import Optional, Type
from klogger import klogger as kl
import os
from threading import Thread

from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory


class GetSurroundings(BaseTool):
    name = "get_surroundings"
    description = "Get the surroundings of the agent"
    agent_name = ""

    def __init__(self, agent_name):
        super().__init__()
        self.agent_name = agent_name
        kl.klog(agent_name, "init", "GetSurroundings tool loaded")

    def _run(self) -> str:
        response = call_remote_service(self.agent_name, self.name)
        kl.klog(self.agent_name, "get_surroundings", f"response: {response}")
        return response

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("GetSurroundings does not support async")


class TalkToNPC(BaseTool):
    name = "talk_to_npc"
    description = "Talk to an NPC"
    agent_name = ""

    def __init__(self, agent_name):
        super().__init__()
        self.agent_name = agent_name
        kl.klog(agent_name, "init", "TalkToNPC tool loaded")


    def _run(self, query: str) -> str:
        """Talk to an NPC"""
        kl.klog(self.agent_name, "talk_to_npc", f"NOT IMPLEMENTED!!!! query: {query}", level="ERROR")
        raise NotImplementedError("TalkToNPC does not support ")

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("TalkToNPC does not support async")


class MoveToKnownPlaceByName(BaseTool):
    name = "move_to_known_place_by_name"
    description = "Move the agent to the given place"
    agent_name = ""

    def __init__(self, agent_name : str):
        super().__init__()
        self.agent_name = agent_name
        kl.klog(agent_name, "init", "MoveToKnownPlaceByName tool loaded")

    def _run(self, query: str) -> str:
        """Move to a known place by the given name"""
        response = call_remote_service(self.agent_name, self.name, query)
        kl.klog(self.agent_name, self.name, f"response: {response}")
        return response


    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("TalkToNPC does not support async")





class GetHealth(BaseTool):
    name = "get_health"
    description = "Get the health of the agent"
    agent_name = ""

    def __init__(self, agent_name):
        """Get the health of the agent"""
        super().__init__()
        self.agent_name = agent_name
        kl.klog(agent_name, "init", "GetHealth tool loaded")

    def _run(self) -> str:
        """Get the health of the agent"""
        response = call_remote_service( self.agent_name, self.name)
        kl.klog(self.agent_name, self.name, f"response: {response}")
        return response

    def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("GetHealth does not support async")


class GetKnownPlaces(BaseTool):
    name = "get_known_places"
    description = "Get every known places from memory"
    agent_name = ""

    def __init__(self, agent_name):
        super().__init__()
        self.agent_name = agent_name
        kl.klog(agent_name, "init", "GetKnownPlaces tool loaded")

    def _run(self) -> str:
        """Get all known places in memory from the town. Can be used to retrive all the possible places to go to."""
        kl.klog(self.agent_name, self.name, "GetKnownPlaces tool run")
        response = call_remote_service(self.agent_name, self.name)
        return response

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("GetKnownPlace does not support async")




def entity_config_loader(folder):
    # load all the agents in the folder
    configs = {}
    for _, __, files in os.walk(folder):
        for file in files:
            if file.endswith(".json"):
                with open(folder + "/" + file) as f:
                    data = json.load(f)
                    # print(f"data: {data}")
                    try:
                        configs[data["sign"]] = data

                    except KeyError:
                        configs[data["name"]] = data

    return configs


def call_remote_service(name, action="", remote_arg="", srv_address='127.0.0.1:9092'):
    kl.klog(name, "call_remote_service", f"Start remote_call: action: {action}, remote_arg: {remote_arg}, srv_address: {srv_address}", level = "DEBUG")
    producer = KafkaProducer(bootstrap_servers=srv_address)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    topic = f"{name}{timestamp}"
    consumer = KafkaConsumer(
        topic , bootstrap_servers=srv_address, auto_offset_reset='earliest')
    kl.klog(name, "call_remote_service", f"Consumer started: consumer: {consumer}, topic: {topic}", level="DEBUG")
    action = json.dumps(
        {'timestamp': timestamp, 'action': action, 'arg': remote_arg})
    kl.klog(name, "call_remote_service", f"POST action: action: {action}", level="DEBUG")
    future = producer.send(name, action.encode('utf-8'))

    try:
        kl.klog(name, "call_remote_service", f"Try to get metadata: future: {future}", level="DEBUG")
        record_metadata = future.get(timeout=10)
    except KafkaError:
        # Decide what to do if produce request failed...
        kl.klog(name, "call_remote_service", f"KafkaError: {KafkaError}", level="ERROR")
        pass
    kl.klog(name, "call_remote_service", f"record_metadata: {record_metadata}", level="DEBUG")
    for action in consumer:
        return action.value.decode('utf-8')


class NPCBrain():
    model = "gpt-4-0613"
    
    def __init__(self, config):
        # agent base configs
        try:
            kl.klog(config["name"], "init", "Agent initialization started")
            self.config = config
            self.name = config["name"]
            kl.klog(self.name, "init", "Agent name set")
            
            self.memory = call_remote_service(self.name, 'get_memory')
            kl.klog(self.name, "init", "Memory loaded")
            self.model = ChatOpenAI(temperature=0,model=self.model)
            self.tools = [
                GetKnownPlaces(self.name),
                MoveToKnownPlaceByName(agent_name=self.name),
                GetHealth(self.name),
                GetSurroundings(self.name)

            ]
            kl.klog(self.name, "init", "Agent tools loaded")  
            

            self.conv_memory = ConversationBufferMemory()
                        
            
            self.planner = load_chat_planner(self.model)

            self.executor = load_agent_executor(
                self.model, self.tools, verbose=True)

            self.langchain_brain = PlanAndExecute(
                planner=self.planner,memory=self.conv_memory, executor=self.executor, verbose=True)
            kl.klog(config["name"], "init", "Agent brain loaded")
            self.run()
            
        except Exception as e:
            kl.klog(config["name"], "run",
                    f"Agent failed: {e}", level="ERROR")



    
    
    def run(self):
       kl.klog(self.name, "run", "Agent started")
        
       # self.langchain_brain = initialize_agent(
        #    self.tools, self.model, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
       self.langchain_brain.run(self.memory)

if __name__ == "__main__":
    # load the config file
    SERVER_ADDRESS = os.environ.get('KAFKA_SERVER_ADDRESS')
    AGENT_NAME = os.environ.get('AGENT_NAME')
    
    kl.klog("MAIN", "init", "Agent started")
    
    agent_configs = entity_config_loader(folder="config")
#    print(f"agent_configs: {agent_configs}")
    agents = []
    threads = []
    #for agent in agent_configs:
        
        #print(f"agent: {agent_configs[agent]}")
       # agents.append(NPCBrain(agent_configs[agent]))

    for agent in agent_configs:
        #print(f"Starting LLM Agent for : {agent}")
        kl.klog(agent, "init", "Starting LLM Agent thread")
        threads.append(Thread(target=NPCBrain,args=([agent_configs[agent]])))
        threads[-1].start()


    for thread in threads:
        
        thread.join()