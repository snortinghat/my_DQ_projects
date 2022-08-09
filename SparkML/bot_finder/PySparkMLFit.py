import operator
import argparse

from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.sql import SparkSession
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.classification import GBTClassifier

MODEL_PATH = 'spark_ml_model'
LABEL_COL = 'is_bot'


def process(spark, data_path, model_path):
    """
    Основной процесс задачи.

    :param spark: SparkSession
    :param data_path: путь до датасета
    :param model_path: путь сохранения обученной модели
    """

    df = spark.read.parquet(data_path)

    # Data preparation
    indexer_user_type = StringIndexer(inputCol="user_type", outputCol="user_type_index")
    indexer_platform = StringIndexer(inputCol="platform", outputCol="platform_index")
    features = ['user_type_index', 'duration', 'platform_index', 'item_info_events',
                'select_item_events', 'make_order_events', 'events_per_min']
    feature_assembler = VectorAssembler(inputCols=features, outputCol="features")

    # ML
    train, validation = df.randomSplit([0.8, 0.2])
    evaluator = MulticlassClassificationEvaluator(labelCol="is_bot", predictionCol="prediction", metricName="accuracy")
    rf_classifier = RandomForestClassifier(labelCol="is_bot", featuresCol="features",
                                           maxDepth=2, maxBins=4, minInfoGain=0.05)

    pipeline = Pipeline(stages=[indexer_user_type, indexer_platform, feature_assembler, rf_classifier])

    # cv = CrossValidator(estimator=pipeline, evaluator=evaluator, numFolds=5)
    # cv_model = cv.fit(df)

    p_model = pipeline.fit(train)
    prediction = p_model.transform(validation)
    p_accuracy = evaluator.evaluate(prediction)
    print("Pipeline model [Accuracy] = %g" % p_accuracy)

    p_model.write().overwrite().save(model_path)


def main(data_path, model_path):
    spark = _spark_session()
    process(spark, data_path, model_path)


def _spark_session():
    """
    Создание SparkSession.

    :return: SparkSession
    """
    return SparkSession.builder.appName('PySparkMLFitJob').getOrCreate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='session-stat.parquet', help='Please set datasets path.')
    parser.add_argument('--model_path', type=str, default=MODEL_PATH, help='Please set model path.')
    args = parser.parse_args()
    data_path = args.data_path
    model_path = args.model_path
    main(data_path, model_path)
