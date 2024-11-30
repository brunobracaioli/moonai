# moonai/moonai_tools/tools/meta_create_sales_campaign_tool/meta_create_sales_campaign_tool.py

from typing import Any, Type, Dict, List
from pydantic import BaseModel, Field, ValidationError
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adimage import AdImage
from facebook_business.api import FacebookAdsApi
import os
import glob
import json

from ..base_tool import BaseTool

class MetaCreateSalesCampaignToolSchema(BaseModel):
    """Input schema for MetaCreateSalesCampaignTool."""
    ad_account_id_file: str = Field(
        ...,
        description="Path to the file containing the Ad Account ID."
    )
    orcamento_file: str = Field(
        ...,
        description="Path to the file containing the campaign budget."
    )
    objective_file: str = Field(
        ...,
        description="Path to the file containing the campaign objective."
    )
    genders_male_file: str = Field(
        ...,
        description="Path to the file containing the male gender ID."
    )
    genders_female_file: str = Field(
        ...,
        description="Path to the file containing the female gender ID."
    )
    age_min_file: str = Field(
        ...,
        description="Path to the file containing the minimum age."
    )
    age_max_file: str = Field(
        ...,
        description="Path to the file containing the maximum age."
    )
    interests_file: str = Field(
        ...,
        description="Path to the file containing interests in JSON format."
    )
    custom_audiences_file: str = Field(
        ...,
        description="Path to the file containing custom audiences in JSON format."
    )
    excluded_custom_audiences_file: str = Field(
        ...,
        description="Path to the file containing excluded custom audiences in JSON format."
    )
    quantidade_de_conjuntos_file: str = Field(
        ...,
        description="Path to the file containing the number of ad sets to create."
    )
    quantidade_de_anuncios_file: str = Field(
        ...,
        description="Path to the file containing the number of ads per ad set."
    )
    anuncios_photo_directory: str = Field(
        ...,
        description="Path to the directory containing ad photos."
    )
    anuncios_creative_directory: str = Field(
        ...,
        description="Path to the directory containing ad creative files."
    )

