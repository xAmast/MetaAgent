from abc import ABC
from typing import Optional, List, Dict

from tenacity import retry, stop_after_attempt, wait_fixed

from metaagent.actions.action_output import ActionOutput
from metaagent.models.openai_llm import OpenAIGPTAPI
from metaagent.utils import OutputParser
from metaagent.logs import logger


class Action(ABC):
    def __init__(self, name: str = '', context=None, llm=None):
        self.name: str = name
        if llm is None:
            llm = OpenAIGPTAPI()
        self.llm = llm
        self.context = context
        self.prefix = ""
        self.profile = ""
        self.desc = ""
        self.content = ""
        self.instruct_content = None

    def set_prefix(self, prefix, profile):
        """Set prefix for later usage"""
        self.prefix = prefix
        self.profile = profile

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def _aask(self, prompt: str, system_msgs: Optional[List[str]] = None) -> str:
        """Append default prefix"""
        if not system_msgs:
            system_msgs = []
        system_msgs.append(self.prefix)
        return self.llm.aask(prompt, system_msgs)

    def _aask_v1(self, prompt: str, output_class_name: str,
                       output_data_mapping: Dict,
                       system_msgs: Optional[List[str]] = None) -> ActionOutput:
        """Append default prefix"""
        if not system_msgs:
            system_msgs = []
        system_msgs.append(self.prefix)
        content = self.llm.aask(prompt, system_msgs)
        logger.debug(content)
        print('######################################')
        print(output_class_name)
        print(output_data_mapping)
        print('######################################')

        output_class = ActionOutput.create_model_class(output_class_name, output_data_mapping)
        parsed_data = OutputParser.parse_data_with_mapping(content, output_data_mapping)
        logger.debug(parsed_data)
        instruct_content = output_class(**parsed_data)
        return ActionOutput(content, instruct_content)

    def run(self, *args, **kwargs):
        """Run action"""
        raise NotImplementedError("The run method should be implemented in a subclass.")