from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.classification import GBTClassifier


def make_pipeline(train_data, classifier=LogisticRegression):

    # Converting categories into numbers
    sex_index = StringIndexer(inputCol='Sex', outputCol="Sex_index")
    embarked_index = StringIndexer(inputCol='Embarked', outputCol="Embarked_index")

    # Converting features into a vector
    features = ['Pclass', 'Age', 'SibSp', 'SibSp', 'Parch', 'Fare', 'Alone', 'Sex_index', 'Embarked_index']
    features_to_vector = VectorAssembler(inputCols=features, outputCol="features")

    # Making a pipeline
    model = classifier(labelCol="Survived", featuresCol="features")
    pipeline = Pipeline(stages=[sex_index, embarked_index, features_to_vector, model])
    p_model = pipeline.fit(train_data)

    p_model.write().overwrite().save('p_model')

    return p_model


def make_predictions(test_data, model):
    # Establishing an error metric
    evaluator = MulticlassClassificationEvaluator(labelCol="Survived",
                                                  predictionCol="prediction",
                                                  metricName="accuracy")
    predictions = model.transform(test_data)
    accuracy = evaluator.evaluate(predictions)

    return accuracy


def main(spark: SparkSession):
    # Reading the dataset
    titanic_df = spark.read.parquet('train.parquet')

    # Splitting the dataset
    train, test = titanic_df.randomSplit([0.8, 0.2], seed=42)
    algorithms = [LogisticRegression, DecisionTreeClassifier, RandomForestClassifier, GBTClassifier]

    # Comparing algorithms
    for algorithm in algorithms:
        model = make_pipeline(train_data=train, classifier=algorithm)
        accuracy = make_predictions(test, model)
        print(f'{algorithm} accuracy is {accuracy}')

if __name__ == '__main__':
    main(SparkSession
         .builder
         .appName('PySparkTitanikJob')
         .getOrCreate())
