import os
import requests
from django.http import JsonResponse

def check_user_access(request):
    user_name = request.GET.get('name')

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

    # Use Graph API to fetch user details
    graph_url = "https://graph.microsoft.com/v1.0/users"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    graph_r = requests.get(graph_url, headers=headers)

    if graph_r.status_code == 200:
        users = graph_r.json().get('value', [])
        for user in users:
            if user.get('displayName') == user_name:  # Compare the name with Azure AD users
                return JsonResponse({"status": "granted", "message": "Access granted"})
        return JsonResponse({"status": "denied", "message": "Access denied"})
    else:
        return JsonResponse({"status": "error", "message": "Unable to fetch user details from Azure AD", "details": graph_r.text})