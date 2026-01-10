import os
import json
from jira import JIRA, JIRAError
from dotenv import load_dotenv
import requests


# --- Configuration & Client Initialization ---
# The tool will securely load its own credentials from the environment.
# They are never passed in from the agent's prompt.
load_dotenv()
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def _get_jira_client():
    """A private helper function to connect to JIRA."""
    if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        raise ConnectionError("JIRA environment variables (JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN) are not set.")
    
    try:
        client = JIRA(server=JIRA_URL, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        # Verify connection
        client.myself()
        print(f"Successfully connected to Jira at {JIRA_URL}")
        return client
    except JIRAError as e:
        print(f"ERROR: Jira connection failed. Status: {e.status_code}, Text: {e.text}")
        raise ConnectionError(f"Jira connection failed: {e.text}")
    except Exception as e:
        raise ConnectionError(f"An unexpected error occurred during Jira connection: {e}")



def list_jira_projects() -> str:
    """
    Fetches a list of all projects (names and keys) that are visible to the user.
    This should be the first tool used if the project is unknown.
    """
    print("TOOL EXECUTED: 'list_jira_projects'")
    try:
        jira_client = _get_jira_client()
        projects = jira_client.projects()
        
        if not projects:
            return "No projects found."
            
        # Format the output nicely for the agent to display
        project_list = [f"- {p.name} (Key: {p.key})" for p in projects]
        return "Here are the available projects:\n" + "\n".join(project_list)
        
    except Exception as e:
        return f"Error: Failed to list JIRA projects. Reason: {e}"



def fetch_project_epics(project_key: str) -> str:
    """
    Fetches all epics and their linked issues (Stories, Tasks) for a single,
    specified Jira project. This tool requires a valid project key.

    Args:
        project_key: The key of the Jira project to search within (e.g., "PROJ").
    """
    print(f"TOOL EXECUTED: 'fetch_project_epics' for project: '{project_key}'")
    try:
        jira_client = _get_jira_client()
        
        # 1. Fetch Epics for the specified project
        jql_epics = f'project = "{project_key}" AND issuetype = Epic'
        epics = jira_client.search_issues(jql_epics, fields='key,summary', maxResults=50)
        
        if not epics:
            return f"No epics found for project '{project_key}'."

        all_details = []
        # 2. For each Epic, fetch its linked issues
        for epic in epics:
            epic_info = f"\n---\nEpic: {epic.key} - {epic.fields.summary}\n"
            
            # JQL to find issues linked to the epic (works for both Cloud and Server)
            jql_issues = f'"Epic Link" = {epic.key} OR parent = {epic.key}'
            linked_issues = jira_client.search_issues(jql_issues, fields='key,summary,issuetype,description', maxResults=100)
            
            if linked_issues:
                issue_list = [f"  - {issue.fields.issuetype.name}: {issue.key} - {issue.fields.summary} - {issue.fields.description}" for issue in linked_issues]
                epic_info += "\n".join(issue_list)
            else:
                epic_info += "  - No linked stories or tasks found."
            
            all_details.append(epic_info)
            
        return "".join(all_details)

    except Exception as e:
        return f"Error: Failed to fetch epics for project '{project_key}'. Reason: {e}"



# =================================== APP DATA POLICIES TOOLS ===================================

def get_workspace_data_policies(JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN):
    url = f"{JIRA_URL}/rest/api/3/data-policies"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code != 200:
        return {"status": response.status_code, "error": response.text}

    return response.json()


def get_projects_with_data_policies(JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN):
    url = f"{JIRA_URL}/rest/api/3/data-policies/project"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code != 200:
        return {"status": response.status_code, "error": response.text}

    return response.json()

# ===================================================================================================


# =================================== APPLICATIONS ROLE TOOLS ===================================
def get_all_application_roles(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str) -> dict:
    """
    Returns all Jira application roles.
    Equivalent to GET /rest/api/3/applicationrole
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/applicationrole"
    headers = {
        "Accept": "application/json"
    }
    auth = (email, api_token)

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code != 200:
        return {
            "status": response.status_code,
            "error": response.text
        }

    return response.json()


def get_application_role(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, role_key: str) -> dict:
    """
    Returns details of a specific Jira application role by key.
    Equivalent to GET /rest/api/3/applicationrole/{key}
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/applicationrole/{role_key}"
    headers = {
        "Accept": "application/json"
    }
    auth = (email, api_token)

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code != 200:
        return {
            "status": response.status_code,
            "error": response.text
        }

    return response.json()


# ===================================================================================================


# =================================== ISSUE ATTACHMENT TOOLS ===================================

def upload_issue_attachment(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_id_or_key: str, file_path: str) -> dict:
    """
    Uploads a file as an attachment to a Jira issue.
    Returns JSON response similar to Postman.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_id_or_key}/attachments"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    headers = {
        "X-Atlassian-Token": "no-check"
    }

    with open(file_path, "rb") as file:
        files = {
            "file": (file_path, file)
        }
        response = requests.post(url, headers=headers, auth=auth, files=files)

    try:
        return response.json()
    except ValueError:
        return response.text

def delete_attachment(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, attachment_id: str) -> dict:
    """
    Deletes an attachment from Jira by attachment ID.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/attachment/{attachment_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.delete(url, auth=auth)

    if response.status_code == 204:
        return {"status": "deleted", "attachment_id": attachment_id}
    else:
        # Return error details
        try:
            return response.json()
        except ValueError:
            return response.text


def get_attachment_metadata(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, attachment_id: str) -> dict:
    """
    Retrieves metadata for an attachment by its ID.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/attachment/{attachment_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, auth=auth)

    try:
        return response.json()
    except ValueError:
        return response.text


def download_attachment_content(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, attachment_id: str, save_path: str) -> dict:
    """
    Downloads the content of an attachment and saves to a local file.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/attachment/{attachment_id}/content"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.get(url, auth=auth, stream=True)

    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return {"status": "downloaded", "file_path": save_path}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def download_attachment_thumbnail(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, attachment_id: str, save_path: str) -> dict:
    """
    Downloads the thumbnail of an attachment and saves to a local file.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/attachment/{attachment_id}/thumbnail"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.get(url, auth=auth, stream=True)

    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return {"status": "thumbnail downloaded", "file_path": save_path}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text

# ===================================================================================================


def bulk_delete_issues(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_ids_or_keys: list, send_bulk_notification: bool = False) -> dict:
    """
    Bulk delete issues in Jira.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/issues/delete"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    payload = {
        "selectedIssueIdsOrKeys": issue_ids_or_keys,
        "sendBulkNotification": send_bulk_notification
    }

    response = requests.post(url, headers=headers, auth=auth, json=payload)

    try:
        return response.json()
    except:
        return response.text


def get_bulk_editable_fields(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_ids_or_keys: list, search_text: str = None) -> dict:
    """
    Get fields eligible for bulk edit operations.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/issues/fields"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    params = {"issueIdsOrKeys": ",".join(issue_ids_or_keys)}
    if search_text:
        params["searchText"] = search_text

    response = requests.get(url, headers=headers, auth=auth, params=params)

    try:
        return response.json()
    except ValueError:
        return response.text


def bulk_edit_issues(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, selected_issue_ids_or_keys: list, edited_fields_input: list, selected_actions: list = [], send_bulk_notification: bool = False) -> dict:
    """
    Bulk edit multiple issues.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/issues/fields"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    payload = {
        "selectedIssueIdsOrKeys": selected_issue_ids_or_keys,
        "editedFieldsInput": edited_fields_input,
        "selectedActions": selected_actions,
        "sendBulkNotification": send_bulk_notification
    }

    response = requests.post(url, headers=headers, auth=auth, json=payload)
    try:
        return response.json()
    except ValueError:
        return response.text


