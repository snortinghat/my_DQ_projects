import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType


@pandas_udf(StringType())
def card_number_mask(s: pd.Series) -> pd.Series:
    return s.str.slice_replace(4, -4, 'XXXXXXXX')


if __name__ == "__main__":
    spark = SparkSession.builder.appName('PySparkUDF').getOrCreate()
    df = spark.createDataFrame([(1, "4042654376478743"),
                                (2, "4042652276478747")], ["id", "card_number"])
    df.show()
    dfr = df.withColumn("hidden", card_number_mask("card_number"))
    dfr.show(truncate=False)
