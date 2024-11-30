# test_direct_MetaUpdateCampaignStatusTool.py

from moonai.moonai_tools import MetaUpdateCampaignStatusTool
from dotenv import load_dotenv

# Carregar variáveis de ambiente, se necessário
load_dotenv()

# Path to the file containing campaign status updates
file_path = "status_updates.txt"

# Initialize the tool
update_status_tool = MetaUpdateCampaignStatusTool()

# Execute the tool by specifying the file path
result = update_status_tool._run(file_path=file_path)

# Display the result
print(result)

# Para executar o teste, use:
# python test_direct_MetaUpdateCampaignStatusTool.py