def bulk_move_issues(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, move_input: dict, send_bulk_notification: bool = False) -> dict:
    """
    Bulk move issues between projects/types.
    move_input is the dictionary specifying source and target mappings.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/issues/move"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    payload = {"sendBulkNotification": send_bulk_notification}
    payload.update(move_input)

    response = requests.post(url, headers=headers, auth=auth, json=payload)

    try:
        return response.json()
    except:
        return response.text

def get_bulk_transitions(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_ids_or_keys: list) -> dict:
    """
    Get available transitions for multiple issues.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/issues/transition"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    params = {"issueIdsOrKeys": ",".join(issue_ids_or_keys)}

    response = requests.get(url, headers=headers, auth=auth, params=params)
    try:
        return response.json()
    except ValueError:
        return response.text


def bulk_transition_issues(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, bulk_transition_inputs: list, send_bulk_notification: bool = False) -> dict:
    """
    Performs bulk issue transitions.
    bulk_transition_inputs example:
    [{"selectedIssueIdsOrKeys": [...], "transitionId": "11" }, ...]
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/issues/transition"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    payload = {
        "bulkTransitionInputs": bulk_transition_inputs,
        "sendBulkNotification": send_bulk_notification
    }

    response = requests.post(url, headers=headers, auth=auth, json=payload)
    try:
        return response.json()
    except ValueError:
        return response.text

def bulk_unwatch_issues(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, selected_issue_ids_or_keys: list) -> dict:
    """
    Unwatch multiple issues.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/issues/unwatch"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    payload = {"selectedIssueIdsOrKeys": selected_issue_ids_or_keys}

    response = requests.post(url, headers=headers, auth=auth, json=payload)
    try:
        return response.json()
    except ValueError:
        return response.text


