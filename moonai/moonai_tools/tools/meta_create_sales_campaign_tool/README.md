# MetaCreateSalesCampaignTool

## Description
The MetaCreateSalesCampaignTool is a Python-based tool designed to automate the creation of Meta (Facebook) Ads campaigns with Campaign Budget Optimization (CBO). By leveraging structured input files and organized directories, this tool simplifies the process of setting up multiple ad sets and ads within a single campaign, ensuring consistency and efficiency in your advertising efforts.



# Table of Contents
# Features
# Prerequisites
# Installation
# Setup
    Directory Structure
    Creating Directories and Files
# Configuration
    Environment Variables
    Configuration Files
# Usage
    Running the Tool
    Example
# Arguments
# Output Format
# Error Handling
# Additional Examples
# Best Practices
# Recommendations
# Security Considerations
# Contributing
# License


# Features
    Automated Campaign Creation: Streamlines the setup of Meta Ads campaigns with predefined budgets and objectives.
    Multiple Ad Sets and Ads: Easily create multiple ad sets and ads within a single campaign.
    Structured Input: Utilizes organized directories and files for managing ad creatives and configurations.
    Error Handling: Comprehensive validation and error messages to guide users through setup issues.
    Extensible: Easily extendable to accommodate additional features or integrations.

# Prerequisites
Before using the MetaCreateSalesCampaignTool, ensure you have the following:

    Python 3.7+: Ensure Python is installed on your system. You can download it from python.org.
    Facebook Business SDK: Required for interacting with Meta's Ads API.
    Pydantic: For input validation.
    dotenv: For managing environment variables.
    Meta/Facebook Ads Account: Access credentials for your Meta Ads account.


# Installation

## Clone the Repository:

```bash
git clone https://github.com/brunobracaioli/moonai.git
cd moonai
```

## Create a Virtual Environment (Optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Install Required Packages:

```bash
pip install -r requirements.txt
```

Ensure requirements.txt includes packages like facebook-business, pydantic, and python-dotenv.

# Setup
## Directory Structure
Organize your files and directories as follows to ensure the tool functions correctly:

meta_campaign_create_info/
├── ad_account_id.txt
├── orcamento.txt
├── objective.txt
├── male.txt
├── female.txt
├── age_min.txt
├── age_max.txt
├── interesses.json
├── publicos_adicionados.json
├── publicos_excluidos.json
├── quantidade_de_conjuntos.txt
├── quantidade_de_anuncios.txt
├── anuncio_1/
│   ├── titulo.txt
│   ├── copy.txt
│   ├── link.txt
│   ├── descricao.txt
│   ├── facebook_page.txt
│   ├── instagram_account.txt
│   └── photo/
│       └── imagem1.jpg
├── anuncio_2/
│   ├── titulo.txt
│   ├── copy.txt
│   ├── link.txt
│   ├── descricao.txt
│   ├── facebook_page.txt
│   ├── instagram_account.txt
│   └── photo/
│       └── imagem2.png
├── anuncio_3/
│   ├── titulo.txt
│   ├── copy.txt
│   ├── link.txt
│   ├── descricao.txt
│   ├── facebook_page.txt
│   ├── instagram_account.txt
│   └── photo/
│       └── imagem3.jpg
├── anuncio_4/
│   ├── titulo.txt
│   ├── copy.txt
│   ├── link.txt
│   ├── descricao.txt
│   ├── facebook_page.txt
│   ├── instagram_account.txt
│   └── photo/
│       └── imagem4.png
└── anuncio_5/
    ├── titulo.txt
    ├── copy.txt
    ├── link.txt
    ├── descricao.txt
    ├── facebook_page.txt
    ├── instagram_account.txt
    └── photo/
        └── imagem5.jpg

# Creating Directories and Files
Use the provided script to create the necessary directories and placeholder files.

