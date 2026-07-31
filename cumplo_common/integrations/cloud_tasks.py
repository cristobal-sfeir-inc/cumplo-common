"""Integration wrapper for Google Cloud Tasks."""

import json
from datetime import datetime
from typing import Annotated

import arrow
from google.cloud.tasks import CloudTasksClient, CreateTaskRequest, HttpMethod, HttpRequest, OidcToken, Task
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp

from cumplo_common.utils.constants import LOCATION, PROJECT_ID, SERVICE_ACCOUNT_EMAIL


class CloudTasks:
    """Integration with Google Cloud Tasks."""

    @staticmethod
    def create_task(  # noqa: PLR0913, PLR0917
        url: str,
        queue: str,
        payload: dict,
        task_id: str,
        headers: dict[str, str] | None = None,
        dispatch_deadline: int | None = None,
        schedule_time: datetime | None = None,
        http_method: Annotated[int, HttpMethod] = HttpMethod.POST,
        *,
        is_internal: bool = True,
    ) -> Task:
        """
        Create an HTTP POST task with a JSON payload.

        Args:
            url (str): Destination URL
            queue (str): Queue name
            payload (dict): Request JSON payload
            headers (dict[str, str], optional): Request headers. Defaults to None.
            task_id (str): Task identifier
            dispatch_deadline (int | None, optional): Seconds until the task is dispatched. Defaults to None.
            schedule_time (datetime | None, optional): Time at which the task will be scheduled. Defaults to None.
            http_method (Annotated[int, HttpMethod], optional): HTTP method to use. Defaults to HttpMethod.POST.
            is_internal (bool, optional): Whether the task is intended for internal use. Defaults to True.

        Returns:
            Task: A unit of scheduled work

        """
        client = CloudTasksClient()

        headers = headers or {}
        task_id = f"{task_id}-{str(arrow.utcnow().timestamp()).replace('.', '')}"
        name = client.task_path(PROJECT_ID, LOCATION, queue, task_id)

        http_request = HttpRequest(
            url=url,
            http_method=http_method,
            body=json.dumps(payload).encode(),
            headers={**headers, "Content-type": "application/json"},
        )

        if is_internal:
            http_request.oidc_token = OidcToken(service_account_email=SERVICE_ACCOUNT_EMAIL)

        task = Task(name=name, http_request=http_request)

        if schedule_time is not None:
            timestamp = Timestamp()
            timestamp.FromDatetime(schedule_time)
            task.schedule_time = timestamp

        if dispatch_deadline is not None:
            duration = Duration()
            duration.FromSeconds(dispatch_deadline)
            task.dispatch_deadline = duration

        parent = client.queue_path(project=PROJECT_ID, location=LOCATION, queue=queue)
        task_request = CreateTaskRequest(parent=parent, task=task)
        return client.create_task(request=task_request)