def bulk_watch_issues(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, selected_issue_ids_or_keys: list) -> dict:
    """
    Watch multiple issues in bulk.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/issues/watch"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    payload = {"selectedIssueIdsOrKeys": selected_issue_ids_or_keys}

    response = requests.post(url, headers=headers, auth=auth, json=payload)
    try:
        return response.json()
    except ValueError:
        return response.text


def get_bulk_operation_status(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, task_id: str) -> dict:
    """
    Check progress for a bulk operation.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/bulk/queue/{task_id}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.get(url, headers=headers, auth=auth)
    try:
        return response.json()
    except ValueError:
        return response.text
# =================================================================================================

def get_comment_properties(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_id_or_key: str, comment_id: str) -> dict:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_id_or_key}/comment/{comment_id}/properties"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.get(url, headers=headers, auth=auth)
    try:
        return response.json()
    except ValueError:
        return response.text    

def get_comment_property(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_id_or_key: str, comment_id: str, property_key: str) -> dict:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_id_or_key}/comment/{comment_id}/properties/{property_key}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.get(url, headers=headers, auth=auth)
    try:
        return response.json()
    except ValueError:
        return response.text

def set_comment_property(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_id_or_key: str, comment_id: str, property_key: str, property_value: dict) -> dict:
    """
    property_value must be a Python object/dict that will be converted to JSON.
    """
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_id_or_key}/comment/{comment_id}/properties/{property_key}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"  
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.put(url, headers=headers, auth=auth, data=json.dumps(property_value))

    try:
        return response.json()
    except ValueError:
        return response.text    


def delete_comment_property(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_id_or_key: str, comment_id: str, property_key: str) -> dict:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_id_or_key}/comment/{comment_id}/properties/{property_key}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.delete(url, auth=auth)

    if response.status_code == 204:
        return {"status": "deleted", "propertyKey": property_key}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def get_issue_comments(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_key: str, start_at: int = 0, max_results: int = 50) -> dict:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_key}/comment"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    params = {
        "startAt": start_at,
        "maxResults": max_results
    }

    response = requests.get(url, headers=headers, auth=auth, params=params)

    try:
        return response.json()
    except ValueError:
        return response.text

def add_issue_comment(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_key: str, comment_body: str) -> dict:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_key}/comment"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    payload = {"body": comment_body}

    response = requests.post(url, headers=headers, auth=auth, json=payload)

    try:
        return response.json()
    except ValueError:
        return response.text


def get_issue_comment(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_key: str, comment_id: str) -> dict:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_key}/comment/{comment_id}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.get(url, headers=headers, auth=auth)

    try:
        return response.json()
    except ValueError:
        return response.text


