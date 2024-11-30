# create_campaign_meta.py

import os
import json

def criar_meta_campaign_create_info():
    # Definir o nome da pasta principal
    nome_pasta = "meta_campaign_create_info"
    
    # Definir subpastas
    subpastas = [
        "anuncio_1/photo",
        "anuncio_2/photo",
        "anuncio_3/photo",
        "anuncio_4/photo",
        "anuncio_5/photo"
    ]
    
    # Definir arquivos TXT
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
    
    # Definir arquivos JSON com seus respectivos nomes
    arquivos_json = {
        "interesses.json": {},
        "publicos_adicionados.json": {},
        "publicos_excluidos.json": {}
    }
    
    try:
        # Criar a pasta principal se não existir
        os.makedirs(nome_pasta, exist_ok=True)
        print(f"Pasta '{nome_pasta}' criada ou já existente.")
        
        # Criar subpastas dentro da pasta principal
        for subpasta in subpastas:
            caminho_subpasta = os.path.join(nome_pasta, subpasta)
            os.makedirs(caminho_subpasta, exist_ok=True)
            print(f"Subpasta '{subpasta}' criada ou já existente em '{nome_pasta}'.")
        
        # Caminho absoluto da pasta principal
        caminho_pasta = os.path.abspath(nome_pasta)
        
        # Criar arquivos TXT dentro da pasta principal
        for nome_arquivo in arquivos_txt:
            caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
            with open(caminho_arquivo, 'w') as arquivo:
                pass  # Cria um arquivo vazio
            print(f"Arquivo '{nome_arquivo}' criado em '{nome_pasta}'.")
        
        # Criar arquivos JSON dentro da pasta principal
        for nome_arquivo, conteudo in arquivos_json.items():
            caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
            with open(caminho_arquivo, 'w') as arquivo:
                json.dump(conteudo, arquivo, indent=4)  # Cria um JSON vazio
            print(f"Arquivo JSON '{nome_arquivo}' criado em '{nome_pasta}'.")
        
        print("Todos os arquivos e subpastas foram criados com sucesso.")
        
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    criar_meta_campaign_create_info()
