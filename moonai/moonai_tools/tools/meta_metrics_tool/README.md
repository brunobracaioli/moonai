# MetaMetricsTool

## Description
The MetaMetricsTool is designed to fetch and analyze metrics from active Meta (Facebook) Ads campaigns. It provides comprehensive insights including spend, CPC, CTR, impressions, and more, making it valuable for monitoring and analyzing ad performance across multiple campaigns.

# Installation
```shell
pip install 'moonai.moonai_tools'
```

# Prerequisites
Set these environment variables:

access_token=<your_meta_access_token>
app_secret=<your_app_secret>
app_id=<your_app_id>
ad_account_id=<your_ad_account_id>

# Example
```python
from moonai.moonai_tools import MetaMetricsTool

# Initialize tool with default 7-day analysis period
meta_metrics_tool = MetaMetricsTool()

# Execute with custom days parameter
result = meta_metrics_tool._run(days=30)

# Arguments

days: Number of days to analyze (default: 7)
```

# Output Format
Returns a dictionary containing:

report: Formatted text report
data: Raw campaign metrics
totals: Aggregated statistics