def update_issue_comment(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_key: str, comment_id: str, new_body: str) -> dict:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_key}/comment/{comment_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    payload = {"body": new_body}

    response = requests.put(url, headers=headers, auth=auth, json=payload)

    try:
        return response.json()
    except ValueError:
        return response.text

def delete_issue_comment(JIRA_URL: str, JIRA_USERNAME: str, JIRA_API_TOKEN: str, issue_key: str, comment_id: str) -> dict:
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_key}/comment/{comment_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)

    response = requests.delete(url, auth=auth)

    if response.status_code == 204:
        return {"status": "deleted", "comment_id": comment_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


# =================================== ISSUE CUSTOM FIELD ASSOCIATIONS ===================================

def create_custom_field_associations(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    association_contexts: list,
    fields: list
) -> dict:
    """Associates custom fields with projects (up to 50 fields and 100 projects per request)."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/association"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {
        "associationContexts": association_contexts,
        "fields": fields
    }
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Association created successfully"}


def remove_custom_field_associations(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    association_contexts: list,
    fields: list
) -> dict:
    """Removes custom field associations from projects and issue type contexts."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/association"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {
        "associationContexts": association_contexts,
        "fields": fields
    }
    
    response = requests.delete(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Association removed successfully"}


# =================================== HELPER FUNCTIONS ===================================

def create_association_context(identifier, context_type="PROJECT_ID"):
    """Creates an association context object for project ID or key."""
    return {
        "identifier": identifier,
        "type": context_type
    }


def create_field_identifier(field_id, identifier_type="FIELD_ID"):
    """Creates a field identifier object for custom field ID."""
    return {
        "identifier": field_id,
        "type": identifier_type
    }


# =================================== ISSUE CUSTOM FIELD CONFIGURATION (APPS) ===================================

def bulk_get_custom_field_configurations(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_ids_or_keys: list,
    id: list = None,
    field_context_id: list = None,
    issue_id: int = None,
    project_key_or_id: str = None,
    issue_type_id: str = None,
    start_at: int = 0,
    max_results: int = 100
) -> dict:
    """Bulk retrieves configurations for custom fields created by Forge apps with optional filtering."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/app/field/context/configuration/list"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"fieldIdsOrKeys": field_ids_or_keys}
    
    params = {
        "startAt": start_at,
        "maxResults": max_results
    }
    
    if id:
        params["id"] = id
    if field_context_id:
        params["fieldContextId"] = field_context_id
    if issue_id:
        params["issueId"] = issue_id
    if project_key_or_id:
        params["projectKeyOrId"] = project_key_or_id
    if issue_type_id:
        params["issueTypeId"] = issue_type_id
    
    response = requests.post(url, headers=headers, auth=auth, json=payload, params=params)
    
    if response.status_code not in (200, 201):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Success"}


def get_custom_field_configurations(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id_or_key: str,
    id: list = None,
    field_context_id: list = None,
    issue_id: int = None,
    project_key_or_id: str = None,
    issue_type_id: str = None,
    start_at: int = 0,
    max_results: int = 100
) -> dict:
    """Retrieves paginated configurations for a custom field created by a Forge app."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/app/field/{field_id_or_key}/context/configuration"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {
        "startAt": start_at,
        "maxResults": max_results
    }
    
    if id:
        params["id"] = id
    if field_context_id:
        params["fieldContextId"] = field_context_id
    if issue_id:
        params["issueId"] = issue_id
    if project_key_or_id:
        params["projectKeyOrId"] = project_key_or_id
    if issue_type_id:
        params["issueTypeId"] = issue_type_id
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def update_custom_field_configurations(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id_or_key: str,
    configurations: list
) -> dict:
    """Updates configurations for contexts of a custom field created by a Forge app."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/app/field/{field_id_or_key}/context/configuration"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"configurations": configurations}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Configuration updated successfully"}


# =================================== ISSUE CUSTOM FIELD CONTEXTS ===================================

def get_custom_field_contexts(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    is_any_issue_type: bool = None,
    is_global_context: bool = None,
    context_id: list = None,
    start_at: int = 0,
    max_results: int = 50
) -> dict:
    """Returns paginated list of custom field contexts for a field."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if is_any_issue_type is not None:
        params["isAnyIssueType"] = is_any_issue_type
    if is_global_context is not None:
        params["isGlobalContext"] = is_global_context
    if context_id:
        params["contextId"] = context_id
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def create_custom_field_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    name: str,
    description: str = None,
    issue_type_ids: list = None,
    project_ids: list = None
) -> dict:
    """Creates a custom field context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"name": name}
    if description:
        payload["description"] = description
    if issue_type_ids:
        payload["issueTypeIds"] = issue_type_ids
    if project_ids:
        payload["projectIds"] = project_ids
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_custom_field_context_default_values(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: list = None,
    start_at: int = 0,
    max_results: int = 50
) -> dict:
    """Returns paginated list of defaults for a custom field."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/defaultValue"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if context_id:
        params["contextId"] = context_id
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def set_custom_field_context_default_values(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    default_values: list
) -> dict:
    """Sets default values for contexts of a custom field."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/defaultValue"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"defaultValues": default_values}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Default values set successfully"}


def get_issue_types_for_custom_field_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    start_at: int = 0,
    max_results: int = 50
) -> dict:
    """Returns paginated list of issue types mapped to a custom field context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/issuetype"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_custom_field_contexts_for_projects_and_issue_types(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    project_issue_type_mappings: list,
    start_at: int = 0,
    max_results: int = 50
) -> dict:
    """Returns paginated list of contexts and their mappings for a custom field."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/mapping"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"mappings": project_issue_type_mappings}
    params = {"startAt": start_at, "maxResults": max_results}
    
    response = requests.post(url, headers=headers, auth=auth, json=payload, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_project_mappings_for_custom_field_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    start_at: int = 0,
    max_results: int = 50
) -> dict:
    """Returns paginated list of project mappings for a custom field context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/project"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def update_custom_field_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    name: str = None,
    description: str = None
) -> dict:
    """Updates a custom field context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Context updated successfully"}


def delete_custom_field_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int
) -> dict:
    """Deletes a custom field context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.delete(url, auth=auth)
    
    if response.status_code == 204:
        return {"status": "deleted", "context_id": context_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def add_issue_types_to_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    issue_type_ids: list
) -> dict:
    """Adds issue types to a custom field context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/issuetype"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"issueTypeIds": issue_type_ids}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue types added successfully"}


def remove_issue_types_from_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    issue_type_ids: list
) -> dict:
    """Removes issue types from a custom field context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/issuetype/remove"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"issueTypeIds": issue_type_ids}
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue types removed successfully"}