class MetaCreateSalesCampaignTool(BaseTool):
    name: str = "Create Sales Campaign Tool"
    description: str = "A tool that creates Meta (Facebook) Ads campaigns with CBO based on provided parameters and file inputs."
    args_schema: Type[BaseModel] = MetaCreateSalesCampaignToolSchema

    def _run(self, **kwargs: Any) -> str:
        try:
            # Validar e extrair os argumentos de entrada
            try:
                input_data = self.args_schema(**kwargs)
            except ValidationError as ve:
                return f"Input validation error: {ve}"

            # Extrair caminhos dos arquivos
            ad_account_id_file = input_data.ad_account_id_file
            orcamento_file = input_data.orcamento_file
            objective_file = input_data.objective_file
            genders_male_file = input_data.genders_male_file
            genders_female_file = input_data.genders_female_file
            age_min_file = input_data.age_min_file
            age_max_file = input_data.age_max_file
            interests_file = input_data.interests_file
            custom_audiences_file = input_data.custom_audiences_file
            excluded_custom_audiences_file = input_data.excluded_custom_audiences_file
            quantidade_de_conjuntos_file = input_data.quantidade_de_conjuntos_file
            quantidade_de_anuncios_file = input_data.quantidade_de_anuncios_file
            anuncios_photo_directory = input_data.anuncios_photo_directory
            anuncios_creative_directory = input_data.anuncios_creative_directory

            # Validar existência dos arquivos
            file_paths = [
                ad_account_id_file, orcamento_file, objective_file, genders_male_file,
                genders_female_file, age_min_file, age_max_file, interests_file,
                custom_audiences_file, excluded_custom_audiences_file
            ]

            for path in file_paths:
                if not os.path.isfile(path):
                    return f"Error: The file '{path}' does not exist."

            if not os.path.isdir(anuncios_photo_directory):
                return f"Error: The directory '{anuncios_photo_directory}' does not exist."

            if not os.path.isdir(anuncios_creative_directory):
                return f"Error: The directory '{anuncios_creative_directory}' does not exist."

            # Extrair credenciais do ambiente
            access_token = os.getenv("ACCESS_TOKEN")
            app_secret = os.getenv("APP_SECRET")
            app_id = os.getenv("APP_ID")
            pixel_id = os.getenv("PIXEL_ID")
            api_version = 'v21.0'  # Especificar a versão da API

            if not all([access_token, app_secret, app_id, pixel_id]):
                return "Error: Facebook Ads credentials not found."

            # Inicializar a API do Facebook
            FacebookAdsApi.init(app_id=app_id, app_secret=app_secret, access_token=access_token, api_version=api_version)

            # Ler ad_account_id e objective
            ad_account_id = self._read_file(ad_account_id_file)
            objective = self._read_file(objective_file)

            # Ler orçamento
            try:
                daily_budget = int(self._read_file(orcamento_file))
            except ValueError:
                return f"Error: O orçamento '{self._read_file(orcamento_file)}' não é um número válido."

            # Ler gêneros
            genders = self._read_genders(genders_male_file, genders_female_file)

            # Ler faixas etárias
            try:
                age_min = int(self._read_file(age_min_file))
                age_max = int(self._read_file(age_max_file))
            except ValueError:
                return f"Error: Os valores de idade mínima ou máxima não são números válidos."

            # Ler interesses e audiências
            try:
                interests = self._read_json_list(interests_file)
                custom_audiences = self._read_json_list(custom_audiences_file)
                excluded_custom_audiences = self._read_json_list(excluded_custom_audiences_file)
            except json.JSONDecodeError as je:
                return f"Error: Falha ao decodificar JSON - {je}"

            # Ler quantidade de conjuntos e anúncios
            try:
                quantidade_de_conjuntos = int(self._read_file(quantidade_de_conjuntos_file))
                quantidade_de_anuncios = int(self._read_file(quantidade_de_anuncios_file))
            except ValueError:
                return f"Error: As quantidades de conjuntos ou anúncios não são números válidos."

            # Iniciar criação da campanha
            resultados = []
            campaign = self.create_campaign(ad_account_id, daily_budget, objective, resultados)
            if not campaign:
                return "\n".join(resultados)

            # Iterar para criar conjuntos de anúncios e anúncios
            for i in range(quantidade_de_conjuntos):
                ad_set = self.create_ad_set(
                    ad_account_id, campaign['id'], genders, age_min, age_max,
                    interests, custom_audiences, excluded_custom_audiences, pixel_id, resultados, ad_set_name_suffix=f"_{i+1}"
                )
                if not ad_set:
                    continue
                for j in range(1, quantidade_de_anuncios + 1):
                    # Obter caminho do anúncio j
                    image_dir = os.path.join(anuncios_photo_directory, f'anuncio_{j}', 'photo')
                    creative_dir = os.path.join(anuncios_creative_directory, f'anuncio_{j}')
                    try:
                        image_path = self.get_single_file_path(image_dir)
                        titulo_j = self._read_file(os.path.join(creative_dir, 'titulo.txt'))
                        copy_j = self._read_file(os.path.join(creative_dir, 'copy.txt'))
                        link_j = self._read_file(os.path.join(creative_dir, 'link.txt'))
                        descricao_j = self._read_file(os.path.join(creative_dir, 'descricao.txt'))
                        facebook_page_j = self._read_file(os.path.join(creative_dir, 'facebook_page.txt'))
                        instagram_account_j = self._read_file(os.path.join(creative_dir, 'instagram_account.txt'))
                    except Exception as e:
                        resultados.append(f"Erro ao ler arquivos do anúncio {j}: {e}\n")
                        continue

                    # Criar creative
                    creative = self.create_ad_creative(
                        ad_account_id, image_path, titulo_j, copy_j, link_j,
                        descricao_j, facebook_page_j, instagram_account_j, j, resultados
                    )
                    if not creative:
                        continue

                    # Criar anúncio
                    ad = self.create_ad(ad_account_id, ad_set['id'], creative, resultados, ad_set_name_suffix=f"_{i+1}")
            
            resultados.append(f"Created Campaign ID: {campaign['id']}")
            return "\n".join(resultados)

        except Exception as e:
            return f"Error creating sales campaign: {str(e)}"

    # Métodos auxiliares (fora do método _run)
    def _read_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Erro ao ler o arquivo '{file_path}': {e}")

    def _read_json_list(self, file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                # Adiciona colchetes para formar uma lista JSON válida
                return json.loads(f"[{content}]")
        except Exception as e:
            raise Exception(f"Erro ao ler o arquivo JSON '{file_path}': {e}")

    def _read_genders(self, male_file: str, female_file: str) -> List[int]:
        genders = []
        male_gender = self._read_file(male_file)
        female_gender = self._read_file(female_file)
        if male_gender:
            try:
                genders.append(int(male_gender))
            except ValueError:
                raise Exception(f"Erro: O gênero masculino '{male_gender}' não é um número válido.")
        if female_gender:
            try:
                genders.append(int(female_gender))
            except ValueError:
                raise Exception(f"Erro: O gênero feminino '{female_gender}' não é um número válido.")
        return genders

    def get_single_file_path(self, directory: str) -> str:
        files = glob.glob(os.path.join(directory, '*'))
        if len(files) == 1:
            return files[0]
        else:
            raise Exception(f"Esperava encontrar apenas um arquivo em {directory}, mas encontrei {len(files)} arquivos.")

    def upload_image(self, account_id: str, image_path: str) -> str:
        try:
            image = AdImage(parent_id=account_id)
            image[AdImage.Field.filename] = image_path
            image.remote_create()
            return image[AdImage.Field.hash]
        except Exception as e:
            raise Exception(f"Erro ao fazer upload da imagem '{image_path}': {e}")

    def create_campaign(self, account_id: str, daily_budget: int, objective: str, resultados: List[str]) -> Campaign:
        try:
            campaign = Campaign(parent_id=account_id)
            campaign.update({
                Campaign.Field.name: 'Campanha CBO criada por equipes de IAs',
                Campaign.Field.status: Campaign.Status.active,
                Campaign.Field.objective: objective,
                'special_ad_categories': [],  # Array vazio
                Campaign.Field.daily_budget: daily_budget,  # Orçamento em centavos
                Campaign.Field.bid_strategy: 'LOWEST_COST_WITHOUT_CAP'  # Estratégia de lances para CBO
            })
            campaign.remote_create(params={'status': Campaign.Status.active})
            resultados.append(f"Campanha criada com sucesso. ID: {campaign['id']}")
            return campaign
        except Exception as e:
            resultados.append(f"Erro ao criar a campanha: {e}\n")
            return None

    def create_ad_set(self, account_id: str, campaign_id: str, genders: List[int],
                     age_min: int, age_max: int, interests: List[Dict],
                     custom_audiences: List[Dict], excluded_custom_audiences: List[Dict],
                     pixel_id: str, resultados: List[str], ad_set_name_suffix: str = "") -> AdSet:
        try:
            ad_set = AdSet(parent_id=account_id)
            ad_set.update({
                AdSet.Field.name: f'Test Ad Set {ad_set_name_suffix}',
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
                AdSet.Field.optimization_goal: AdSet.OptimizationGoal.offsite_conversions,
                AdSet.Field.destination_type: AdSet.DestinationType.website,
                AdSet.Field.targeting: {
                    'geo_locations': {'countries': ['BR']},
                    'genders': genders,
                    'age_min': age_min,
                    'age_max': age_max,
                    'publisher_platforms': ['instagram'],
                    'facebook_positions': ['feed', 'story'],
                    'instagram_positions': ['stream', 'story', 'reels', 'explore'],
                    'device_platforms': ['mobile', 'desktop'],
                    'interests': interests,
                    'custom_audiences': custom_audiences,
                    'excluded_custom_audiences': excluded_custom_audiences
                },
                AdSet.Field.promoted_object: {
                    'pixel_id': pixel_id,
                    'custom_event_type': 'PURCHASE'
                },
                AdSet.Field.status: AdSet.Status.active,
            })
            ad_set.remote_create(params={'status': AdSet.Status.active})
            resultados.append(f"Conjunto de anúncios criado com sucesso. ID: {ad_set['id']}")
            return ad_set
        except Exception as e:
            resultados.append(f"Erro ao criar o conjunto de anúncios: {e}\n")
            return None

    def create_ad_creative(self, account_id: str, image_path: str, titulo: str, copy: str,
                           link: str, descricao: str, facebook_page_id: str,
                           instagram_actor_id: str, ad_number: int, resultados: List[str]) -> AdCreative:
        try:
            # Determinar mimetype
            mimetype = 'image/png' if image_path.lower().endswith('.png') else 'image/jpeg'

            # Fazer upload da imagem
            image_hash = self.upload_image(account_id, image_path)

            creative = AdCreative(parent_id=account_id)
            creative.update({
                AdCreative.Field.name: f'Foto e copy gerada por Agentes GPT - Anúncio {ad_number}',
                AdCreative.Field.title: titulo,
                AdCreative.Field.body: copy,
                AdCreative.Field.object_story_spec: {
                    'page_id': facebook_page_id,
                    'instagram_actor_id': instagram_actor_id,
                    'link_data': {
                        'call_to_action': {'type': 'LEARN_MORE'},
                        'image_hash': image_hash,
                        'link': link,
                        'message': copy,
                        'name': titulo,
                        'description': descricao
                    }
                },
                AdCreative.Field.degrees_of_freedom_spec: {
                    'creative_features_spec': {
                        'standard_enhancements': {
                            'enroll_status': 'OPT_IN'
                        }
                    }
                }
            })
            creative.remote_create()
            resultados.append(f"Creative criado com sucesso. ID: {creative['id']}")
            return creative
        except Exception as e:
            resultados.append(f"Erro ao criar o creative: {e}\n")
            return None

    def create_ad(self, account_id: str, ad_set_id: str, creative: AdCreative,
                 resultados: List[str], ad_set_name_suffix: str = "") -> Ad:
        try:
            ad = Ad(parent_id=account_id)
            ad.update({
                Ad.Field.name: f'Test Ad {ad_set_name_suffix}',
                Ad.Field.adset_id: ad_set_id,
                Ad.Field.creative: {'creative_id': creative['id']},
                Ad.Field.status: Ad.Status.active,
            })
            ad.remote_create(params={'status': Ad.Status.active})
            resultados.append(f"Anúncio criado com sucesso. ID: {ad['id']}")
            return ad
        except Exception as e:
            resultados.append(f"Erro ao criar o anúncio: {e}\n")
            return None