## Create the Setup Script:

    Save the following script as create_directory_structure.py:

    ```python
    # create_directory_structure.py

    import os
    import json

    def criar_meta_campaign_create_info():
        # Define the main folder name
        nome_pasta = "meta_campaign_create_info"
        
        # Define subfolders
        subpastas = [
            "anuncio_1/photo",
            "anuncio_2/photo",
            "anuncio_3/photo",
            "anuncio_4/photo",
            "anuncio_5/photo"
        ]
        
        # Define TXT files
        arquivos_txt = [
            "ad_account_id.txt",
            "orcamento.txt",
            "male.txt",
            "female.txt",
            "age_min.txt",
            "age_max.txt",
            "anuncio_1/titulo.txt",
            "anuncio_1/copy.txt",
            "anuncio_1/link.txt",
            "anuncio_1/descricao.txt",
            "anuncio_1/facebook_page.txt",
            "anuncio_1/instagram_account.txt",
            "quantidade_de_conjuntos.txt",
            "quantidade_de_anuncios.txt",
            "anuncio_2/titulo.txt",
            "anuncio_2/copy.txt",
            "anuncio_2/link.txt",
            "anuncio_2/descricao.txt",
            "anuncio_2/facebook_page.txt",
            "anuncio_2/instagram_account.txt",
            "anuncio_3/titulo.txt",
            "anuncio_3/copy.txt",
            "anuncio_3/link.txt",
            "anuncio_3/descricao.txt",
            "anuncio_3/facebook_page.txt",
            "anuncio_3/instagram_account.txt",
            "anuncio_4/titulo.txt",
            "anuncio_4/copy.txt",
            "anuncio_4/link.txt",
            "anuncio_4/descricao.txt",
            "anuncio_4/facebook_page.txt",
            "anuncio_4/instagram_account.txt",
            "anuncio_5/titulo.txt",
            "anuncio_5/copy.txt",
            "anuncio_5/link.txt",
            "anuncio_5/descricao.txt",
            "anuncio_5/facebook_page.txt",
            "anuncio_5/instagram_account.txt"
        ]
        
        # Define JSON files with their respective names
        arquivos_json = {
            "interesses.json": [],
            "publicos_adicionados.json": [],
            "publicos_excluidos.json": []
        }

        # Create the main folder
        os.makedirs(nome_pasta, exist_ok=True)
        print(f"Main folder '{nome_pasta}' created.")

        # Create subfolders
        for subpasta in subpastas:
            caminho_subpasta = os.path.join(nome_pasta, subpasta)
            os.makedirs(caminho_subpasta, exist_ok=True)
            print(f"Subfolder '{caminho_subpasta}' created.")

        # Create empty TXT files
        for arquivo in arquivos_txt:
            caminho_arquivo = os.path.join(nome_pasta, arquivo)
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write("")  # Write initial content if necessary
            print(f"File '{caminho_arquivo}' created.")

        # Create empty JSON files
        for arquivo, conteudo in arquivos_json.items():
            caminho_arquivo = os.path.join(nome_pasta, arquivo)
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(conteudo, f, ensure_ascii=False, indent=4)
            print(f"JSON file '{caminho_arquivo}' created.")

    if __name__ == "__main__":
        criar_meta_campaign_create_info()
    ```

## Execute the Script to Create Directories and Files:

    ```bash
    python create_campaign_meta.py
    ```
    This script will create the directory structure and necessary files with empty content that you can populate with appropriate information.

    # Configuration
    ## Configure the necessary credentials to access the Facebook Ads API. Create a .env file in the root of your project with the following content:

    ```env
    ACCESS_TOKEN=your_facebook_access_token
    APP_SECRET=your_facebook_app_secret
    APP_ID=your_facebook_app_id
    PIXEL_ID=your_facebook_pixel_id
    ```

## Notes:

ACCESS_TOKEN: Your Meta access token.
APP_SECRET: Your Meta app secret.
APP_ID: Your Meta app ID.
PIXEL_ID: Your associated Facebook Pixel ID.

Ensure that this file is kept secure and not shared publicly.

# Configuration Files

Fill in the configuration files within the meta_campaign_create_info/ folder with the necessary information:

    ad_account_id.txt: Your Facebook Ads account ID (e.g., act_1234567890).
    orcamento.txt: Daily budget for the campaign (in cents, e.g., 5000 for $50.00).
    objective.txt: Campaign objective (e.g., CONVERSIONS).
    male.txt and female.txt: Male and female gender IDs, respectively (e.g., 1 for male, 2 for female).
    age_min.txt and age_max.txt: Target age range (e.g., 18 and 65).
    interesses.json: List of interests in JSON format.
    publicos_adicionados.json: List of custom audiences to include.
    publicos_excluidos.json: List of custom audiences to exclude.
    quantidade_de_conjuntos.txt: Number of ad sets to create (e.g., 2).
    quantidade_de_anuncios.txt: Number of ads per ad set (e.g., 3).

