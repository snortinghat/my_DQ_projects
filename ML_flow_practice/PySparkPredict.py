import argparse
import os

from pyspark.sql import SparkSession

import mlflow

os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://storage.yandexcloud.net'
os.environ['AWS_ACCESS_KEY_ID'] = '33kU43UzyCYfV1jgKUPL'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'WPZnfkNEOlpdZ32hwVGhQ6PNiPPjmFZEajnWUMRe'

def process(spark, data_path, result):
    """
    Основной процесс задачи.

    :param spark: SparkSession
    :param data_path: путь до датасета
    :param result: путь сохранения результата
    """
    df = spark.read.parquet(data_path)
    model = mlflow.spark.load_model("s3://kc-mlflow/88/2b3733cdc046401e87cc435add690e0d/artifacts/a-tskhay")
    prediction = model.transform(df)
    prediction.write.mode('overwrite').parquet(result)


def main(data, result):
    spark = _spark_session()
    process(spark, data, result)


def _spark_session():
    """
    Создание SparkSession.

    :return: SparkSession
    """
    return SparkSession.builder.appName('PySparkPredict').getOrCreate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data.parquet', help='Please set datasets path.')
    parser.add_argument('--result', type=str, default='result', help='Please set result path.')
    args = parser.parse_args()
    data = args.data
    result = args.result
    main(data, result)
