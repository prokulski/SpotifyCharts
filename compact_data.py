# %%
import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType
import pyspark.sql.functions as F

import logging
import argparse


# %%
logging.basicConfig(filename=f'{__file__}.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# %%
parser = argparse.ArgumentParser(usage='%(prog)s [task]')
parser.add_argument('task', choices=[
                    'charts', 'tracks'], help='what to compact from JSONs into PARQUETs?')


# %%
def compact_charts_data(spark):
    logging.info("Loading CSVs from data/")
    chart_data = spark \
        .read \
        .format("csv") \
        .option("header", "true") \
        .load("data/*.csv")
    logging.info("Loaded!")

    logging.info("Preprocessing data")
    chart_data = chart_data \
        .withColumnRenamed('Track Name', 'TrackName') \
        .withColumn('Position', chart_data['Position'].cast(IntegerType())) \
        .withColumn('Streams', chart_data['Streams'].cast(IntegerType())) \
        .filter(F.length(chart_data['Country']) == 2) \
        .select('Country', 'Date', 'Position', 'Artist', 'TrackName', 'TrackID', 'Streams') \
        .sort(chart_data.Country, chart_data.Date, chart_data.Position)
    logging.info("Data preprocessed!")

    logging.info("Writing PARQUET chart_data.parquet")
    chart_data \
        .repartition(50) \
        .write \
        .mode('overwrite') \
        .parquet('chart_data.parquet')
    logging.info("PARQUET saved!")


# %%
def generate_trackid_list(spark):
    logging.info("Preparing TrackID list")
    track_id = chart_data.select('TrackID').distinct().toPandas()
    track_id.to_csv('track_ids.csv', header=True, index=False)
    logging.info("TrackIDs list done.")


# %%
def compact_track_data(spark):
    logging.info("Loading audio feature data")
    audio_features = spark \
        .read \
        .format("json") \
        .load("track_data/*.json")
    logging.info("Audio features loaded!")

    logging.info("Saving track_audio_features.parquet")
    audio_features \
        .repartition(50) \
        .write \
        .mode('overwrite') \
        .option('header', 'true') \
        .parquet('track_audio_features.parquet')
    logging.info("track_audio_features.parquet saved")


# &&
def compact_artist_data(spark):
    logging.info("Loading artists data")
    audio_features = spark \
        .read \
        .format("json") \
        .load("artist_data/*.json")
    logging.info("Audio artists data loaded!")

    logging.info("Saving artist_data.parquet")
    audio_features \
        .repartition(50) \
        .write \
        .mode('overwrite') \
        .option('header', 'true') \
        .parquet('artist_data.parquet')
    logging.info("artist_data.parquet saved")


# %%
if __name__ == '__main__':
    args = parser.parse_args()
    spark = SparkSession.builder \
        .master("local") \
        .appName("SpotifyCharts Compact Data") \
        .getOrCreate()

    if args.task == 'charts':
        compact_charts_data(spark)
        generate_trackid_list(spark)

    if args.task == 'tracks':
        compact_track_data(spark)
        compact_artist_data(spark)
