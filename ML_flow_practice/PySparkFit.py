import argparse
import os

from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.tuning import TrainValidationSplit, ParamGridBuilder
from pyspark.sql import SparkSession
from pyspark.ml.classification import GBTClassifier
import mlflow

LABEL_COL = 'has_car_accident'

os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://storage.yandexcloud.net'
os.environ['AWS_ACCESS_KEY_ID'] = '33kU43UzyCYfV1jgKUPL'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'WPZnfkNEOlpdZ32hwVGhQ6PNiPPjmFZEajnWUMRe'


def build_pipeline(train_alg):
    """
    Создание пайплаина над выбранной моделью.

    :return: Pipeline
    """
    sex_indexer = StringIndexer(inputCol='sex',
                                outputCol="sex_index")
    car_class_indexer = StringIndexer(inputCol='car_class',
                                      outputCol="car_class_index")
    features = ["age", "sex_index", "car_class_index", "driving_experience",
                "speeding_penalties", "parking_penalties", "total_car_accident"]
    assembler = VectorAssembler(inputCols=features, outputCol='features')
    return Pipeline(stages=[sex_indexer, car_class_indexer, assembler, train_alg])


def evaluate_model(evaluator, predict, metric_list):
    for metric in metric_list:
        evaluator.setMetricName(metric)
        score = evaluator.evaluate(predict)
        print(f"{metric} score = {score}")
        mlflow.log_metric(metric, score)


def optimization(pipeline, gbt, train_df, evaluator):
    grid = ParamGridBuilder() \
        .addGrid(gbt.maxDepth, [3, 5]) \
        .addGrid(gbt.maxIter, [20, 30]) \
        .addGrid(gbt.maxBins, [16, 32]) \
        .build()
    tvs = TrainValidationSplit(estimator=pipeline,
                               estimatorParamMaps=grid,
                               evaluator=evaluator,
                               trainRatio=0.8)
    models = tvs.fit(train_df)
    return models.bestModel


def process(spark, train_path, test_path):
    """
    Основной процесс задачи.

    :param spark: SparkSession
    :param train_path: путь до тренировочного датасета
    :param test_path: путь до тренировочного датасета
    """
    evaluator = MulticlassClassificationEvaluator(labelCol=LABEL_COL, predictionCol="prediction", metricName='f1')
    train_df = spark.read.parquet(train_path)
    test_df = spark.read.parquet(test_path)

    gbt = GBTClassifier(labelCol=LABEL_COL)
    pipeline = build_pipeline(gbt)

    model = optimization(pipeline, gbt, train_df, evaluator)
    predict = model.transform(test_df)

    evaluate_model(evaluator, predict, ['f1', 'weightedPrecision', 'weightedRecall', 'accuracy'])
    print('Best model saved')

    # Logging

    mlflow.log_param('input_columns', train_df.columns)
    mlflow.log_param('maxDepth', model.stages[-1].getMaxDepth())
    mlflow.log_param('maxIter', model.stages[-1].getMaxIter())
    mlflow.log_param('maxBins', model.stages[-1].getMaxBins())
    mlflow.log_param('target', model.stages[-1].getLabelCol())
    mlflow.log_param('features', model.stages[-1].getFeaturesCol())

    for i in range(0, len(model.stages)):
        stage = model.stages[i]
        mlflow.log_param(f'stage_{i}', stage)

    mlflow.spark.log_model(model,
                           artifact_path="a-tskhay",
                           registered_model_name="a-tskhay")


def main(train_path, test_path):
    mlflow.set_tracking_uri("https://mlflow.lab.karpov.courses")
    mlflow.set_experiment(experiment_name="a-tskhay")
    spark = _spark_session()
    mlflow.start_run()
    process(spark, train_path, test_path)
    mlflow.end_run()

def _spark_session():
    """
    Создание SparkSession.

    :return: SparkSession
    """
    return SparkSession.builder.appName('PySparkMLJob').getOrCreate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', type=str, default='train.parquet', help='Please set train datasets path.')
    parser.add_argument('--test', type=str, default='test.parquet', help='Please set test datasets path.')
    args = parser.parse_args()
    train = args.train
    test = args.test
    main(train, test)