def assign_custom_field_context_to_projects(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    project_ids: list
) -> dict:
    """Assigns a custom field context to projects."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/project"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"projectIds": project_ids}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Context assigned to projects successfully"}


def remove_custom_field_context_from_projects(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    project_ids: list
) -> dict:
    """Removes a custom field context from projects."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/project/remove"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"projectIds": project_ids}
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Context removed from projects successfully"}


# =================================== ISSUE CUSTOM FIELD OPTIONS ===================================

def get_custom_field_option(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    option_id: str
) -> dict:
    """Returns a custom field option by ID."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/customFieldOption/{option_id}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.get(url, headers=headers, auth=auth)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_custom_field_options_for_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    option_id: int = None,
    only_options: bool = False,
    start_at: int = 0,
    max_results: int = 100
) -> dict:
    """Returns paginated list of all custom field options for a context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/option"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {
        "startAt": start_at,
        "maxResults": max_results,
        "onlyOptions": only_options
    }
    if option_id:
        params["optionId"] = option_id
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def create_custom_field_options_for_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    options: list
) -> dict:
    """Creates custom field options for a context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/option"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"options": options}
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def update_custom_field_options_for_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    options: list
) -> dict:
    """Updates custom field options for a context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/option"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"options": options}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Options updated successfully"}


def reorder_custom_field_options_for_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    option_ids: list,
    position: str = "First",
    after: int = None
) -> dict:
    """Reorders custom field options in a context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/option/move"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {
        "customFieldOptionIds": option_ids,
        "position": position
    }
    if after:
        payload["after"] = after
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Options reordered successfully"}


def delete_custom_field_options_for_context(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    context_id: int,
    option_id: int
) -> dict:
    """Deletes a custom field option from a context."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context/{context_id}/option/{option_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.delete(url, auth=auth)
    
    if response.status_code == 204:
        return {"status": "deleted", "option_id": option_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def replace_custom_field_options(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    replace_with: int,
    jql: str = None,
    override_screen_security: bool = False,
    override_editable_flag: bool = False
) -> dict:
    """Replaces custom field options in issues matching a JQL query."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/option/replace"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {
        "replaceWith": replace_with,
        "overrideScreenSecurity": override_screen_security,
        "overrideEditableFlag": override_editable_flag
    }
    if jql:
        payload["jql"] = jql
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 303):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Options replaced successfully"}


# =================================== ISSUE CUSTOM FIELD VALUES (APPS) ===================================

def update_multiple_custom_field_values(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    updates: list,
    generate_changelog: bool = True
) -> dict:
    """Updates custom field values on multiple issues for Forge app custom fields."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/app/field/value"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"generateChangelog": generate_changelog}
    payload = {"updates": updates}
    
    response = requests.post(url, headers=headers, auth=auth, json=payload, params=params)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Custom field values updated successfully"}