Within each anuncio_{j}/ folder, fill in the following files:

    titulo.txt: Ad title.
    copy.txt: Ad copy text.
    link.txt: Destination URL for the ad.
    descricao.txt: Ad description.
    facebook_page.txt: Associated Facebook Page ID.
    instagram_account.txt: Associated Instagram Account ID.
    photo/: Directory containing the ad image (imagem1.jpg, imagem2.png, etc.).

# Usage
## Running the Tool
After configuring the files and directories, execute the test script to start the campaign creation process.

## Create the Test Script:

Save the following script as test_direct_MetaCreateSalesCampaignTool.py:

```python
# test_direct_MetaCreateSalesCampaignTool.py

from moonai.moonai_tools.tools.meta_create_sales_campaign_tool.meta_create_sales_campaign_tool import MetaCreateSalesCampaignTool
from dotenv import load_dotenv
import os

# Load environment variables if necessary
load_dotenv()

# Paths to configuration files
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
anuncios_photo_directory = "meta_campaign_create_info/"  # Base for ad folders
anuncios_creative_directory = "meta_campaign_create_info/"  # Base for ad folders

# Initialize the tool with the file paths
create_campaign_tool = MetaCreateSalesCampaignTool()

# Execute the tool by passing the correct arguments
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

# Display the result
print(result)

# To run the test, use:
# python test_direct_MetaCreateSalesCampaignTool.py
```

## Execute the Test Script:

```bash
python test_direct_MetaCreateSalesCampaignTool.py
```
## Expected Output:

```yaml
Campaign created successfully. ID: 123456789012345
Ad set created successfully. ID: 678901234567890
Creative created successfully. ID: 112233445566778
Ad created successfully. ID: 223344556677889
Ad set created successfully. ID: 678901234567891
Creative created successfully. ID: 112233445566779
Ad created successfully. ID: 223344556677880
Created Campaign ID: 123456789012345
```


# Example
Assuming you have filled out all the necessary configuration files and images, running the tool should create a new Meta Ads campaign with the specified ad sets and ads. Here's a step-by-step example:

## Fill Out Configuration Files:

    ad_account_id.txt: act_1234567890
    orcamento.txt: 5000 (Represents $50.00 if budget is in cents)
    objective.txt: CONVERSIONS
    male.txt: 1
    female.txt: 2
    age_min.txt: 18
    age_max.txt: 65
    interesses.json:
    ```json
    [
        {"id": "6003139266461", "name": "Fitness and wellness"},
        {"id": "6003139266462", "name": "Nutrition"}
    ]
    ```
    publicos_adicionados.json:
    ```json
    [
        {"id": "1234567890", "name": "Custom Audience 1"}
    ]
    ```
    quantidade_de_conjuntos.txt: 2
    quantidade_de_anuncios.txt: 3

# Prepare Ad Creatives:

## Ad 1 (anuncio_1/):
    titulo.txt: Special Offer
    copy.txt: Take advantage of our exclusive offer!
    link.txt: https://yoursite.com/offer
    descricao.txt: Buy now and save.
    facebook_page.txt: 123456789012345
    instagram_account.txt: instagram_actor_id_1
    photo/imagem1.jpg: (Your ad image)

## Ad 2 (anuncio_2/):
    titulo.txt: Summer Discount
    copy.txt: Incredible discounts for this summer!
    link.txt: https://yoursite.com/summer
    descricao.txt: Don't miss this opportunity.
    facebook_page.txt: 123456789012345
    instagram_account.txt: instagram_actor_id_2
    photo/imagem2.png: (Your ad image)

(Repeat for additional ads as necessary)

## Execute the Test Script:

```bash
python test_direct_MetaCreateSalesCampaignTool.py
```
You should see an output confirming the successful creation of the campaign, ad sets, creatives, and ads.


