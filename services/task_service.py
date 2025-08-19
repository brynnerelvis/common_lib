from http import HTTPStatus
from typing import Any, Dict, List

from common_lib.requests_utils import ApiClient, ResponseAsserter


class TaskService:
    """
    ToDoList Services API's task endpoints.
    """

    def __init__(self, client: ApiClient):
        self.client = client


    def create_task(
        self,
        payload: Dict[str, Any],
        expected: int = HTTPStatus.OK,
    ):
        """PUT /create-task"""
        return self.client.put("/create-task", json=payload, expected=expected)

    def get_task(
        self,
        task_id: str,
        expected: int = HTTPStatus.OK,
    ):
        """GET /get-task/{task_id}"""
        return self.client.get(f"/get-task/{task_id}", expected=expected)

    def update_task(
        self,
        payload: Dict[str, Any],
        expected: int = HTTPStatus.OK,
    ):
        """PUT /update-task"""
        return self.client.put("/update-task", json=payload, expected=expected)

    def delete_task(
        self,
        task_id: str,
        expected: int = HTTPStatus.OK,
    ):
        """DELETE /delete-task/{task_id}"""
        return self.client.delete(f"/delete-task/{task_id}", expected=expected)

    def get_list_tasks(
        self,
        user_id: str,
        expected: int = HTTPStatus.OK,
    ):
        """GET /list-tasks/{user_id}"""
        return self.client.get(f"/list-tasks/{user_id}", expected=expected)


    @staticmethod
    def assert_task_contract(task: Dict[str, Any]):
        """Ensure a single task object has required fields."""
        required = {"task_id", "user_id", "content", "is_done"}
        missing = required - set(task.keys())
        assert not missing, f"Task missing fields: {missing}. Got keys: {list(task.keys())}"

        assert isinstance(task["task_id"], str), "task_id must be str"
        assert isinstance(task["user_id"], str), "user_id must be str"
        assert isinstance(task["content"], str), "content must be str"
        assert isinstance(task["is_done"], bool), "is_done must be bool"

    @staticmethod
    def assert_create_response(resp):
        """
        Validate the shape of a create-task response.
        Returns parsed JSON for convenience.
        """
        data = ResponseAsserter.json_has_keys(resp, "task")
        TaskService.assert_task_contract(data["task"])
        return data

    @staticmethod
    def assert_get_response(resp):
        """
        Validate the shape of a get-task response.
        """
        data = ResponseAsserter.json(resp)
        TaskService.assert_task_contract(data)
        return data

    @staticmethod
    def assert_list_response(
        resp,
        expected_user_id: str | None = None,
        expected_len: int | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Validate the shape of a list-tasks response and optionally
        assert user_id and length constraints.
        """
        data = ResponseAsserter.json_has_keys(resp, "tasks")
        tasks = data["tasks"]
        assert isinstance(tasks, list), f"'tasks' must be a list, got {type(tasks)}"

        for t in tasks:
            TaskService.assert_task_contract(t)
            if expected_user_id is not None:
                assert t["user_id"] == expected_user_id, "Listed task belongs to another user"

        if expected_len is not None:
            assert len(tasks) == expected_len, f"Expected {expected_len} tasks, got {len(tasks)}"

        return tasks