def update_custom_field_value(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id_or_key: str,
    updates: list,
    generate_changelog: bool = True
) -> dict:
    """Updates custom field value on one or more issues for a specific Forge app custom field."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/app/field/{field_id_or_key}/value"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"generateChangelog": generate_changelog}
    payload = {"updates": updates}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload, params=params)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Custom field value updated successfully"}


# =================================== ISSUE FIELD CONFIGURATIONS ===================================

def get_all_field_configurations(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    start_at: int = 0,
    max_results: int = 50,
    id: list = None,
    is_default: bool = None,
    query: str = None
) -> dict:
    """Returns paginated list of all field configurations."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfiguration"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if id:
        params["id"] = id
    if is_default is not None:
        params["isDefault"] = is_default
    if query:
        params["query"] = query
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def create_field_configuration(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    name: str,
    description: str = None
) -> dict:
    """Creates a field configuration."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfiguration"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"name": name}
    if description:
        payload["description"] = description
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def update_field_configuration(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    config_id: int,
    name: str,
    description: str = None
) -> dict:
    """Updates a field configuration."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfiguration/{config_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"name": name}
    if description:
        payload["description"] = description
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Field configuration updated successfully"}


def delete_field_configuration(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    config_id: int
) -> dict:
    """Deletes a field configuration."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfiguration/{config_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.delete(url, auth=auth)
    
    if response.status_code == 204:
        return {"status": "deleted", "config_id": config_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def get_field_configuration_items(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    config_id: int,
    start_at: int = 0,
    max_results: int = 50
) -> dict:
    """Returns paginated list of field configuration items."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfiguration/{config_id}/fields"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def update_field_configuration_items(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    config_id: int,
    field_configuration_items: list
) -> dict:
    """Updates field configuration items."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfiguration/{config_id}/fields"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"fieldConfigurationItems": field_configuration_items}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Field configuration items updated successfully"}


def get_all_field_configuration_schemes(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    start_at: int = 0,
    max_results: int = 50,
    id: list = None
) -> dict:
    """Returns paginated list of field configuration schemes."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if id:
        params["id"] = id
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def create_field_configuration_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    name: str,
    description: str = None
) -> dict:
    """Creates a field configuration scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"name": name}
    if description:
        payload["description"] = description
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_field_configuration_issue_type_items(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    start_at: int = 0,
    max_results: int = 50,
    field_configuration_scheme_id: list = None
) -> dict:
    """Returns paginated list of field configuration issue type items."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme/mapping"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if field_configuration_scheme_id:
        params["fieldConfigurationSchemeId"] = field_configuration_scheme_id
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_field_configuration_schemes_for_projects(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    project_id: list,
    start_at: int = 0,
    max_results: int = 50
) -> dict:
    """Returns paginated list of field configuration schemes for projects."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme/project"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {
        "startAt": start_at,
        "maxResults": max_results,
        "projectId": project_id
    }
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def assign_field_configuration_scheme_to_project(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_configuration_scheme_id: str,
    project_id: str
) -> dict:
    """Assigns a field configuration scheme to a project."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme/project"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {
        "fieldConfigurationSchemeId": field_configuration_scheme_id,
        "projectId": project_id
    }
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Field configuration scheme assigned successfully"}


