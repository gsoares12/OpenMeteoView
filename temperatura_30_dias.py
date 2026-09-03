from datetime import date, timedelta

import matplotlib.pyplot as plt
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry


def connect_api_meteo(
	latitude=-19.9208,
	longitude=-43.9378,
	start_date=None,
	end_date=None,
):
	"""Conecta à API Open-Meteo e solicita as temperaturas horárias."""
	end_date = end_date or date.today()
	start_date = start_date or (end_date - timedelta(days=30))

	cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
	retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
	openmeteo = openmeteo_requests.Client(session=retry_session)

	params = {
		"latitude": latitude,
		"longitude": longitude,
		"hourly": "temperature_2m",
		"timezone": "America/Sao_Paulo",
		"start_date": start_date.isoformat(),
		"end_date": end_date.isoformat(),
	}
	return openmeteo.weather_api(
		"https://api.open-meteo.com/v1/forecast", params=params
	)


def create_dataframe():
	"""Converte a resposta da API em um DataFrame horário."""
	response = connect_api_meteo()[0]
	hourly = response.Hourly()

	hourly_data = {
		"date": pd.date_range(
			start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
			end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
			freq=pd.Timedelta(seconds=hourly.Interval()),
			inclusive="left",
		).tz_convert(response.Timezone().decode())
	}
	hourly_data["temperature_2m"] = hourly.Variables(0).ValuesAsNumpy()
	return pd.DataFrame(data=hourly_data)


def transform_data(df):
	"""Agrupa os dados por dia e calcula a temperatura média arredondada."""
	transformed = (
		df.groupby(df["date"].dt.strftime("%Y-%m-%d"))["temperature_2m"]
		.mean()
		.round()
		.astype(int)
		.reset_index(name="temperature")
	)
	transformed["date"] = pd.to_datetime(transformed["date"])
	return transformed


def plot_temperature(df):
	"""Exibe a variação da temperatura média diária."""
	background_color = "#000000"
	text_color = "#f8fafc"
	secondary_text_color = "#fbfcfd"
	line_color = "#55b0c0"

	fig, ax = plt.subplots(figsize=(18, 6), facecolor=background_color)
	ax.set_facecolor(background_color)
	ax.plot(
		df["date"],
		df["temperature"],
		color=line_color,
		linewidth=2.5,
		label="Temperatura (°C)",
		marker="o",
		markersize=5,
		markerfacecolor=background_color,
		markeredgewidth=2,
	)
	ax.set_title(
		"Variação de Temperatura nos Últimos 30 Dias",
		fontsize=16,
		fontweight="bold",
		color=text_color,
		pad=20,
	)
	ax.set_ylabel("Temperatura (°C)", fontsize=13, color=text_color, labelpad=10)
	ax.set_xticks(df["date"])
	ax.set_xticklabels(
		df["date"].dt.strftime("%d/%m"),
		rotation=45,
		ha="right",
		fontsize=13,
		color=secondary_text_color,
	)
	ax.tick_params(axis="y", colors=secondary_text_color, labelsize=10)
	ax.grid(True, linestyle=":", alpha=0.15, color=text_color)

	for spine in ["top", "right", "left", "bottom"]:
		ax.spines[spine].set_visible(False)

	ax.legend(
		facecolor=background_color,
		edgecolor="none",
		labelcolor=text_color,
		loc="upper right",
	)
	plt.tight_layout()
	return plt.show()


def main():
	"""Executa a coleta, transformação e visualização dos dados."""
	dataframe = create_dataframe()
	daily_data = transform_data(dataframe)
	plot_temperature(daily_data)


if __name__ == "__main__":
	main()
