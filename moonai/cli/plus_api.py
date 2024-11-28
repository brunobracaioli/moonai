from typing import Optional
import requests
from os import getenv
from moonai.cli.utils import get_moonai_version
from urllib.parse import urljoin


class PlusAPI:
    """
    This class exposes methods for working with the moonai+ API.
    """

    TOOLS_RESOURCE = "/moonai_plus/api/v1/tools"
    SQUADS_RESOURCE = "/moonai_plus/api/v1/squads"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"moonai-CLI/{get_moonai_version()}",
            "X-moonai-Version": get_moonai_version(),
        }
        self.base_url = getenv("moonai_BASE_URL", "https://app.moonai.dev")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = urljoin(self.base_url, endpoint)
        session = requests.Session()
        session.trust_env = False
        return session.request(method, url, headers=self.headers, **kwargs)

    def login_to_tool_repository(self):
        return self._make_request("POST", f"{self.TOOLS_RESOURCE}/login")

    def get_tool(self, handle: str):
        return self._make_request("GET", f"{self.TOOLS_RESOURCE}/{handle}")

    def publish_tool(
        self,
        handle: str,
        is_public: bool,
        version: str,
        description: Optional[str],
        encoded_file: str,
    ):
        params = {
            "handle": handle,
            "public": is_public,
            "version": version,
            "file": encoded_file,
            "description": description,
        }
        return self._make_request("POST", f"{self.TOOLS_RESOURCE}", json=params)

    def deploy_by_name(self, project_name: str) -> requests.Response:
        return self._make_request(
            "POST", f"{self.SQUADS_RESOURCE}/by-name/{project_name}/deploy"
        )

    def deploy_by_uuid(self, uuid: str) -> requests.Response:
        return self._make_request("POST", f"{self.SQUADS_RESOURCE}/{uuid}/deploy")

    def squad_status_by_name(self, project_name: str) -> requests.Response:
        return self._make_request(
            "GET", f"{self.SQUADS_RESOURCE}/by-name/{project_name}/status"
        )

    def squad_status_by_uuid(self, uuid: str) -> requests.Response:
        return self._make_request("GET", f"{self.SQUADS_RESOURCE}/{uuid}/status")

    def squad_by_name(
        self, project_name: str, log_type: str = "deployment"
    ) -> requests.Response:
        return self._make_request(
            "GET", f"{self.SQUADS_RESOURCE}/by-name/{project_name}/logs/{log_type}"
        )

    def squad_by_uuid(
        self, uuid: str, log_type: str = "deployment"
    ) -> requests.Response:
        return self._make_request(
            "GET", f"{self.SQUADS_RESOURCE}/{uuid}/logs/{log_type}"
        )

    def delete_squad_by_name(self, project_name: str) -> requests.Response:
        return self._make_request(
            "DELETE", f"{self.SQUADS_RESOURCE}/by-name/{project_name}"
        )

    def delete_squad_by_uuid(self, uuid: str) -> requests.Response:
        return self._make_request("DELETE", f"{self.SQUADS_RESOURCE}/{uuid}")

    def list_squads(self) -> requests.Response:
        return self._make_request("GET", self.SQUADS_RESOURCE)

    def create_squad(self, payload) -> requests.Response:
        return self._make_request("POST", self.SQUADS_RESOURCE, json=payload)
