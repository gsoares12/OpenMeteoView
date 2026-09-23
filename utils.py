import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests


class WeatherLocation:
    """
        Representa uma localidade com seu nome, região e coordenadas geográficas.
    """
    def __init__(self, name: str, region: str, latitude: float, longitude: float):
        self.name = name
        self.region = region
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"WeatherLocation({self.name}, {self.region})"


class OpenMeteoFetcher:
    """Gerencia a conexão com a API Open-Meteo e extrai dados meteorológicos."""
    URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, cache_name: str = '.cache', expire_after: int = 3600, retries: int = 5):
        # Inicializa o cliente da API com cache e retração (retry)
        cache_session = requests_cache.CachedSession(cache_name, expire_after=expire_after)
        retry_session = retry(cache_session, retries=retries, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)

    def fetch_hourly_temperature(self, location: WeatherLocation, start_date: str, end_date: str) -> pd.DataFrame:
        """Busca a temperatura horária de uma única localidade e retorna um DataFrame."""
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "hourly": "temperature_2m",
            "timezone": "America/Sao_Paulo",
            "start_date": start_date,
            "end_date": end_date,
        }

        # Faz a requisição à API
        responses = self.client.weather_api(self.URL, params=params)
        response = responses[0]

        # Processa os dados horários
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        # Cria a estrutura temporal
        dates = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ).tz_convert(response.Timezone().decode())

        # Monta o DataFrame final
        df = pd.DataFrame({
            "date": dates,
            "temperature_2m": hourly_temperature_2m,
            "region": location.region,
            "city": location.name
        })
        
        return df
    
    def fetch_multiple_locations(self, locations: list[WeatherLocation], start_date: str, end_date: str) -> list[pd.DataFrame]:

        """
            Itera por uma lista de localidades, buscando e consolidando os DataFrames.
        """
        list_df = []
        
        for loc in locations:
            print(f"Região: {loc.region} | Capital: {loc.name} | Localização: ({loc.latitude}, {loc.longitude})")
            try:
                df = self.fetch_hourly_temperature(loc, start_date, end_date)
                list_df.append(df)
            except Exception as e:
                print(f"Erro ao buscar dados para {loc.name}: {e}")
                
        return list_df



# Adicione isso ao seu utils.py
import os
import json
import pandas as pd

class DataExporter:
    """
        Responsável por exportar listas de DataFrames ou dicionários para múltiplos formatos.
    """
    
    @staticmethod
    def to_csv(df_list: list[pd.DataFrame], output_path: str) -> None:
        """Consolida os DataFrames e salva em um único arquivo CSV."""
        if not df_list:
            print("Nenhum dado para salvar em CSV.")
            return
        
        # Consolida todos os DataFrames da lista em um só
        df_final = pd.concat(df_list, ignore_index=True)
        df_final.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Dados salvos com sucesso em CSV: {output_path}")

    @staticmethod
    def to_excel(df_list: list[pd.DataFrame], output_path: str) -> None:
        """Consolida os DataFrames e salva em um arquivo Excel (.xlsx)."""
        if not df_list:
            print("Nenhum dado para salvar em Excel.")
            return
            
        df_final = pd.concat(df_list, ignore_index=True)
        df_final.to_excel(output_path, index=False)
        print(f"Dados salvos com sucesso em Excel: {output_path}")

    @staticmethod
    def to_json(df_list: list[pd.DataFrame], output_path: str, orient: str = "records") -> None:
        """Consolida os DataFrames e salva em formato JSON estruturado."""
        if not df_list:
            print("Nenhum dado para salvar em JSON.")
            return
            
        df_final = pd.concat(df_list, ignore_index=True)
        
        # Converte as datas para string para evitar problemas de serialização no JSON
        df_final['date'] = df_final['date'].astype(str)
        
        df_final.to_json(output_path, orient=orient, indent=4, force_ascii=False)
        print(f"Dados salvos com sucesso em JSON: {output_path}")
