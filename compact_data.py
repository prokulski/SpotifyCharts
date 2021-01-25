# %%
import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType
import pyspark.sql.functions as F

# %%
spark = SparkSession.builder \
    .master("local") \
    .appName("Spotify Load") \
    .getOrCreate()

# %%
df = spark \
    .read \
    .format("csv") \
    .option("header", "true") \
    .load("data/*.csv")

# %%
df = df \
    .withColumnRenamed('Track Name', 'TrackName') \
    .withColumn('Position', df['Position'].cast(IntegerType())) \
    .withColumn('Streams', df['Streams'].cast(IntegerType())) \
    .filter(F.length(df['Country']) == 2) \
    .select('Country', 'Date', 'Position', 'Artist', 'TrackName', 'TrackID', 'Streams') \
    .sort(df.Country, df.Date, df.Position)

# df.show()

# %%
df \
    .coalesce(1) \
    .write \
    .mode('overwrite') \
    .option('header', 'true') \
    .csv('output.csv')

# %%
track_id = df.select('TrackID').distinct().toPandas()
track_id.to_csv('track_ids.csv', header=True, index=False)
