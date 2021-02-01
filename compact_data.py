# %%
import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType
import pyspark.sql.functions as F

import logging
import argparse

# %%
DATA_DIR = 'data'
CHARTS_DATA_DIR = f'{DATA_DIR}/charts'
TRACKS_DATA_DIR = f'{DATA_DIR}/tracks'
ARTISTS_DATA_DIR = f'{DATA_DIR}/artists'
PARQUET_DATA_DIR = f'{DATA_DIR}/parquets'

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
        .load(f"{CHARTS_DATA_DIR}/*.csv")
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

    logging.info("Writing PARQUET chart.parquet")
    chart_data \
        .repartition(50) \
        .write \
        .mode('overwrite') \
        .parquet(f'{PARQUET_DATA_DIR}/chart.parquet')
    logging.info("PARQUET saved!")

    return chart_data


# %%
def generate_trackid_list(spark, chart_data):
    logging.info("Preparing TrackID list")
    track_id = chart_data.select('TrackID').distinct().toPandas()
    track_id.to_csv(f'{DATA_DIR}/track_ids.csv', header=True, index=False)
    logging.info("TrackIDs list done.")


# %%
def compact_track_data(spark):
    logging.info("Loading audio feature data")
    audio_features = spark \
        .read \
        .format("json") \
        .load(f"{TRACKS_DATA_DIR}/*.json")
    logging.info("Audio features loaded!")

    logging.info("Saving track_audio_features.parquet")
    audio_features \
        .repartition(50) \
        .write \
        .mode('overwrite') \
        .option('header', 'true') \
        .parquet(f'{PARQUET_DATA_DIR}/track_audio_features.parquet')
    logging.info("track_audio_features.parquet saved")


# &&
def compact_artist_data(spark):
    logging.info("Loading artists data")
    artist = spark \
        .read \
        .format("json") \
        .load(f"{ARTISTS_DATA_DIR}/*.json")
    logging.info("Audio artists data loaded!")

    logging.info("Saving artist.parquet")
    artist \
        .repartition(50) \
        .write \
        .mode('overwrite') \
        .option('header', 'true') \
        .parquet('artist.parquet')
    logging.info(f"{PARQUET_DATA_DIR}artist.parquet saved")


# %%
if __name__ == '__main__':
    args = parser.parse_args()
    spark = SparkSession.builder \
        .master("local") \
        .appName("Spotify Charts Compact Data") \
        .getOrCreate()

    if args.task == 'charts':
        cdata = compact_charts_data(spark)
        generate_trackid_list(spark, cdata)

    if args.task == 'tracks':
        compact_track_data(spark)
        compact_artist_data(spark)
