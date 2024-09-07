from flytekit import workflow
from flytekit.extend.backend.base_agent import AgentRegistry
from flyte_agent.agent import CustomAgent
from flyte_agent.task import CustomTask
import datetime as dt


AgentRegistry.register(CustomAgent())


custom_task = CustomTask(
    name="my_custom_task",
    task_config={"config_a": "test", "config_b": 1, "config_c": True},
)


@workflow
def custom_workflow(
    input_a: str, input_b: int, input_c: dt.datetime | None = None
) -> None:
    custom_task(input_a=input_a, input_b=input_b, input_c=input_c)
