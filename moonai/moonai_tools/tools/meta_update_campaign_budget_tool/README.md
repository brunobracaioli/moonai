# title:
Update Campaign Budget description: The MetaUpdateCampaignBudgetTool updates the budgets of specified Meta (Facebook) Ads campaigns based on provided campaign IDs and new budget values. icon: money

# MetaUpdateCampaignBudgetTool
<Note> We are still working on improving tools, so there might be unexpected behavior or changes in the future. </Note>

# Description
The MetaUpdateCampaignBudgetTool is a robust component within the moonai_tools package, designed to update the budgets of specified Meta (Facebook) Ads campaigns. By providing a file containing campaign IDs along with their corresponding new budget values, this tool automates the process of budget management, ensuring that your campaigns are always running with the desired financial allocations. Additionally, it processes the budget values by multiplying them by 100, removing decimal points, and then multiplying by 1.30 to adjust the final budget accordingly. It also updates the campaign names to reflect the date of the budget modification, aiding in tracking and auditing changes over time.

# Installation
To utilize the functionalities of the MetaUpdateCampaignBudgetTool, install the moonai_tools package:

```shell
pip install 'moonai.moonai_tools'
```

# Prerequisites
Before using the MetaUpdateCampaignBudgetTool, ensure you have set the following environment variables with your Meta Ads credentials:

ACCESS_TOKEN: Your Meta access token.
APP_SECRET: Your Meta app secret.
APP_ID: Your Meta app ID.

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
To get started with the MetaUpdateCampaignBudgetTool:

# Prepare the Budget Updates File:

Create a text file (e.g., budget_updates.txt) with each line containing a campaign_id and a new budget_value separated by a comma. The budget_value should be in a monetary format (e.g., 250.33).

# Example Content (budget_updates.txt):

```bash
id da campanha 120213989598720505,190 
120213945451090505,250.33
algum texto inválido
130213989598720506,300
campanha 140213989598720507,abc
150213989598720508,400.75
```

# Initialize and Execute the Tool:

```python
from moonai.moonai_tools import MetaUpdateCampaignBudgetTool

# Path to the file containing campaign budget updates
file_path = "campaigns/budget_updates.txt"

# Initialize the tool
update_budget_tool = MetaUpdateCampaignBudgetTool()

# Execute the tool by specifying the file path
result = update_budget_tool._run(file_path=file_path)

# Display the result
print(result)
```

# Explanation of the Example:
## Prepare the Budget Updates File:

Each line should follow the format 'campaign_id,budget_value'.
The budget_value should be a monetary value (e.g., 250.33).
Initialize the Tool:

Instantiate the MetaUpdateCampaignBudgetTool class.

# Execute the Tool:

Call the _run method, passing the file_path as an argument.
Result:

The tool processes each line, cleans the data, converts the budget_value by multiplying by 100 and then by 1.30, and updates the campaigns accordingly.
The result will be a string indicating the success of each operation or detailing any errors encountered during the process.

## Arguments
file_path: Required. A string representing the path to the file containing campaign budget updates. Each line in the file should follow the format 'campaign_id,budget_value', where budget_value is a monetary value.

## Example:

```python
"campaigns/budget_updates.txt"
```
## File Content Example:

120213989598720505,190 
120213945451090505,250.33
algum texto inválido
130213989598720506,300
campanha 140213989598720507,abc
150213989598720508,400.75

## Output Format
The tool returns a string indicating the success of the operations or detailing any errors encountered during the process. The possible outputs include:

## Success:

```yaml
Linha limpa: '120213989598720505,190'
Linha limpa: '120213945451090505,250.33'
Linha ignorada durante a limpeza: 'algum texto inválido'
Linha limpa: '130213989598720506,300'
Linha limpa: '150213989598720508,400.75'

Orçamento atualizado para 24700 na campanha 120213989598720505 com sucesso.
Confirmação via API - Orçamento atual: 24700)

Nome da campanha 120213989598720505 atualizado para: 'Campanha Primavera [Orçamento editado em 28/11/24]' com sucesso.

Orçamento atualizado para 32543 na campanha 120213945451090505 com sucesso.
Confirmação via API - Orçamento atual: 32543)

Nome da campanha 120213945451090505 atualizado para: 'Campanha Verão [Orçamento editado em 28/11/24]' com sucesso.

Orçamento atualizado para 39000 na campanha 130213989598720506 com sucesso.
Confirmação via API - Orçamento atual: 39000)

Nome da campanha 130213989598720506 atualizado para: 'Campanha Outono [Orçamento editado em 28/11/24]' com sucesso.

Orçamento atualizado para 52100 na campanha 150213989598720508 com sucesso.
Confirmação via API - Orçamento atual: 52100)

Nome da campanha 150213989598720508 atualizado para: 'Campanha Inverno [Orçamento editado em 28/11/24]' com sucesso.

Atualização das campanhas concluída com sucesso.
```

## Missing Credentials:

```javascript
Error: Facebook Ads credentials not found.
```

Errors During Processing:

```arduino
Linha 5: Erro - O valor do orçamento 'abc' não é numérico. Verifique o conteúdo do arquivo.
```

```javascript
Error updating campaign budgets: <error_details>
```

## Empty Budget Updates:

```css
Nenhuma atualização de orçamento ou alteração de nome necessária após a limpeza.
```

## Error Handling
The tool handles various error scenarios to ensure robustness:

