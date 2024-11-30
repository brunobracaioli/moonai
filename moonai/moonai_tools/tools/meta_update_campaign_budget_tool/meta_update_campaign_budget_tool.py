from typing import Any, Type, Dict, List
from pydantic import BaseModel, Field, ValidationError
import re
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApi
from datetime import datetime
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from ..base_tool import BaseTool

class MetaUpdateCampaignBudgetToolSchema(BaseModel):
    """Input schema for MetaUpdateCampaignBudgetTool."""
    file_path: str = Field(
        ...,
        description="Path to the file containing campaign budget updates. Each line should be in the format 'campaign_id,budget_value'. Example: '123456789012345,1000'"
    )

class MetaUpdateCampaignBudgetTool(BaseTool):
    name: str = "Update Campaign Budget Tool"
    description: str = "A tool that updates the budgets of specified Meta (Facebook) Ads campaigns based on provided campaign IDs and new budget values."
    args_schema: Type[BaseModel] = MetaUpdateCampaignBudgetToolSchema

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
            budget_updates = self._read_budget_updates(file_path)

            if not budget_updates:
                return "Nenhuma atualização de orçamento encontrada no arquivo especificado."

            # Limpar os dados de budget
            budget_updates_limpos = self._limpar_budget(budget_updates)

            if not budget_updates_limpos:
                return "Nenhuma atualização de orçamento válida encontrada após a limpeza."

            # Atualizar as campanhas com base na lista limpa
            resultado = self._atualizar_campanhas(budget_updates_limpos)

            return resultado

        except Exception as e:
            return f"Error updating campaign budgets: {str(e)}"

    def _read_budget_updates(self, file_path: str) -> List[str]:
        """
        Lê o arquivo especificado e retorna uma lista de strings no formato 'campaign_id,budget_value'.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            budget_updates = [line.strip() for line in lines if line.strip()]
            return budget_updates
        except Exception as e:
            raise Exception(f"Erro ao ler o arquivo '{file_path}': {e}")

    def _limpar_budget(self, budget_updates: List[str]) -> List[str]:
        """
        Limpa a lista de atualizações de budget, extraindo apenas as partes 'ID,valor' de qualquer posição na linha.
        Retorna uma lista de linhas válidas no formato 'campaign_id,budget_value'.
        """
        try:
            budget_updates_limpos = []
            for linha in budget_updates:
                # Procurar pelo padrão ID,valor onde ambos são números, em qualquer parte da linha
                match = re.search(r'(\d{15,}),(\d+(\.\d+)?)', linha)
                if match:
                    id_, value = match.groups()[:2]
                    budget_updates_limpos.append(f"{id_},{value}")
                    print(f"Linha limpa: '{id_},{value}'")
                else:
                    print(f"Linha ignorada durante a limpeza: '{linha}'")
            return budget_updates_limpos
        except Exception as e:
            raise Exception(f"Erro ao limpar os dados de budget: {e}")

    def _atualizar_campanhas(self, budget_updates: List[str]) -> str:
        """
        Atualiza o orçamento e o nome das campanhas com base na lista de atualizações limpas.
        """
        try:
            # Obter a data atual no formato DD/MM/AA
            current_date_str = datetime.now().strftime("%d/%m/%y")

            resultados = []

            # Iterar sobre cada linha do arquivo e atualizar o orçamento e o nome da campanha correspondente
            for line_number, line in enumerate(budget_updates, start=1):
                try:
                    campaign_id, budget_value_str = line.split(',', 1)
                    campaign_id = campaign_id.strip()
                    budget_value_str = budget_value_str.strip()

                    # Substituir ',' por '.' se necessário
                    budget_value_str = budget_value_str.replace(',', '.')

                    # Converter para Decimal
                    try:
                        budget_value_decimal = Decimal(budget_value_str)
                    except InvalidOperation:
                        resultados.append(f"Linha {line_number}: Erro - O valor do orçamento '{budget_value_str}' não é um número válido. Verifique o conteúdo do arquivo.\n")
                        continue

                    # Multiplicar por 100 e por 1.30
                    final_budget_decimal = (budget_value_decimal * Decimal('100') * Decimal('1.30')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                    final_budget = int(final_budget_decimal)

                    # Inicializar o objeto da campanha
                    campaign = Campaign(campaign_id)

                    # Atualizar o orçamento da campanha
                    self._update_campaign_budget(campaign, final_budget, resultados)

                    # Atualizar o nome da campanha
                    self._update_campaign_name(campaign, current_date_str, resultados)

                except ValueError:
                    resultados.append(f"Linha {line_number}: Erro - Formato inválido. Cada linha deve estar no formato 'campaign_id,budget_value'.\n")
                except Exception as e:
                    resultados.append(f"Linha {line_number}: Erro inesperado: {e}\n")

            # Consolidar os resultados
            if resultados:
                return "\n".join(resultados)
            else:
                return "Atualização das campanhas concluída com sucesso."

        except Exception as e:
            return f"Erro ao atualizar as campanhas: {str(e)}"

    def _update_campaign_budget(self, campaign: Campaign, budget_value: int, resultados: List[str]):
        """
        Atualiza o orçamento diário da campanha.
        """
        try:
            # Atualizar a campanha com o novo orçamento e campos obrigatórios
            params = {
                Campaign.Field.daily_budget: budget_value,
                Campaign.Field.special_ad_categories: [],  # Use ['NONE'] se necessário
            }

            campaign.update(params)
            campaign.remote_update()  # Enviar a atualização para a API

            resultados.append(f"Orçamento atualizado para {budget_value} na campanha {campaign.get_id()} com sucesso.")

            # Confirmar se o orçamento foi atualizado consultando a API
            updated_campaign = Campaign(campaign.get_id()).api_get(fields=[Campaign.Field.daily_budget])
            resultados.append(f"Confirmação via API - Orçamento atual: {updated_campaign[Campaign.Field.daily_budget]})\n")

        except Exception as e:
            resultados.append(f"Erro ao atualizar o orçamento da campanha {campaign.get_id()}: {e}\n")

    def _update_campaign_name(self, campaign: Campaign, current_date_str: str, resultados: List[str]):
        """
        Atualiza o nome da campanha adicionando uma tag com a data da edição do orçamento.
        """
        try:
            # Buscar os dados atuais da campanha
            campaign.remote_read(fields=['name'])
            current_name = campaign['name']

            # Remover qualquer tag existente de orçamento editado
            if "[Orçamento editado em" in current_name:
                new_name = current_name.split("[Orçamento editado em")[0].strip()
            else:
                new_name = current_name

            # Adicionar a nova tag com a data atual
            new_name += f" [Orçamento editado em {current_date_str}]"

            # Preparar os parâmetros para atualização apenas do nome
            params = {
                'name': new_name
            }

            # Atualizar a campanha com o novo nome
            campaign.update(params)
            campaign.remote_update()  # Enviar a atualização para a API

            resultados.append(f"Nome da campanha {campaign.get_id()} atualizado para: '{new_name}' com sucesso.\n")

        except Exception as e:
            resultados.append(f"Erro ao atualizar o nome da campanha {campaign.get_id()}: {e}\n")
