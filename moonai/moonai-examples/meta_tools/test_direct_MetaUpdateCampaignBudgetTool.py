# test_direct_MetaUpdateCampaignBudgetTool.py

from moonai.moonai_tools import MetaUpdateCampaignBudgetTool
from dotenv import load_dotenv

# Carregar variáveis de ambiente, se necessário
load_dotenv()

# Inicializar a ferramenta
meta_tool = MetaUpdateCampaignBudgetTool()

# Definir o caminho para o arquivo contendo as atualizações de orçamento
file_path = "campaign.txt"  # Pode ser um caminho relativo ou absoluto

# Executar a ferramenta passando o caminho do arquivo
result = meta_tool._run(file_path=file_path)

# Exibir o resultado
print(result)

# Para executar o teste, use:
# python test_direct_MetaUpdateCampaignBudgetTool.py

