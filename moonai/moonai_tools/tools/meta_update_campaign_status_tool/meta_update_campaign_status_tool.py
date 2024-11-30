# moonai/moonai_tools/tools/meta_update_campaign_status_tool/meta_update_campaign_status_tool.py

from typing import Any, Type, Dict, List
from pydantic import BaseModel, Field, ValidationError
import re
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApi
from datetime import datetime
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from ..base_tool import BaseTool

class MetaUpdateCampaignStatusToolSchema(BaseModel):
    """Input schema for MetaUpdateCampaignStatusTool."""
    file_path: str = Field(
        ...,
        description="Path to the file containing campaign status updates. Each line should be in the format 'campaign_id,desired_status'. Example: '123456789012345,PAUSED'"
    )

class MetaUpdateCampaignStatusTool(BaseTool):
    name: str = "Update Campaign Status Tool"
    description: str = "A tool that updates the statuses of specified Meta (Facebook) Ads campaigns based on provided campaign IDs and desired statuses."
    args_schema: Type[BaseModel] = MetaUpdateCampaignStatusToolSchema

    def _run(self, **kwargs: Any) -> str:
        try:
            # Validar e extrair os argumentos de entrada
            try:
                input_data = self.args_schema(**kwargs)
            except ValidationError as ve:
                return f"Input validation error: {ve}"

            file_path = input_data.file_path

            if not os.path.isfile(file_path):
                return f"Error: The file '{file_path}' does not exist."

            # Extrair credenciais do ambiente
            access_token = os.getenv("ACCESS_TOKEN")
            app_secret = os.getenv("APP_SECRET")
            app_id = os.getenv("APP_ID")
            api_version = 'v21.0'  # Especificar a versão da API

            if not all([access_token, app_secret, app_id]):
                return "Error: Facebook Ads credentials not found."

            # Inicializar a API do Facebook
            FacebookAdsApi.init(app_id=app_id, app_secret=app_secret, access_token=access_token, api_version=api_version)

            # Processar o arquivo de atualizações
            status_updates = self._read_status_updates(file_path)

            if not status_updates:
                return "Nenhuma atualização de status encontrada no arquivo especificado."

            # Limpar os dados de status
            status_updates_limpos = self._limpar_status(status_updates)

            if not status_updates_limpos:
                return "Nenhuma atualização de status válida encontrada após a limpeza."

            # Atualizar as campanhas com base na lista limpa
            resultado = self._atualizar_campanhas(status_updates_limpos)

            return resultado

        except Exception as e:
            return f"Error updating campaign statuses: {str(e)}"

    def _read_status_updates(self, file_path: str) -> List[str]:
        """
        Lê o arquivo especificado e retorna uma lista de strings no formato 'campaign_id,desired_status'.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            status_updates = [line.strip() for line in lines if line.strip()]
            return status_updates
        except Exception as e:
            raise Exception(f"Erro ao ler o arquivo '{file_path}': {e}")

    def _limpar_status(self, status_updates: List[str]) -> List[str]:
        """
        Limpa a lista de atualizações de status, extraindo apenas as partes 'campaign_id,desired_status' de qualquer posição na linha.
        Retorna uma lista de linhas válidas no formato 'campaign_id,desired_status'.
        """
        try:
            status_updates_limpos = []
            for linha in status_updates:
                # Procurar pelo padrão campaign_id,desired_status onde campaign_id é numérico e desired_status é uma string válida
                match = re.search(r'(\d{15,}),([A-Z]+)', linha)
                if match:
                    campaign_id, desired_status = match.groups()
                    status_updates_limpos.append(f"{campaign_id},{desired_status}")
                    print(f"Linha limpa: '{campaign_id},{desired_status}'")
                else:
                    print(f"Linha ignorada durante a limpeza: '{linha}'")
            return status_updates_limpos
        except Exception as e:
            raise Exception(f"Erro ao limpar os dados de status: {e}")

    def _atualizar_campanhas(self, status_updates: List[str]) -> str:
        """
        Atualiza o status das campanhas com base na lista de atualizações limpas.
        """
        try:
            resultados = []

            # Lista de status válidos conforme a documentação
            valid_statuses = {"ACTIVE", "PAUSED", "DELETED", "ARCHIVED"}

            # Iterar sobre cada linha do arquivo e atualizar o status correspondente
            for line_number, line in enumerate(status_updates, start=1):
                try:
                    campaign_id, desired_status = line.split(',', 1)
                    campaign_id = campaign_id.strip()
                    desired_status = desired_status.strip().upper()

                    # Validar se o desired_status é válido
                    if desired_status not in valid_statuses:
                        resultados.append(f"Linha {line_number}: Erro - Status inválido '{desired_status}'. Status válidos são: {valid_statuses}\n")
                        continue

                    # Inicializar o objeto da campanha
                    campaign = Campaign(campaign_id)

                    # Atualizar o status da campanha
                    self._update_campaign_status(campaign, desired_status, resultados)

                except ValueError:
                    resultados.append(f"Linha {line_number}: Erro - Formato inválido. Cada linha deve estar no formato 'campaign_id,desired_status'.\n")
                except Exception as e:
                    resultados.append(f"Linha {line_number}: Erro inesperado: {e}\n")

            # Consolidar os resultados
            if resultados:
                return "\n".join(resultados)
            else:
                return "Atualização dos status das campanhas concluída com sucesso."

        except Exception as e:
            return f"Erro ao atualizar os status das campanhas: {str(e)}"

    def _update_campaign_status(self, campaign: Campaign, desired_status: str, resultados: List[str]):
        """
        Atualiza o status de uma campanha.
        """
        try:
            # Atualizar a campanha com o novo status e campos obrigatórios
            params = {
                Campaign.Field.status: desired_status,
                Campaign.Field.special_ad_categories: [],  # Use ['NONE'] se necessário
            }

            campaign.update(params)
            campaign.remote_update()  # Enviar a atualização para a API

            resultados.append(f"Status da campanha {campaign.get_id()} atualizado com sucesso para {desired_status}.")

            # Confirmar se o status foi atualizado consultando a API
            updated_campaign = Campaign(campaign.get_id()).api_get(fields=[Campaign.Field.status, Campaign.Field.special_ad_categories])
            resultados.append(f"Confirmação via API - Status atual: {updated_campaign.get(Campaign.Field.status)}")
            resultados.append(f"Special Ad Categories: {updated_campaign.get(Campaign.Field.special_ad_categories, [])}\n")

        except Exception as e:
            resultados.append(f"Erro ao atualizar o status da campanha {campaign.get_id()}: {e}\n")
