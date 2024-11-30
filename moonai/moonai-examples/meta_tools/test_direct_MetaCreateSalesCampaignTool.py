# test_direct_MetaCreateSalesCampaignTool.py

from moonai.moonai_tools.tools.meta_create_sales_campaign_tool.meta_create_sales_campaign_tool import MetaCreateSalesCampaignTool
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente, se necessário
load_dotenv()

# Caminhos para os arquivos de configuração
ad_account_id_file = "meta_campaign_create_info/ad_account_id.txt"
orcamento_file = "meta_campaign_create_info/orcamento.txt"
objective_file = "meta_campaign_create_info/objective.txt"
genders_male_file = "meta_campaign_create_info/male.txt"
genders_female_file = "meta_campaign_create_info/female.txt"
age_min_file = "meta_campaign_create_info/age_min.txt"
age_max_file = "meta_campaign_create_info/age_max.txt"
interests_file = "meta_campaign_create_info/interesses.json"
custom_audiences_file = "meta_campaign_create_info/publicos_adicionados.json"
excluded_custom_audiences_file = "meta_campaign_create_info/publicos_excluidos.json"
quantidade_de_conjuntos_file = "meta_campaign_create_info/quantidade_de_conjuntos.txt"
quantidade_de_anuncios_file = "meta_campaign_create_info/quantidade_de_anuncios.txt"
anuncios_photo_directory = "meta_campaign_create_info/"  # Base para pastas de anúncios
anuncios_creative_directory = "meta_campaign_create_info/"  # Base para pastas de anúncios

# Inicializar a ferramenta com os caminhos dos arquivos
create_campaign_tool = MetaCreateSalesCampaignTool()

# Executar a ferramenta passando os argumentos corretos
result = create_campaign_tool._run(
    ad_account_id_file=ad_account_id_file,
    orcamento_file=orcamento_file,
    objective_file=objective_file,
    genders_male_file=genders_male_file,
    genders_female_file=genders_female_file,
    age_min_file=age_min_file,
    age_max_file=age_max_file,
    interests_file=interests_file,
    custom_audiences_file=custom_audiences_file,
    excluded_custom_audiences_file=excluded_custom_audiences_file,
    quantidade_de_conjuntos_file=quantidade_de_conjuntos_file,
    quantidade_de_anuncios_file=quantidade_de_anuncios_file,
    anuncios_photo_directory=anuncios_photo_directory,
    anuncios_creative_directory=anuncios_creative_directory
)

# Exibir o resultado
print(result)

# Para executar o teste, use:
# python test_direct_MetaCreateSalesCampaignTool.py

