import os
import requests
from django.http import JsonResponse

def check_user_access(request):
    # Retrieve parameters
    user_name = request.GET.get('name')
    group_id = request.GET.get('group_id')

    # Load sensitive information from environment variables
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    tenant_id = os.getenv('TENANT_ID')

    # Check if environment variables are set
    if not all([client_id, client_secret, tenant_id]):
        return JsonResponse({"status": "error", "message": "Missing environment variables"})

    # Fetch access token from Azure AD
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }

    token_r = requests.post(token_url, data=token_data)
    if token_r.status_code != 200:
        return JsonResponse({"status": "error", "message": "Failed to get access token from Azure AD", "details": token_r.text})

    token = token_r.json().get('access_token')

    # Use Graph API to get the user’s ID based on their display name
    graph_url = f"https://graph.microsoft.com/v1.0/users?$filter=displayName eq '{user_name}'"
    headers = {
        'Authorization': f'Bearer {token}'
    }

    user_r = requests.get(graph_url, headers=headers)
    if user_r.status_code != 200:
        return JsonResponse({"status": "error", "message": "Failed to fetch user details from Azure AD", "details": user_r.text})

    users = user_r.json().get('value', [])
    if not users:
        return JsonResponse({"status": "denied", "message": "User not found"})

    user_id = users[0].get('id')  # Get the first matching user’s ID

    # Check if the user belongs to the specified group
    group_check_url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/{user_id}/$ref"
    group_r = requests.get(group_check_url, headers=headers)

    if group_r.status_code == 204:
        return JsonResponse({"status": "granted", "message": "Access granted"})
    elif group_r.status_code == 404:
        return JsonResponse({"status": "denied", "message": "Access denied"})
    else:
        return JsonResponse({"status": "error", "message": "Error checking group membership", "details": group_r.text})