## Missing Credentials:
If the necessary credentials (ACCESS_TOKEN, APP_SECRET, APP_ID) are not found in the environment variables, the tool returns:

```javascript
Error: Facebook Ads credentials not found.
Invalid Budget Update Format:
If a line does not follow the 'campaign_id,budget_value' format or if budget_value is not a valid monetary number, the tool will ignore that line and notify the user:
```
```arduino
Linha 5: Erro - O valor do orçamento 'abc' não é numérico. Verifique o conteúdo do arquivo.
```

## API Errors:
Any errors returned by the Facebook Ads API during the budget or name updates will be captured and returned to the user:

```javascript
Error updating campaign budgets: <error_details>
```

## Empty Budget Updates:
If no valid budget updates are provided after cleaning, the tool will notify:

```css
Nenhuma atualização de orçamento ou alteração de nome necessária após a limpeza.
```

# Additional Examples
Updating with Multiple Campaigns

```python
from moonai.moonai_tools import MetaUpdateCampaignBudgetTool

# Path to the file containing campaign budget updates
file_path = "campaigns/budget_updates_multiple.txt"

# Content of budget_updates_multiple.txt:
# 123456789012345,1000
# 678901234567890,1500
# 112233445566778,2000

update_budget_tool = MetaUpdateCampaignBudgetTool()
result = update_budget_tool._run(file_path=file_path)

print(result)
```

## Expected Output:

```yaml
Linha limpa: '123456789012345,1000'
Linha limpa: '678901234567890,1500'
Linha limpa: '112233445566778,2000'

Orçamento atualizado para 130000 na campanha 123456789012345 com sucesso.
Confirmação via API - Orçamento atual: 130000)

Nome da campanha 123456789012345 atualizado para: 'Campanha Primavera [Orçamento editado em 28/11/24]' com sucesso.

Orçamento atualizado para 195000 na campanha 678901234567890 com sucesso.
Confirmação via API - Orçamento atual: 195000)

Nome da campanha 678901234567890 atualizado para: 'Campanha Verão [Orçamento editado em 28/11/24]' com sucesso.

Orçamento atualizado para 260000 na campanha 112233445566778 com sucesso.
Confirmação via API - Orçamento atual: 260000)

Nome da campanha 112233445566778 atualizado para: 'Campanha Outono [Orçamento editado em 28/11/24]' com sucesso.

Atualização das campanhas concluída com sucesso.
```

## Handling Invalid Entries

```python
from moonai.moonai_tools import MetaUpdateCampaignBudgetTool

# Path to the file containing campaign budget updates
file_path = "campaigns/budget_updates_invalid.txt"

# Content of budget_updates_invalid.txt:
# 123456789012345,1000
# invalid_line
# 678901234567890,abc
# 112233445566778,2000

update_budget_tool = MetaUpdateCampaignBudgetTool()
result = update_budget_tool._run(file_path=file_path)

print(result)
```

## Expected Output:

```yaml
Linha limpa: '123456789012345,1000'
Linha ignorada durante a limpeza: 'invalid_line'
Linha limpa: '678901234567890,abc'
Linha limpa: '112233445566778,2000'

Orçamento atualizado para 130000 na campanha 123456789012345 com sucesso.
Confirmação via API - Orçamento atual: 130000)

Nome da campanha 123456789012345 atualizado para: 'Campanha Primavera [Orçamento editado em 28/11/24]' com sucesso.

Linha 3: Erro - O valor do orçamento 'abc' não é numérico. Verifique o conteúdo do arquivo.

Orçamento atualizado para 260000 na campanha 112233445566778 com sucesso.
Confirmação via API - Orçamento atual: 260000)

Nome da campanha 112233445566778 atualizado para: 'Campanha Outono [Orçamento editado em 28/11/24]' com sucesso.

Atualização das campanhas concluída com sucesso.
```

# Best Practices
Secure Credential Management:
Ensure that your access credentials (ACCESS_TOKEN, APP_SECRET, APP_ID) are stored securely. Avoid hardcoding them in your scripts or exposing them in version control systems.

## Data Validation:
Always verify that the provided campaign_id values are correct and that the budget_value amounts are appropriate to prevent unintended interruptions in your campaigns.

## Monitor Updates:
After executing the tool, review the output logs to ensure that all updates were applied as expected.

## Backup Campaign Data:
Before performing bulk updates, consider backing up your current campaign configurations to restore them in case of any issues.

Note: This tool automates the process of updating campaign budgets and names in Meta Ads. Use it cautiously and always validate the data before performing bulk updates to avoid inconsistencies or unwanted errors in your ad campaigns.

## Additional Recommendations
Use Logging Instead of Print Statements:

For better control and flexibility over logging, consider using Python's logging library instead of print statements.

Example:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace print statements with logging
logging.info(f"Linha limpa: '{id_},{value}'")
logging.warning(f"Linha ignorada durante a limpeza: '{linha}'")
```

# Implement Environment Variable Validation:

Before initializing the Facebook Ads API, ensure that all required environment variables are present and valid.

# Enhance Error Messages:

Provide more detailed error messages to assist users in troubleshooting issues effectively.

# Automate Testing:

Use testing frameworks like pytest to create automated tests for the tool, ensuring it handles various scenarios gracefully.

## Documentation Updates:

Keep the documentation updated with any future changes to the tool to ensure users have accurate and helpful information.

## Handle Multiple Budget Formats:

Consider supporting different budget formats and providing clear instructions on the expected input to accommodate diverse user needs.

