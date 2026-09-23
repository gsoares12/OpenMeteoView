# Esse script será uma segunda versão do script com algumas melhorias em vista do temperatura_30_dias.py
# Nessa segunda versão terá todos os estados do brasil para extração de temperaturas, capturando pela capital, o range de datas também será maior.



# 1. IMPORTANDO AS CLASSES DO SEU ARQUIVO UTILS
from utils import WeatherLocation, OpenMeteoFetcher, DataExporter
import pandas as pd

# --- INSTANCIAÇÃO E EXECUÇÃO DO CÓDIGO (MAIN) ---
if __name__ == "__main__":
    # Dados brutos estruturados para facilitar a conversão em objetos
    dados_regioes = {
        "Nordeste": {
            "Aracaju (SE)": (-10.9472, -37.0731), "Barreiras (BA)": (-12.1545, -44.9912),
            "Fortaleza (CE)": (-3.7172, -38.5434), "João Pessoa (PB)": (-7.1153, -34.861),
            "Maceió (AL)": (-9.6658, -35.735), "Natal (RN)": (-5.7945, -35.211),
            "Recife (PE)": (-8.0476, -34.877), "Salvador (BA)": (-12.9714, -38.5014),
            "São Luís (MA)": (-2.5297, -44.3028), "Teresina (PI)": (-5.0892, -42.8016)
        },
        "Norte": {
            "Belém (PA)": (-1.4558, -48.5039), "Boa Vista (RR)": (2.8196, -60.6733),
            "Macapá (AP)": (0.0349, -51.0694), "Manaus (AM)": (-3.1019, -60.025),
            "Palmas (TO)": (-10.184, -48.333), "Porto Velho (RO)": (-8.7608, -63.900),
            "Rio Branco (AC)": (-9.9747, -67.8105)
        },
        "Centro-Oeste": {
            "Brasília (DF)": (-15.601, -56.097), "Campo Grande (MS)": (-20.4697, -54.6201),
            "Cuiabá (MT)": (-15.6010, -56.0967), "Goiânia (GO)": (-16.6869, -49.2648)
        },
        "Sul": {
            "Curitiba (PR)": (-25.4290, -49.2671), "Florianópolis (SC)": (-27.5954, -48.5480),
            "Porto Alegre (RS)": (-30.0346, -51.2177)
        },
        "Sudeste": {
            "São Paulo (SP)": (-23.5505, -46.6333), "Rio de Janeiro (RJ)": (-22.9064, -43.1729),
            "Belo Horizonte (MG)": (-19.9281, -43.9419), "Vitória (ES)": (-20.3194, -40.3472)
        }
    }


    # 2. INSTANCIANDO OS OBJETOS DE LOCALIDADE
    lista_localidades = []
    for regiao, cidades in dados_regioes.items():
        for nome_cidade, coords in cidades.items():
            # Criamos uma instância passando os argumentos obrigatórios do __init__
            objeto_localidade = WeatherLocation(
                name=nome_cidade, 
                region=regiao, 
                latitude=coords[0], 
                longitude=coords[1]
            )
            lista_localidades.append(objeto_localidade)

    # 3. INSTANCIANDO O CLIENTE DA API
    fetcher = OpenMeteoFetcher()

    # 4. EXECUTANDO O MÉTODO
    lista_df_estado = fetcher.fetch_multiple_locations(
        locations=lista_localidades, 
        start_date="2026-07-01", 
        end_date="2026-09-23"
    )

    print(f"\nSucesso! {len(lista_df_estado)} DataFrames foram gerados.")

    # 5. UTILIZANDO A CLASSE EXPORTER PARA SALVAR OS ARQUIVOS
    if lista_df_estado:        
        
        # Salvando em JSON
        DataExporter.to_json(lista_df_estado, "temperaturas_capitais.json")