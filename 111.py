from composio import ComposioToolSet, App
toolset = ComposioToolSet(api_key="h6ci7q0d4l427nownc993h")

integration = toolset.get_integration(id="8fd3ac89-bf93-4e82-b098-8ce19e78f89a")
# Collect auth params from your users
print(integration.expectedInputFields)

connection_request = toolset.initiate_connection(
    integration_id=integration.id,
    connected_account_params={
  "apikey": "your apikey"
  },
    entity_id="default",
)

# Redirect step require for OAuth Flow
print(connection_request.redirectUrl)
print(connection_request.connectedAccountId)
