# MetaUpdateCampaignStatusTool

# Description
The `MetaUpdateCampaignStatusTool` updates the statuses of specified Meta (Facebook) Ads campaigns based on provided campaign IDs and desired statuses. By supplying a file with campaign IDs and their corresponding new statuses, this tool automates the process of managing campaign states, ensuring your campaigns are active, paused, deleted, or archived as needed. This aids in efficient campaign management and operational control over your advertising efforts.

# Installation
```shell
pip install 'moonai.moonai_tools'

Prerequisites
Before using the MetaUpdateCampaignStatusTool, ensure you have set the following environment variables with your Meta Ads credentials:

ACCESS_TOKEN: Your Meta access token.
APP_SECRET: Your Meta app secret.
APP_ID: Your Meta app ID.
```

You can set these variables in your environment using export commands, environment configuration files managed by your deployment system, or any other secure method.

# Example in Unix/Linux:
```shell
export ACCESS_TOKEN='your_access_token'
export APP_SECRET='your_app_secret'
export APP_ID='your_app_id'
```

# Example in Windows (CMD):
```cmd
set ACCESS_TOKEN=your_access_token
set APP_SECRET=your_app_secret
set APP_ID=your_app_id
```
Note: Ensure that these credentials are stored securely and not exposed in your codebase or version control systems.


# Usage Example
To get started with the MetaUpdateCampaignStatusTool:

Prepare the Status Updates File:

Create a text file (e.g., status_updates.txt) with each line containing a campaign_id and a desired_status separated by a comma. The desired_status should be one of the valid statuses: ACTIVE, PAUSED, DELETED, or ARCHIVED.

Example Content (status_updates.txt):

120213989598720505,PAUSED
120213945451090505,ACTIVE
invalid_line
130213989598720506,DELETED
campanha 140213989598720507,abc
150213989598720508,ARCHIVED

## Initialize and Execute the Tool:

```python
from moonai.moonai_tools import MetaUpdateCampaignStatusTool

# Path to the file containing campaign status updates
file_path = "campaigns/status_updates.txt"

# Initialize the tool
update_status_tool = MetaUpdateCampaignStatusTool()

# Execute the tool by specifying the file path
result = update_status_tool._run(file_path=file_path)

# Display the result
print(result)
```

# Explanation of the Example:
## Prepare the Status Updates File:

Each line should follow the format 'campaign_id,desired_status'.
The desired_status should be one of the valid statuses: ACTIVE, PAUSED, DELETED, or ARCHIVED.

## Initialize the Tool:

Instantiate the MetaUpdateCampaignStatusTool class.

## Execute the Tool:

Call the _run method, passing the file_path as an argument.

## Result:

The tool processes each line, cleans the data, validates the desired status, and updates the campaigns accordingly.
The result will be a string indicating the success of each operation or detailing any errors encountered during the process.

# Arguments
file_path: Required. A string representing the path to the file containing campaign status updates. Each line in the file should follow the format 'campaign_id,desired_status', where desired_status is one of the valid statuses (ACTIVE, PAUSED, DELETED, ARCHIVED).

## Example:

```python
"campaigns/status_updates.txt"
```

## File Content Example:

120213989598720505,PAUSED
120213945451090505,ACTIVE
invalid_line
130213989598720506,DELETED
campanha 140213989598720507,abc
150213989598720508,ARCHIVED

# Output Format
The tool returns a string indicating the success of the operations or detailing any errors encountered during the process. The possible outputs include:

## Success:
```yaml
Linha limpa: '120213989598720505,PAUSED'
Linha limpa: '120213945451090505,ACTIVE'
Linha ignorada durante a limpeza: 'invalid_line'
Linha limpa: '130213989598720506,DELETED'
Linha limpa: '150213989598720508,ARCHIVED'

Status da campanha 120213989598720505 atualizado com sucesso para PAUSED.
Confirmação via API - Status atual: PAUSED
Special Ad Categories: []

Status da campanha 120213945451090505 atualizado com sucesso para ACTIVE.
Confirmação via API - Status atual: ACTIVE
Special Ad Categories: []

Status da campanha 130213989598720506 atualizado com sucesso para DELETED.
Confirmação via API - Status atual: DELETED
Special Ad Categories: []

Status da campanha 150213989598720508 atualizado com sucesso para ARCHIVED.
Confirmação via API - Status atual: ARCHIVED
Special Ad Categories: []

Atualização dos status das campanhas concluída com sucesso.
```

## Missing Credentials:
```javascript
Error: Facebook Ads credentials not found.

```
## Errors During Processing:
```arduino
Linha 5: Erro - Status inválido 'abc'. Status válidos são: {'ACTIVE', 'PAUSED', 'DELETED', 'ARCHIVED'}
```
```javascript
Error updating campaign statuses: <error_details>

```
## Empty Status Updates:
```css
Nenhuma atualização de status ou alteração de nome necessária após a limpeza.
```

# Error Handling
The tool handles various error scenarios to ensure robustness:

