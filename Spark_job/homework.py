import os
from pathlib import Path

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as f
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, DoubleType


dim_columns = ['id', 'name']

payment_rows = [
    (1, 'Credit card'),
    (2, 'Cash'),
    (3, 'No charge'),
    (4, 'Dispute'),
    (5, 'Unknown'),
    (6, 'Voided trip'),
]

trips_schema = StructType([
    StructField('vendor_id', StringType(), True),
    StructField('tpep_pickup_datetime', TimestampType(), True),
    StructField('tpep_dropoff_datetime', TimestampType(), True),
    StructField('passenger_count', IntegerType(), True),
    StructField('trip_distance', DoubleType(), True),
    StructField('ratecode_id', IntegerType(), True),
    StructField('store_and_fwd_flag', StringType(), True),
    StructField('pulocation_id', IntegerType(), True),
    StructField('dolocation_id', IntegerType(), True),
    StructField('payment_type', IntegerType(), True),
    StructField('fare_amount', DoubleType(), True),
    StructField('extra', DoubleType(), True),
    StructField('mta_tax', DoubleType(), True),
    StructField('tip_amount', DoubleType(), True),
    StructField('tolls_amount', DoubleType(), True),
    StructField('improvement_surcharge', DoubleType(), True),
    StructField('total_amount', DoubleType(), True),
    StructField('congestion_surcharge', DoubleType()),
])

def create_dict(spark: SparkSession, header: list[str], data: list):
    df = spark.createDataFrame(data=data, schema=header)
    return df


def agg_calc(spark: SparkSession) -> DataFrame:
    data_path = os.path.join(Path(__name__).parent, './data', 'yellow_tripdata_2020-01.csv')

    trip_fact = spark.read \
        .option("header", "true") \
        .schema(trips_schema) \
        .csv(data_path)

    datamart = trip_fact \
        .where((trip_fact['vendor_id'].isNotNull())
               &
               (f.month(f.to_date(trip_fact['tpep_pickup_datetime'])) == 1)
               &
               (f.year(f.to_date(trip_fact['tpep_pickup_datetime'])) == 2020)
            )\
        .groupBy(trip_fact['payment_type'],
                 f.to_date(trip_fact['tpep_pickup_datetime']).alias('Date')
                 ) \
        .agg(f.round(f.avg(trip_fact['total_amount']),2).alias('Average trip cost'),
             f.round((f.sum(trip_fact['total_amount']) / f.sum(trip_fact['trip_distance'])),2).alias("Avg trip km cost")) \
        .select(f.col('payment_type'),
                f.col('Date'),
                f.col('Average trip cost'),
                f.col('Avg trip km cost')) \
        .orderBy(f.col('Date').desc(), f.col('payment_type'))

    return datamart


def main(spark: SparkSession):
    payment_dim = create_dict(spark, dim_columns, payment_rows)

    datamart = agg_calc(spark).cache()

    joined_datamart = datamart \
        .join(other=payment_dim, on=payment_dim['id'] == f.col('payment_type'), how='inner') \
        .select(payment_dim['name'].alias('Payment type'),
                f.col('Date'),
                f.col('Average trip cost'),
                f.col('Avg trip km cost')
                ) \
        .sort(f.col('Date').desc(), f.col('Payment type').asc())


    joined_datamart.show(truncate=False, n=20000)

    joined_datamart.repartition(1).write.mode('overwrite').csv('output_homework')



if __name__ == '__main__':
    main(SparkSession
         .builder
         .appName('My homework spark job')
         .getOrCreate())
