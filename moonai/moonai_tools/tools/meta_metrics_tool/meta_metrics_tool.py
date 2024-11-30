# brunobracaioli/moonai_tools/tools/meta_metrics_tool/meta_metrics_tool.py

from typing import Any, Type, Dict
from pydantic import BaseModel, Field
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from datetime import datetime, timedelta
import os

from ..base_tool import BaseTool

class MetaMetricsToolSchema(BaseModel):
    """Input for MetaMetricsTool."""
    days: int = Field(default=7, description="Number of days to analyze")

class MetaMetricsTool(BaseTool):
    name: str = "Meta Ads Metrics Tool"
    description: str = "A tool that fetches metrics from active Meta (Facebook) Ads campaigns."
    args_schema: Type[BaseModel] = MetaMetricsToolSchema

    def _run(self, **kwargs: Any) -> str:
        try:
            days = kwargs.get('days', 7)
            access_token = os.getenv("ACCESS_TOKEN")
            app_secret = os.getenv("APP_SECRET")
            app_id = os.getenv("APP_ID")
            ad_account_id = os.getenv("AD_ACCOUNT_ID")

            if not all([access_token, app_secret, app_id, ad_account_id]):
                return "Error: Facebook Ads credentials not found"

            FacebookAdsApi.init(app_id=app_id, app_secret=app_secret, access_token=access_token)
            account = AdAccount(f'act_{ad_account_id}')

            hoje = datetime.now().strftime('%Y-%m-%d')
            data_inicio = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            periodo = {'since': data_inicio, 'until': hoje}

            campanhas = account.get_campaigns(
                fields=['id', 'name', 'objective', 'daily_budget'],
                params={'effective_status': ['ACTIVE']}
            )

            if not campanhas:
                return "No active campaigns found."

            metricas = [
                AdsInsights.Field.spend,
                AdsInsights.Field.cpc,
                AdsInsights.Field.ctr,
                AdsInsights.Field.cpm,
                AdsInsights.Field.cost_per_unique_outbound_click,
                AdsInsights.Field.frequency,
                AdsInsights.Field.reach,
                AdsInsights.Field.impressions
            ]

            dados_analise = self._process_campaigns(campanhas, metricas, periodo)
            relatorio = self._generate_report(dados_analise, data_inicio, hoje)
            totais = self._calculate_totals(dados_analise) if dados_analise else {}

            return str({
                'report': relatorio,
                'data': dados_analise,
                'totals': totais
            })

        except Exception as e:
            return f"Error collecting metrics: {str(e)}"

    def _process_campaigns(self, campanhas, metricas, periodo) -> list:
        dados_analise = []
        for campanha in campanhas:
            insights = campanha.get_insights(fields=metricas, params={'time_range': periodo})
            if insights:
                dados_analise.append(self._extract_campaign_data(campanha, insights[0]))
        return dados_analise

    def _extract_campaign_data(self, campanha, metrica) -> Dict:
        return {
            'name': campanha['name'],
            'id': campanha.get('id', 'N/A'),
            'objective': campanha.get('objective', 'Not informed'),
            'budget': self._get_float_value(campanha.get('daily_budget', 0), 100),
            'spent': self._get_float_value(metrica.get('spend', 0)),
            'cpc': self._get_float_value(metrica.get('cpc', 0)),
            'ctr': self._get_float_value(metrica.get('ctr', 0)) * 100,
            'cpm': self._get_float_value(metrica.get('cpm', 0)),
            'cpa': self._get_float_value(metrica.get('cost_per_unique_outbound_click', 0)),
            'frequency': self._get_float_value(metrica.get('frequency', 0)),
            'range': self._get_int_value(metrica.get('reach', 0)),
            'impressions': self._get_int_value(metrica.get('impressions', 0))
        }

    def _generate_report(self, dados_analise: list, data_inicio: str, hoje: str) -> str:
        relatorio = f"\n=== META ADS METRICS ({data_inicio} to {hoje}) ===\n\n"
        
        for dados in dados_analise:
            relatorio += self._format_campaign_report(dados)
        
        if dados_analise:
            totais = self._calculate_totals(dados_analise)
            relatorio += self._format_totals_report(totais)
        
        return relatorio

    def _format_campaign_report(self, dados: Dict) -> str:
        return f"""📊 Campaign: {dados['name']}
🆔 ID: {dados['id']}
🎯 Objective: {dados['objective']}
💰 Daily Budget: R$ {dados['budget']:.2f}
💸 Total Spend: R$ {dados['spent']:.2f}
🎯 CPC: R$ {dados['cpc']:.2f}
📈 CTR: {dados['ctr']:.2f}%
📊 CPM: R$ {dados['cpm']:.2f}
💲 CPA: R$ {dados['cpa']:.2f}
🔄 Frequency: {dados['frequency']:.1f}
👥 Range: {dados['range']:,}
👀 Impressions: {dados['impressions']:,}
{'-' * 50}\n"""

    @staticmethod
    def _get_float_value(value, divisor=1):
        if isinstance(value, list):
            value = value[0] if value else 0
        try:
            return float(value) / divisor
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _get_int_value(value):
        if isinstance(value, list):
            value = value[0] if value else 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _calculate_totals(dados_analise: list) -> Dict:
        return {
            'campaigns': len(dados_analise),
            'budget_total': sum(d['budget'] for d in dados_analise),
            'total_spend': sum(d['spent'] for d in dados_analise),
            'total_range': sum(d['range'] for d in dados_analise),
            'total_impressions': sum(d['impressions'] for d in dados_analise),
            'ctr_average': sum(d['ctr'] for d in dados_analise) / len(dados_analise),
            'cpc_average': sum(d['cpc'] for d in dados_analise) / len(dados_analise),
            'cpa_average': sum(d['cpa'] for d in dados_analise) / len(dados_analise)
        }
    
    def _format_totals_report(self, totais: Dict) -> str:
        return f"""
    === GENERAL SUMMARY ===
    📊 Total Campaigns: {totais['campaigns']}
    💰 Total Daily Budget: R$ {totais['budget_total']:.2f}
    💸 Total Spend: R$ {totais['total_spend']:.2f}
    👥 Total Range: {totais['total_range']:,}
    👀 Total Impressions: {totais['total_impressions']:,}
    📈 Average CTR: {totais['ctr_average']:.2f}%
    🎯 Average CPC: R$ {totais['cpc_average']:.2f}
    💲 Average CPA: R$ {totais['cpa_average']:.2f}
    """