## Missing Credentials:
If the necessary credentials (ACCESS_TOKEN, APP_SECRET, APP_ID) are not found in the environment variables, the tool returns:

```javascript
Error: Facebook Ads credentials not found.
```

## Invalid Status Update Format:
If a line does not follow the 'campaign_id,desired_status' format or if desired_status is not one of the valid statuses (ACTIVE, PAUSED, DELETED, ARCHIVED), the tool will ignore that line and notify the user:

```arduino
Linha 5: Erro - Status inválido 'abc'. Status válidos são: {'ACTIVE', 'PAUSED', 'DELETED', 'ARCHIVED'}
```
## API Errors:
Any errors returned by the Facebook Ads API during the status updates will be captured and returned to the user:

```javascript
Error updating campaign statuses: <error_details>
```
## Empty Status Updates:
If no valid status updates are provided after cleaning, the tool will notify:

```css
Nenhuma atualização de status ou alteração de nome necessária após a limpeza.
```

# Additional Examples

## Updating with Multiple Campaigns
```python
from moonai.moonai_tools import MetaUpdateCampaignStatusTool

# Path to the file containing campaign status updates
file_path = "campaigns/status_updates_multiple.txt"

# Content of status_updates_multiple.txt:
# 123456789012345,ACTIVE
# 678901234567890,PAUSED
# 112233445566778,DELETED

update_status_tool = MetaUpdateCampaignStatusTool()
result = update_status_tool._run(file_path=file_path)

print(result)
```

## Expected Output:

```yaml
Linha limpa: '123456789012345,ACTIVE'
Linha limpa: '678901234567890,PAUSED'
Linha limpa: '112233445566778,DELETED'

Status da campanha 123456789012345 atualizado com sucesso para ACTIVE.
Confirmação via API - Status atual: ACTIVE
Special Ad Categories: []

Status da campanha 678901234567890 atualizado com sucesso para PAUSED.
Confirmação via API - Status atual: PAUSED
Special Ad Categories: []

Status da campanha 112233445566778 atualizado com sucesso para DELETED.
Confirmação via API - Status atual: DELETED
Special Ad Categories: []

Atualização dos status das campanhas concluída com sucesso.
```

## Handling Invalid Entries
```python
from moonai.moonai_tools import MetaUpdateCampaignStatusTool

# Path to the file containing campaign status updates
file_path = "campaigns/status_updates_invalid.txt"

# Content of status_updates_invalid.txt:
# 123456789012345,ACTIVE
# invalid_line
# 678901234567890,abc
# 112233445566778,PAUSED

update_status_tool = MetaUpdateCampaignStatusTool()
result = update_status_tool._run(file_path=file_path)

print(result)
```

## Expected Output:

```yaml
Linha limpa: '123456789012345,ACTIVE'
Linha ignorada durante a limpeza: 'invalid_line'
Linha limpa: '678901234567890,abc'
Linha limpa: '112233445566778,PAUSED'

Status da campanha 123456789012345 atualizado com sucesso para ACTIVE.
Confirmação via API - Status atual: ACTIVE
Special Ad Categories: []

Linha 3: Erro - Status inválido 'abc'. Status válidos são: {'ACTIVE', 'PAUSED', 'DELETED', 'ARCHIVED'}

Status da campanha 112233445566778 atualizado com sucesso para PAUSED.
Confirmação via API - Status atual: PAUSED
Special Ad Categories: []

Atualização dos status das campanhas concluída com sucesso.
```

# Best Practices

## Secure Credential Management:
Ensure that your access credentials (ACCESS_TOKEN, APP_SECRET, APP_ID) are stored securely. Avoid hardcoding them in your scripts or exposing them in version control systems.

## Data Validation:
Always verify that the provided campaign_id values are correct and that the desired_status values are valid to prevent unintended interruptions in your campaigns.

## Monitor Updates:
After executing the tool, review the output logs to ensure that all updates were applied as expected.

## Backup Campaign Data:
Before performing bulk updates, consider backing up your current campaign configurations to restore them in case of any issues.

Note: This tool automates the process of updating campaign statuses in Meta Ads. Use it cautiously and always validate the data before performing bulk updates to avoid inconsistencies or unwanted errors in your ad campaigns.

# Additional Recommendations

## Use Logging Instead of Print Statements:

For better control and flexibility over logging, consider using Python's logging library instead of print statements.

Example:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace print statements with logging
logging.info(f"Linha limpa: '{campaign_id},{desired_status}'")
logging.warning(f"Linha ignorada durante a limpeza: '{linha}'")
```

## Implement Environment Variable Validation:

Before initializing the Facebook Ads API, ensure that all required environment variables are present and valid.

## Enhance Error Messages:

Provide more detailed error messages to assist users in troubleshooting issues effectively.

## Automate Testing:

Use testing frameworks like pytest to create automated tests for the tool, ensuring it handles various scenarios gracefully.

## Documentation Updates:

Keep the documentation updated with any future changes to the tool to ensure users have accurate and helpful information.

## Handle Multiple Status Formats:

Consider supporting different status formats and providing clear instructions on the expected input to accommodate diverse user needs.
