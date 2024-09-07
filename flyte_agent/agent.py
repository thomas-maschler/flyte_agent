import datetime as dt
import io
from dataclasses import _MISSING_TYPE, Field, dataclass
from typing import Any, Optional


from flyteidl.core.execution_pb2 import TaskExecution
from flytekit import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.extend.backend.base_agent import (
    AsyncAgentBase,
    Resource,
    ResourceMeta,
)
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate
from flytekit.types.structured.structured_dataset import (
    StructuredDataset,
)

import pandas as pd


INPUTS: dict[str, Any] = {
    "input_a": str,
    "input_b": int,
    "input_c": dt.datetime | None,
}

OUTPUTS = {"tasks": pd.DataFrame}


class AsyncJob(object):

    def __init__(self, config_a: str, config_b: int, config_c: bool) -> None:
        """Instantiate job using Task Config"""
        self.config_a = config_a
        self.config_b = config_b
        self.config_c = config_c

    def schedule_job(
        self, input_a: str, input_b: int, input_c: dt.datetime | None
    ) -> dt.datetime:
        """Schedule job with User input values"""
        return dt.datetime.now()

    def get_job_status(self, start_datetime: dt.datetime) -> str:
        """Get job status"""

        runtime = (dt.datetime.now() - start_datetime).seconds
        if runtime < 5:
            return "QUEUED"
        elif runtime < 10:
            return "SCHEDULED"
        elif runtime < 15:
            return "RUNNING"
        else:
            return "SUCCEEDED"

    def get_results(self) -> pd.DataFrame:
        """Fetch results from successful job"""
        return pd.DataFrame(
            {
                "a": [self.config_a],
                "b": [self.config_b],
                "c": [self.config_c],
            }
        )

    def cleanup(self) -> None:
        pass


@dataclass
class CustomMetadata(ResourceMeta):
    """
    This is the metadata for the job. For example, the id of the job.
    """

    start_datetime: dt.datetime
    config_a: str
    config_b: int
    config_c: bool


class CustomAgent(AsyncAgentBase):

    def __init__(self) -> None:
        super().__init__(task_type_name="custom_job", metadata_type=CustomMetadata)

    def create(
        self,
        task_template: TaskTemplate,
        inputs: Optional[LiteralMap] = None,
        **kwargs: Any,
    ) -> CustomMetadata:
        """Create the job"""

        config: dict[str, str] = task_template.config

        ctx = FlyteContextManager.current_context()
        input_values: dict[str, Any] = TypeEngine.literal_map_to_kwargs(
            ctx,
            inputs,
            INPUTS,
        )

        # Values come as strings and to be deserialized.
        # Is there a better way to do this? Ie. using the Flyte TypeEngine?
        config_a = config.get("config_a")
        config_b = int(config.get("config_b"))
        config_c = bool(config.get("config_c"))

        async_job = AsyncJob(config_a=config_a, config_b=config_b, config_c=config_c)
        start_datetime = async_job.schedule_job(**input_values)

        return CustomMetadata(
            start_datetime=start_datetime,
            config_a=config_a,
            config_b=config_b,
            config_c=config_c,
        )

    def get(self, resource_meta: CustomMetadata, **kwargs: Any) -> Resource:
        """Get the job status and results"""

        ctx = FlyteContextManager.current_context()

        async_job = AsyncJob(
            resource_meta.config_a, resource_meta.config_b, resource_meta.config_c
        )

        status = async_job.get_job_status(resource_meta.start_datetime)


        # set phase based on job status
        if status == "QUEUED":
            phase = TaskExecution.QUEUED

        elif status == "SCHEDULED":
            phase = TaskExecution.WAITING_FOR_RESOURCES

        elif status == "RUNNING":
            phase = TaskExecution.RUNNING

        elif status == "SUCCEEDED":
            phase = TaskExecution.SUCCEEDED

        else:
            phase = TaskExecution.UNDEFINED


        # set outputs based on job status
        if status == "SUCCEEDED":
            results = async_job.get_results()
        else:
            results = pd.DataFrame()

        outputs = TypeEngine.dict_to_literal_map(
            ctx, {"tasks": StructuredDataset(dataframe=results)}
        )

        return Resource(
            phase=phase, message=f"Batch job status: {status}", outputs=outputs
        )

    def delete(self, resource_meta: CustomMetadata, **kwargs: Any) -> None:
        """Delete the job"""
        async_job = AsyncJob(
            resource_meta.config_a, resource_meta.config_b, resource_meta.config_c
        )
        async_job.cleanup()