# Arguments
    ad_account_id_file: Required. A string representing the path to the file containing the Ad Account ID. Example:

    ```python
    "meta_campaign_create_info/ad_account_id.txt"
    ```

    orcamento_file: Required. A string representing the path to the file containing the campaign budget (in cents). Example:

    ```python
    "meta_campaign_create_info/orcamento.txt"
    ```

    objective_file: Required. A string representing the path to the file containing the campaign objective. Example:

    ```python
    "meta_campaign_create_info/objective.txt"
    ```
    genders_male_file: Required. A string representing the path to the file containing the male gender ID. Example:
    
    ```python
    "meta_campaign_create_info/male.txt"
    ```

    genders_female_file: Required. A string representing the path to the file containing the female gender ID. Example:

    ```python
    "meta_campaign_create_info/female.txt"
    ```
    age_min_file: Required. A string representing the path to the file containing the target minimum age. Example:
    
    ```python
    "meta_campaign_create_info/age_min.txt"
    ```
    age_max_file: Required. A string representing the path to the file containing the target maximum age. Example:
    
    ```python
    "meta_campaign_create_info/age_max.txt"
    ```

    interests_file: Required. A string representing the path to the JSON file containing interests. Example:

    ```python
    "meta_campaign_create_info/interesses.json"
    ```

    custom_audiences_file: Required. A string representing the path to the JSON file containing custom audiences to include. Example:

    ```python
    "meta_campaign_create_info/publicos_adicionados.json"
    ```

    excluded_custom_audiences_file: Required. A string representing the path to the JSON file containing custom audiences to exclude. Example:

    ```python
    "meta_campaign_create_info/publicos_excluidos.json"
    ```

    quantidade_de_conjuntos_file: Required. A string representing the path to the file containing the number of ad sets to create. Example:

    ```python
    "meta_campaign_create_info/quantidade_de_conjuntos.txt"
    ```

    quantidade_de_anuncios_file: Required. A string representing the path to the file containing the number of ads per ad set. Example:

    ```python
    "meta_campaign_create_info/quantidade_de_anuncios.txt"
    ```

    anuncios_photo_directory: Required. A string representing the path to the directory containing ad photos. Example:

    ```python
    "meta_campaign_create_info/"
    ```

    anuncios_creative_directory: Required. A string representing the path to the directory containing ad creative files. Example:

    ```python
    "meta_campaign_create_info/"
    ```

# Output Format
The tool returns a string indicating the success of operations or detailing any errors encountered during the process. The possible outputs include:

## Success:
```yaml
Campaign created successfully. ID: 123456789012345
Ad set created successfully. ID: 678901234567890
Creative created successfully. ID: 112233445566778
Ad created successfully. ID: 223344556677889
Ad set created successfully. ID: 678901234567891
Creative created successfully. ID: 112233445566779
Ad created successfully. ID: 223344556677880
Created Campaign ID: 123456789012345
```

## Input Validation Errors:
```javascript
Input validation error: 2 validation errors for MetaCreateSalesCampaignToolSchema
titulo_file
  Field required [type=missing, input_value={'ad_account_id_file': 'meta_campaign_create_info/ad_account_id.txt', ...}, input_type=dict]
copy_file
  Field required [type=missing, input_value={'ad_account_id_file': 'meta_campaign_create_info/ad_account_id.txt', ...}, input_type=dict]
...
```

## Errors During Campaign Creation:
```yaml
Error creating campaign: <error_details>
```

## Errors During Ad Creation:
```yaml
Error creating ad: <error_details>
```


# Error Handling
The tool handles various error scenarios to ensure robustness:

## Missing Credentials
If the necessary credentials (ACCESS_TOKEN, APP_SECRET, APP_ID, PIXEL_ID) are not found in the environment variables, the tool returns:

```javascript
Error: Facebook Ads credentials not found.
```

## Invalid File or Directory Paths
If a specified file or directory does not exist, the tool returns:

```yaml
Error: The file 'meta_campaign_create_info/ad_account_id.txt' does not exist.
```

```yaml
Error: The directory 'meta_campaign_create_info/' does not exist.
```

# JSON Decoding Errors
If a JSON file is improperly formatted, the tool returns:

```javascript
Error: Failed to decode JSON - <error_details>
```

## Errors During File Reading
If there's an issue reading a file, the tool returns:

```yaml
Erro ao ler arquivos do anúncio 3: <error_details>
```

## API Errors
Any errors returned by the Facebook Ads API during campaign or ad creation will be captured and returned to the user:

```javascript
Error creating sales campaign: <error_details>
```

# Additional Examples
## Creating Multiple Ads

