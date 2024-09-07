from typing import Any, TypeVar

from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_agent import AsyncAgentExecutorMixin

from flyte_agent.agent import INPUTS, OUTPUTS

C = TypeVar("C")


class CustomTask(AsyncAgentExecutorMixin, PythonTask[C]):
    _TASK_TYPE = "custom_job"

    def __init__(self, name: str, task_config: C, **kwargs: Any) -> None:
        interface = Interface(inputs=INPUTS, outputs=OUTPUTS)
        super().__init__(
            self._TASK_TYPE,
            name,
            task_config=task_config,
            interface=interface,
            **kwargs,
        )

    def get_config(self, settings: SerializationSettings) -> dict[str, str] | None:
        """
        Returns the task config as a serializable dictionary.
        This task config consists of metadata about the custom
        defined for this task.
        """

        # Values need to be strings for serialization
        # Is there a better way to do this? Ie. using the Flyte TypeEngine?
        return {k: str(v) for k, v in self.task_config.items()}
