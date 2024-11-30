from moonai.moonai_tools import MetaCreateSalesCampaignTool
from moonai import Agent, Mission, Squad
from dotenv import load_dotenv

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

meta_tool = MetaCreateSalesCampaignTool()

campaign_creator = Agent(
    role="Meta ads campaign builder",
    goal=f"Activate the MetaCreateSalesCampaignTool tool using the parameters {ad_account_id_file}, {orcamento_file}, {objective_file},"
    f"{genders_male_file}, {genders_female_file}, {age_min_file}, {age_max_file}, {interests_file}, {custom_audiences_file}, {excluded_custom_audiences_file},"
    f"{quantidade_de_conjuntos_file}, {quantidade_de_anuncios_file}, {anuncios_photo_directory}, {anuncios_creative_directory}",
    backstory="Specialist in activating the MetaCreateSalesCampaignTool tool",
    llm="gpt-4o-mini",
    verbose=True,
    tools=[meta_tool]
)

create_campaign = Mission(
    description=f"Activate the MetaCreateSalesCampaignTool tool using the parameters {ad_account_id_file}, {orcamento_file}, {objective_file},"
    f"{genders_male_file}, {genders_female_file}, {age_min_file}, {age_max_file}, {interests_file}, {custom_audiences_file}, {excluded_custom_audiences_file},"
    f"{quantidade_de_conjuntos_file}, {quantidade_de_anuncios_file}, {anuncios_photo_directory}, {anuncios_creative_directory}",
    expected_output="confirmation of campaign creation",
    agent=campaign_creator,
    tools=[meta_tool]
)

squad = Squad(
    agents=[campaign_creator],
    missions=[create_campaign],
    verbose=True
)

squad.kickoff()

# python test_MetaCreateSalesCampaignTool.py