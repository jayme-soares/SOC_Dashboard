import base64
import pandas as pd

# Nome do arquivo Excel que você quer converter
# Certifique-se de que este script e a pasta 'base de dados' estejam no mesmo local.
caminho_do_arquivo = 'base de dados/base.xlsx'
nome_do_secret = 'EXCEL_BASE64'
nome_arquivo_saida = 'secret_para_copiar.txt'

try:
    # Abre o arquivo em modo de leitura de bytes
    with open(caminho_do_arquivo, "rb") as f:
        # Codifica o conteúdo do arquivo para Base64
        base64_string = base64.b64encode(f.read()).decode()

    # Cria a string completa no formato que o Streamlit espera
    conteudo_para_salvar = f'{nome_do_secret} = "{base64_string}"'

    # Salva a string em um arquivo de texto
    with open(nome_arquivo_saida, "w") as f_out:
        f_out.write(conteudo_para_salvar)

    print(f"Conversão bem-sucedida! O secret foi salvo no arquivo '{nome_arquivo_saida}'.")
    print("\nAbra este arquivo, copie todo o seu conteúdo e cole nos Secrets do seu app no Streamlit Cloud.")


except FileNotFoundError:
    print(f"Erro: O arquivo '{caminho_do_arquivo}' não foi encontrado. Verifique o caminho.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")

