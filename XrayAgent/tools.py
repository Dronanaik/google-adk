import requests
import os
from dotenv import load_dotenv

load_dotenv()
XRAY_BASE_URL = os.getenv("XRAY_BASE_URL")
client_id = os.getenv("XRAY_CLIENT_ID")
client_secret = os.getenv("XRAY_CLIENT_SECRET")

# def check_project_permission(jira_url, jira_email, jira_api_token, project_key):
#     url = f"{jira_url}/rest/api/3/project/{project_key}"
#     auth = (jira_email, jira_api_token)
#     res = requests.get(url, auth=auth)

#     print("Status:", res.status_code)
    # print(res.text)



def get_xray_token(client_id: str, client_secret: str) -> str:
    """
    Authenticate with Xray Cloud and return the Bearer token.
    """
    url = f"{XRAY_BASE_URL}/authenticate"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Xray authentication failed: {response.status_code}, {response.text}"
        )

    token = response.text.strip('"')  # returns bare token
    return token


def build_auth_header(token: str) -> dict:
    """
    Returns the header to be used for authenticated Xray REST API calls.
    """
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_xray_token(client_id: str, client_secret: str) -> str:
    """
    Authenticate with Xray Cloud and return the Bearer token.
    """
    url = f"{XRAY_BASE_URL}/authenticate"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Xray authentication failed: {response.status_code}, {response.text}"
        )

    token = response.text.strip('"')  # returns bare token
    return token

def build_auth_header(token: str) -> dict:
    """
    Returns the header to be used for authenticated Xray REST API calls.
    """
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


test_payload = [
    {
        "projectKey": "XSP1",
        "summary": "Login functionality test",
        "testType": "Manual",
        "steps": [
            { "action": "Enter username", "result": "Accepted" },
            { "action": "Enter password", "result": "Accepted" },
            { "action": "Click login", "result": "User redirected to dashboard" }
        ]
    }
]



def import_manual_tests_cloud(token: str, test_payload: list) -> dict:
    """
    Import manual test cases to Xray Cloud in bulk.
    
    This function sends a bulk import request to Xray Cloud to create or update
    manual test cases. Each test in the payload should include project key, summary,
    test type, and test steps.
    
    Args:
        token (str): Bearer authentication token obtained from get_xray_token().
        test_payload (list): List of test case dictionaries. Each dictionary should contain:
            - projectKey (str): The Jira project key (e.g., "XSP1").
            - summary (str): Brief description of the test case.
            - testType (str): Type of test (e.g., "Manual", "Automated").
            - steps (list): List of test step dictionaries with 'action' and 'result' keys.
    
    Returns:
        dict: Response from Xray API containing import job details and status.
    
    Raises:
        Exception: If the import request fails (status code not 200 or 201).
    
    Example:
        >>> token = get_xray_token(client_id, client_secret)
        >>> payload = [{
        ...     "projectKey": "XSP1",
        ...     "summary": "Login test",
        ...     "testType": "Manual",
        ...     "steps": [{"action": "Enter credentials", "result": "Login successful"}]
        ... }]
        >>> result = import_manual_tests_cloud(token, payload)
    """
    url = f"{XRAY_BASE_URL}/import/test/bulk"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=test_payload)

    if response.status_code not in (200, 201):
        raise Exception(
            f"Error importing manual tests: {response.status_code} - {response.text}"
        )

    return response.json()



def get_import_job_status(token: str, job_id: str) -> dict:
    """
    Check the status of a bulk test import job in Xray Cloud.
    
    This function queries the Xray API to retrieve the current status of a previously
    submitted bulk import job. Use this to monitor the progress of test case imports.
    
    Args:
        token (str): Bearer authentication token obtained from get_xray_token().
        job_id (str): The unique identifier of the import job returned by
            import_manual_tests_cloud().
    
    Returns:
        dict: Response from Xray API containing job status information, which may include:
            - status (str): Current status of the job (e.g., "processing", "completed", "failed").
            - progress (dict): Details about import progress.
            - errors (list): Any errors encountered during import.
    
    Raises:
        Exception: If the status check request fails (status code not 200).
    
    Example:
        >>> token = get_xray_token(client_id, client_secret)
        >>> job_result = import_manual_tests_cloud(token, test_payload)
        >>> job_id = job_result['jobId']
        >>> status = get_import_job_status(token, job_id)
        >>> print(status['status'])
    """
    url = f"{XRAY_BASE_URL}/import/test/bulk/{job_id}/status"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Error checking job status: {response.status_code} - {response.text}"
        )

    return response.json()