def update_field_configuration_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int,
    name: str,
    description: str = None
) -> dict:
    """Updates a field configuration scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme/{scheme_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"name": name}
    if description:
        payload["description"] = description
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Field configuration scheme updated successfully"}


def delete_field_configuration_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int
) -> dict:
    """Deletes a field configuration scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme/{scheme_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.delete(url, auth=auth)
    
    if response.status_code == 204:
        return {"status": "deleted", "scheme_id": scheme_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def assign_issue_types_to_field_configurations(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int,
    field_configuration_to_issue_type_mappings: list
) -> dict:
    """Assigns issue types to field configurations in a field configuration scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme/{scheme_id}/mapping"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"mappings": field_configuration_to_issue_type_mappings}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue types assigned successfully"}


def remove_issue_types_from_field_configuration_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int,
    issue_type_ids: list
) -> dict:
    """Removes issue types from a field configuration scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/fieldconfigurationscheme/{scheme_id}/mapping/delete"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"issueTypeIds": issue_type_ids}
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue types removed successfully"}


# =================================== ISSUE FIELDS ===================================

def get_fields(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str
) -> dict:
    """Returns system and custom issue fields."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.get(url, headers=headers, auth=auth)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def create_custom_field(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    name: str,
    type: str,
    description: str = None,
    searcher_key: str = None
) -> dict:
    """Creates a custom field."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {
        "name": name,
        "type": type
    }
    if description:
        payload["description"] = description
    if searcher_key:
        payload["searcherKey"] = searcher_key
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_fields_paginated(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    start_at: int = 0,
    max_results: int = 50,
    type: list = None,
    id: list = None,
    query: str = None,
    order_by: str = None,
    expand: str = None
) -> dict:
    """Returns paginated list of fields."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/search"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if type:
        params["type"] = type
    if id:
        params["id"] = id
    if query:
        params["query"] = query
    if order_by:
        params["orderBy"] = order_by
    if expand:
        params["expand"] = expand
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_fields_in_trash_paginated(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    start_at: int = 0,
    max_results: int = 50,
    id: list = None,
    query: str = None,
    order_by: str = None
) -> dict:
    """Returns paginated list of fields in the trash."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/search/trashed"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if id:
        params["id"] = id
    if query:
        params["query"] = query
    if order_by:
        params["orderBy"] = order_by
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def update_custom_field(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str,
    name: str = None,
    description: str = None,
    searcher_key: str = None
) -> dict:
    """Updates a custom field."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    if searcher_key:
        payload["searcherKey"] = searcher_key
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Custom field updated successfully"}


def delete_custom_field(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str
) -> dict:
    """Deletes a custom field (moves to trash by default)."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.delete(url, auth=auth)
    
    if response.status_code == 204:
        return {"status": "deleted", "field_id": field_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def restore_custom_field_from_trash(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str
) -> dict:
    """Restores a custom field from trash."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/restore"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.post(url, headers=headers, auth=auth)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Custom field restored successfully"}


def move_custom_field_to_trash(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    field_id: str
) -> dict:
    """Moves a custom field to trash."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/trash"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.post(url, headers=headers, auth=auth)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Custom field moved to trash successfully"}


# =================================== ISSUE TYPES ===================================

def get_all_issue_types_for_user(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str
) -> dict:
    """Returns all issue types visible to the user."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetype"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.get(url, headers=headers, auth=auth)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def create_issue_type(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    name: str,
    description: str = None,
    type: str = "standard"
) -> dict:
    """Creates an issue type."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetype"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"name": name, "type": type}
    if description:
        payload["description"] = description
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_issue_types_for_project(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    project_id: int,
    level: int = None
) -> dict:
    """Returns issue types for a project."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetype/project"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"projectId": project_id}
    if level is not None:
        params["level"] = level
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_issue_type(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    issue_type_id: str
) -> dict:
    """Returns an issue type."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetype/{issue_type_id}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.get(url, headers=headers, auth=auth)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def update_issue_type(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    issue_type_id: str,
    name: str = None,
    description: str = None,
    avatar_id: int = None
) -> dict:
    """Updates an issue type."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetype/{issue_type_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    if avatar_id is not None:
        payload["avatarId"] = avatar_id
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue type updated successfully"}


def delete_issue_type(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    issue_type_id: str,
    alternative_issue_type_id: str = None
) -> dict:
    """Deletes an issue type."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetype/{issue_type_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {}
    if alternative_issue_type_id:
        params["alternativeIssueTypeId"] = alternative_issue_type_id
    
    response = requests.delete(url, auth=auth, params=params)
    
    if response.status_code == 204:
        return {"status": "deleted", "issue_type_id": issue_type_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def get_alternative_issue_types(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    issue_type_id: str
) -> dict:
    """Returns alternative issue types for an issue type."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetype/{issue_type_id}/alternatives"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.get(url, headers=headers, auth=auth)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def load_issue_type_avatar(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    issue_type_id: str,
    size: int,
    x: int = None,
    y: int = None,
    avatar_data: bytes = None
) -> dict:
    """Loads an avatar for an issue type."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetype/{issue_type_id}/avatar2"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"size": size}
    if x is not None:
        params["x"] = x
    if y is not None:
        params["y"] = y
    
    files = {}
    if avatar_data:
        files = {"avatar": avatar_data}
    
    response = requests.post(url, headers=headers, auth=auth, params=params, files=files)
    
    try:
        return response.json()
    except ValueError:
        return response.text