```python
from moonai.moonai_tools.tools.meta_create_sales_campaign_tool.meta_create_sales_campaign_tool import MetaCreateSalesCampaignTool
from dotenv import load_dotenv
import os

# Load environment variables if necessary
load_dotenv()

# Paths to configuration files
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
anuncios_photo_directory = "meta_campaign_create_info/"  # Base for ad folders
anuncios_creative_directory = "meta_campaign_create_info/"  # Base for ad folders

# Initialize the tool with the file paths
create_campaign_tool = MetaCreateSalesCampaignTool()

# Execute the tool by passing the correct arguments
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

# Display the result
print(result)
```

## Expected Output:
```yaml
Campaign created successfully. ID: 123456789012345
Ad set created successfully. ID: 678901234567890
Creative created successfully. ID: 112233445566778
Ad created successfully. ID: 223344556677889
Ad set created successfully. ID: 678901234567891
Creative created successfully. ID: 112233445566779
Ad created successfully. ID: 223344556677880
Created Campaign ID: 123456789012345
```


# Handling Invalid Entries

```python
from moonai.moonai_tools.tools.meta_create_sales_campaign_tool.meta_create_sales_campaign_tool import MetaCreateSalesCampaignTool
from dotenv import load_dotenv
import os

# Load environment variables if necessary
load_dotenv()

# Paths to configuration files
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
anuncios_photo_directory = "meta_campaign_create_info/"  # Base for ad folders
anuncios_creative_directory = "meta_campaign_create_info/"  # Base for ad folders

# Initialize the tool with the file paths
create_campaign_tool = MetaCreateSalesCampaignTool()

# Execute the tool by passing the correct arguments
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

# Display the result
print(result)
```

## Expected Output with Errors:

```yaml
Error reading ad files for ad 3: <error_details>
```

# Best Practices
    Secure Credential Management: Use environment variables or secure secret management services to store your Facebook Ads credentials. Avoid hardcoding them in your scripts or exposing them in version control systems.
    Data Validation: Always verify that the values provided in the configuration files are valid to prevent errors during campaign creation.
    Monitor Updates: After executing the tool, review the output logs to ensure all operations were performed as expected.
    Backup Configurations: Before performing bulk updates, consider backing up your current campaign configurations to restore them if necessary.


# Recommendations
    Implement Logging: For better control and flexibility over logging, consider using Python's logging library instead of relying solely on return messages.

    Example of Implementing Logging:

    ```python
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    class MetaCreateSalesCampaignTool(BaseTool):
        # ... previous code ...

        def _run(self, **kwargs: Any) -> str:
            try:
                # ... previous code ...
                logging.info(f"Campaign created successfully. ID: {campaign['id']}")
                # ... rest of the code ...
            except Exception as e:
                logging.error(f"Error creating sales campaign: {str(e)}")
                return f"Error creating sales campaign: {str(e)}"
    ```
    Automate Testing: Use testing frameworks like pytest to create automated tests for the tool, ensuring it handles various scenarios gracefully.

    Validate Environment Variables: Before initializing the Facebook Ads API, ensure that all required environment variables are present and valid.

    Enhance Error Messages: Provide more detailed error messages to assist users in troubleshooting issues effectively.

    Keep Documentation Updated: Maintain the documentation with any future changes to the tool to ensure users have accurate and helpful information.

    Support Multiple Status Formats: Consider supporting different status formats and provide clear instructions on the expected input to accommodate diverse user needs.


# Security Considerations
    Protect Credentials: Never share or expose your Facebook Ads credentials (ACCESS_TOKEN, APP_SECRET, APP_ID, PIXEL_ID). Store them securely using environment variables or secret management tools.
    Restrict Access: Limit access to configuration files and directories containing sensitive information.
    Rigorous Validation: Implement strict validations on input files to prevent the execution of malicious or incorrect commands.

# Contributing

Contributions are welcome! Feel free to open issues or pull requests to improve this project.

    Fork the Repository

    Create a Feature Branch
    ```bash
    git checkout -b feature/YourFeature
    ```

    Commit Your Changes
    ```bash
    git commit -m "Add new feature"
    ```

    Push to the Branch
    ```bash
    git push origin feature/YourFeature
    ```

    Open a Pull Request

# License
This project is licensed under the MIT License.










