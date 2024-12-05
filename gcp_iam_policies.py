from googleapiclient.discovery import build
from google.oauth2 import service_account

# Authenticate and create API clients
credentials = service_account.Credentials.from_service_account_file(
    'path_to_your_service_account.json', scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Build IAM API client
iam_service = build('iam', 'v1', credentials=credentials)

# Function to get IAM roles for an organization
def get_organization_iam_policy(org_id):
    request = iam_service.organizations().getIamPolicy(
        resource=org_id, body={}
    )
    response = request.execute()
    return response

# Example to list roles for users
org_id = 'organizations/your-org-id'
iam_policy = get_organization_iam_policy(org_id)
print(iam_policy)