# =================================== ISSUE TYPE SCHEMES ===================================

def get_all_issue_type_schemes(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    start_at: int = 0,
    max_results: int = 50,
    id: list = None
) -> dict:
    """Returns paginated list of issue type schemes."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if id:
        params["id"] = id
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def create_issue_type_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    name: str,
    description: str = None,
    default_issue_type_id: str = None,
    issue_type_ids: list = None
) -> dict:
    """Creates an issue type scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"name": name}
    if description:
        payload["description"] = description
    if default_issue_type_id:
        payload["defaultIssueTypeId"] = default_issue_type_id
    if issue_type_ids:
        payload["issueTypeIds"] = issue_type_ids
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_issue_type_scheme_items(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    start_at: int = 0,
    max_results: int = 50,
    issue_type_scheme_id: list = None
) -> dict:
    """Returns paginated list of issue type scheme items."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme/mapping"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {"startAt": start_at, "maxResults": max_results}
    if issue_type_scheme_id:
        params["issueTypeSchemeId"] = issue_type_scheme_id
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def get_issue_type_schemes_for_projects(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    project_id: list,
    start_at: int = 0,
    max_results: int = 50
) -> dict:
    """Returns paginated list of issue type schemes for projects."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme/project"
    headers = {"Accept": "application/json"}
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    params = {
        "startAt": start_at,
        "maxResults": max_results,
        "projectId": project_id
    }
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    
    try:
        return response.json()
    except ValueError:
        return response.text


def assign_issue_type_scheme_to_project(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    issue_type_scheme_id: str,
    project_id: str
) -> dict:
    """Assigns an issue type scheme to a project."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme/project"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {
        "issueTypeSchemeId": issue_type_scheme_id,
        "projectId": project_id
    }
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue type scheme assigned successfully"}


def update_issue_type_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int,
    name: str = None,
    description: str = None,
    default_issue_type_id: str = None
) -> dict:
    """Updates an issue type scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme/{scheme_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    if default_issue_type_id:
        payload["defaultIssueTypeId"] = default_issue_type_id
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue type scheme updated successfully"}


def delete_issue_type_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int
) -> dict:
    """Deletes an issue type scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme/{scheme_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.delete(url, auth=auth)
    
    if response.status_code == 204:
        return {"status": "deleted", "scheme_id": scheme_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text


def add_issue_types_to_issue_type_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int,
    issue_type_ids: list
) -> dict:
    """Adds issue types to an issue type scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme/{scheme_id}/issuetype"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {"issueTypeIds": issue_type_ids}
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue types added successfully"}


def reorder_issue_types_in_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int,
    issue_type_id: str,
    position: int,
    after: str = None
) -> dict:
    """Reorders issue types in an issue type scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme/{scheme_id}/issuetype/move"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    payload = {
        "issueTypeId": issue_type_id,
        "position": position
    }
    if after:
        payload["after"] = after
    
    response = requests.put(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code not in (200, 201, 204):
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        return {
            "status": response.status_code,
            "error": error_detail
        }
    
    try:
        return response.json()
    except ValueError:
        return {"status": response.status_code, "message": "Issue types reordered successfully"}


def remove_issue_type_from_scheme(
    JIRA_URL: str,
    JIRA_USERNAME: str,
    JIRA_API_TOKEN: str,
    scheme_id: int,
    issue_type_id: str
) -> dict:
    """Removes an issue type from an issue type scheme."""
    url = f"{JIRA_URL.rstrip('/')}/rest/api/3/issuetypescheme/{scheme_id}/issuetype/{issue_type_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    
    response = requests.delete(url, auth=auth)
    
    if response.status_code == 204:
        return {"status": "removed", "issue_type_id": issue_type_id}
    else:
        try:
            return response.json()
        except ValueError:
            return response.text

# ===================================================================================================









