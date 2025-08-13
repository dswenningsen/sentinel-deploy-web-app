"""SharePoint Stuff"""

import subprocess
import requests


class GraphClient:
    """
    A client for interacting with the Microsoft Graph API.
    """

    def __init__(self):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.token = self.get_graph_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get_graph_token(self):
        """
        Retrieves a token for accessing the Microsoft Graph API using a PowerShell script.
        """
        powershell_command = "GetGraphToken.ps1"

        result = subprocess.run(
            ["powershell", "-File", powershell_command],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def get_me(self):
        """
        Retrieves the current user's information from the Microsoft Graph API.
        """
        url = f"{self.base_url}/me"
        response = requests.get(url, headers=self.headers, timeout=300)
        response.raise_for_status()
        return response.json()

    def get_site_id(self, hostname, site_path):
        """
        Retrieves the site ID for a given hostname and site path.
        """
        url = f"{self.base_url}/sites/{hostname}:/sites/{site_path}?$select=id"
        response = requests.get(url, headers=self.headers, timeout=300)
        response.raise_for_status()
        return response.json().get("id").split(",")[1]

    def get_list(self, site_id, list_name):
        """
        Retrieves all lists from a specified SharePoint site.
        """
        url = f"{self.base_url}/sites/{site_id}/lists/{list_name}"
        response = requests.get(url, headers=self.headers, timeout=300)
        response.raise_for_status()
        return response.json()  # .get("value", [])

    def get_list_items(self, site_id, list_name):
        """
        Retrieves items from a specified list in a SharePoint site.
        """
        url = f"{self.base_url}/sites/{site_id}/lists/{list_name}/items"
        response = requests.get(url, headers=self.headers, timeout=300)
        response.raise_for_status()
        return response.json()  # .get("value", [])


a = GraphClient()
host = "ts.accenture.com"
path = "SentinelCapabilityLibrary"
lister = "Sub Use Case Library"
b = a.get_site_id(host, path)
c = a.get_list(b, lister)
