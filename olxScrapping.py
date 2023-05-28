#importações de bibliotecas
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import sleep
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
import datetime
from tqdm import tqdm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#configurações do driver
servico=Service(ChromeDriverManager().install())
timeespera=5
driver=webdriver.Chrome(service=servico)
driver.maximize_window()

# definindo olx pags
pagina=1
maxpagina = 99

# Começando Scrapping
for pagina in range(1, maxpagina+1):  #trocar depois para um botão de próx pagina...
    url = f'https://www.olx.com.br/imoveis/venda/estado-ce/fortaleza-e-regiao/fortaleza?o={pagina}'
    driver.get(url)
    sleep(timeespera + 5)
    
    # Definindo a lista geral
    listageral = driver.find_elements(By.ID, 'ad-list')[0]

    # Títulos
    titulos = listageral.find_elements(By.TAG_NAME, 'h2')
    tituloall = []
    for titulo in titulos:
        tituloall.append(titulo.text)
        
    # Preços
    precoT = listageral.find_elements(By.TAG_NAME, 'h3')
    precosall = []
    for precos in precoT:
        precosall.append(precos.text)

    # Locais
    locais = listageral.find_elements(By.CLASS_NAME, 'sc-eAKXzc')
    locaisall = []
    for local in locais:
        locaisall.append(local.text.split('\n')[0])

    # Detalhes da venda
    variosdetalhes = listageral.find_elements(By.CLASS_NAME, 'sc-jeCdPy')
    detalhesall = []
    for detalhes in variosdetalhes:
        partes = detalhes.find_elements(By.CLASS_NAME, 'sc-jtRlXQ')
        paux = []
        for parte in partes:
            paux.append(parte.find_element(By.TAG_NAME, 'span').get_attribute('aria-label'))
        detalhesall.append(paux)
    
    # IPTU e condomínio
    iptucond = listageral.find_elements(By.CLASS_NAME, 'price-info')
    iptucondall = []
    for infosV in iptucond:
        info = infosV.text.split('\n')
        iptu = 'NULL'
        condominio = 'NULL'
        for i in range(len(info)):
            if 'IPTU' in info[i]:
                iptu = info[i]
            elif 'Condomínio' in info[i]:
                condominio = info[i]
        iptucondall.append(f"{iptu} / {condominio}")

    # Links 
    links = listageral.find_elements(By.CSS_SELECTOR, 'a[data-ds-component="DS-NewAdCard-Link"]')
    href_values = []
    for link in links:
        href_value = link.get_attribute('href')
        href_values.append(href_value)

    # Data de postagem
    postagem = listageral.find_elements(By.CLASS_NAME, 'date')
    postall = []
    for postagens in postagem:
        postall.append(postagens.text.split('\n')[0])

    # Verifica o comprimento de cada lista e adiciona "NULL" quando necessário
    length = max(len(tituloall), len(precosall), len(locaisall), len(detalhesall), len(iptucondall), len(postall), len(href_values))
    tituloall += ['NULL'] * (length - len(tituloall))
    precosall += ['NULL'] * (length - len(precosall))
    locaisall += ['NULL'] * (length - len(locaisall))
    detalhesall += [['NULL']] * (length - len(detalhesall))
    iptucondall += ['NULL'] * (length - len(iptucondall))
    postall += ['NULL'] * (length - len(postall))
    href_values += ['NULL'] * (length - len(href_values))

    if pagina == 1:
        df = pd.DataFrame({'TITULO': tituloall, 'PRECOS': precosall, 'DETALHES': detalhesall, 'LOCAL': locaisall, 'IPTU E CONDOMINIO': iptucondall, 'DATA DE POSTAGEM': postall, 'LINKS': href_values})
    else:
        dfaux = pd.DataFrame({'TITULO': tituloall, 'PRECOS': precosall, 'DETALHES': detalhesall, 'LOCAL': locaisall, 'IPTU E CONDOMINIO': iptucondall, 'DATA DE POSTAGEM': postall, 'LINKS': href_values})
        df = pd.concat([df, dfaux], axis=0, ignore_index=True)
    
    sleep(timeespera)

    print(f"Coleta de dados da página {pagina} concluída.")

driver.close()

# Filtro de duplicatas
df = df.drop_duplicates(subset=['TITULO', 'PRECOS', 'LOCAL', 'LINKS'])

# Adicionar coluna com a data de hoje
hoje = datetime.date.today()
data_formatada = hoje.strftime('%d/%m/%Y')
df['DATA DA COLETA'] = pd.to_datetime(data_formatada, format='%d/%m/%Y')

# Salvar o DataFrame em um arquivo Excel
nome_arquivo = 'dados_OLX.xlsx'  
df.to_excel(nome_arquivo, index=False)  

print(f"Dados {nome_arquivo} salvos com sucesso")

