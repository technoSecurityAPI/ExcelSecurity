import os
import requests
import base64
import json
from django.http import JsonResponse

def check_user_access(request):
    display_name = request.GET.get('name')  # This should be the exact display name of the user
    group_id = request.GET.get('group_id')  # Fetch group_id from request

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

    # Decode and format JWT token correctly
    try:
        header, payload, signature = token.split('.')
        
        # Decode header and payload from base64
        decoded_header = base64.urlsafe_b64decode(header + '==').decode('utf-8')
        decoded_payload = base64.urlsafe_b64decode(payload + '==').decode('utf-8')

        header_json = json.loads(decoded_header)
        payload_json = json.loads(decoded_payload)
        
        # Now you can access the decoded header and payload
        print("Decoded Header: ", header_json)
        print("Decoded Payload: ", payload_json)

    except Exception as e:
        return JsonResponse({"status": "error", "message": "Failed to decode JWT", "details": str(e)})

    # Fetch user details from Azure AD by filtering users based on their display name
    graph_url = f"https://graph.microsoft.com/v1.0/users?$filter=displayName eq '{display_name}'"
    headers = {
        'Authorization': f'Bearer {token}'
    }

    graph_r = requests.get(graph_url, headers=headers)

    if graph_r.status_code == 200:
        users = graph_r.json().get('value', [])
        if users:
            user = users[0]  # Get the first user that matches the display name

            # Fetch the groups for the user
            user_groups_url = f"https://graph.microsoft.com/v1.0/users/{user['id']}/memberOf"
            groups_r = requests.get(user_groups_url, headers=headers)

            if groups_r.status_code == 200:
                groups = groups_r.json().get('value', [])
                # Check if the user is part of the specified group
                for group in groups:
                    if group.get('id') == group_id:
                        return JsonResponse({"status": "granted", "message": "Access granted"})
                return JsonResponse({"status": "denied", "message": "User is not in the specified group"})
            else:
                return JsonResponse({"status": "error", "message": "Unable to fetch user groups from Azure AD", "details": groups_r.text})
        else:
            return JsonResponse({"status": "denied", "message": "User not found in Azure AD"})
    else:
        return JsonResponse({"status": "error", "message": "Unable to fetch user details from Azure AD", "details": graph_r.text})
