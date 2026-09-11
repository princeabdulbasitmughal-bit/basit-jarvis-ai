"""
👑 BASIT JARVIS AI — APACHE SPARK & BIG DATA ACCELERATION ENGINE
Distributed Data Processing, Spark SQL Execution, DataFrame Analytics & Pipeline Generation.
Integrates with Google Gemini for automated data engineering.
"""

import os
import sys
import time
import json
import logging
import sqlite3
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JarvisSpark")
logger.setLevel(logging.INFO)

# PySpark Availability Check
PYSPARK_AVAILABLE = False
try:
    import pyspark
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class BasitSparkEngine:
    BANNER = "SPARK ENGINE | Apache PySpark Distributed Compute + Spark SQL + In-Memory Analytics"

    _spark_session = None

    def __init__(self, app_name: str = "BasitJarvisSpark", master: str = "local[*]"):
        self.app_name = app_name
        self.master = master
        self.init_error = None

    def get_spark_session(self):
        """Lazily initialize and return the PySpark SparkSession."""
        if not PYSPARK_AVAILABLE:
            return None

        if BasitSparkEngine._spark_session is not None:
            return BasitSparkEngine._spark_session

        try:
            # Silence verbose Spark driver logging
            os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
            builder = (
                SparkSession.builder
                .appName(self.app_name)
                .master(self.master)
                .config("spark.driver.memory", "4g")
                .config("spark.sql.shuffle.partitions", "8")
                .config("spark.ui.showConsoleProgress", "false")
                .config("spark.sql.adaptive.enabled", "true")
            )
            BasitSparkEngine._spark_session = builder.getOrCreate()
            BasitSparkEngine._spark_session.sparkContext.setLogLevel("WARN")
            logger.info("PySpark SparkSession initialized successfully.")
            return BasitSparkEngine._spark_session
        except Exception as e:
            self.init_error = str(e)
            logger.warning(f"PySpark initialization failed: {e}. Falling back to Pandas SQL engine.")
            return None

    def execute_sql(self, sql_query: str, sample_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a Spark SQL query.
        Falls back to Pandas + SQLite in-memory engine if PySpark is not ready.
        """
        t0 = time.time()
        spark = self.get_spark_session()

        if spark is not None:
            try:
                # If sample data provided, register temporary view
                if sample_data and isinstance(sample_data, dict):
                    for table_name, records in sample_data.items():
                        if isinstance(records, list) and records:
                            df = spark.createDataFrame(records)
                            df.createOrReplaceTempView(table_name)

                df_result = spark.sql(sql_query)
                rows = [row.asDict() for row in df_result.limit(100).collect()]
                columns = df_result.columns
                count = df_result.count()
                elapsed = round(time.time() - t0, 3)

                return {
                    "engine": "PySpark Distributed SQL",
                    "status": "SUCCESS",
                    "query": sql_query,
                    "columns": columns,
                    "row_count": count,
                    "preview_rows": rows[:20],
                    "latency_sec": elapsed,
                    "summary": f"Spark SQL executed in {elapsed}s | {count} total rows returned."
                }
            except Exception as e:
                logger.error(f"Spark SQL error: {e}")
                # Fall through to SQLite fallback

        # Fallback Engine: SQLite In-Memory
        try:
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()

            # Seed sample tables if provided
            if sample_data and isinstance(sample_data, dict):
                for table_name, records in sample_data.items():
                    if isinstance(records, list) and records and PANDAS_AVAILABLE:
                        pdf = pd.DataFrame(records)
                        pdf.to_sql(table_name, conn, index=False, if_exists="replace")

            cursor.execute(sql_query)
            cols = [desc[0] for desc in cursor.description] if cursor.description else []
            fetched = cursor.fetchall()
            dict_rows = [dict(zip(cols, row)) for row in fetched[:20]]
            elapsed = round(time.time() - t0, 3)

            return {
                "engine": "In-Memory SQL (Spark Fallback)",
                "status": "SUCCESS",
                "query": sql_query,
                "columns": cols,
                "row_count": len(fetched),
                "preview_rows": dict_rows,
                "latency_sec": elapsed,
                "summary": f"SQL query executed in {elapsed}s | {len(fetched)} rows returned."
            }
        except Exception as e:
            elapsed = round(time.time() - t0, 3)
            return {
                "engine": "SQL Engine",
                "status": "ERROR",
                "query": sql_query,
                "error": str(e),
                "latency_sec": elapsed,
                "summary": f"SQL Execution Error: {str(e)}"
            }

    def analyze_dataset(self, file_path: str) -> Dict[str, Any]:
        """
        Inspects and profiles a dataset (CSV, JSON, Parquet) with Spark/Pandas.
        """
        t0 = time.time()
        if not os.path.exists(file_path):
            return {
                "status": "ERROR",
                "error": f"File '{file_path}' not found.",
                "latency_sec": 0
            }

        spark = self.get_spark_session()
        ext = os.path.splitext(file_path)[1].lower().replace(".", "")

        if spark is not None:
            try:
                if ext == "csv":
                    df = spark.read.option("header", "true").option("inferSchema", "true").csv(file_path)
                elif ext == "json":
                    df = spark.read.option("multiline", "true").json(file_path)
                elif ext in ["parquet", "pq"]:
                    df = spark.read.parquet(file_path)
                else:
                    df = spark.read.text(file_path)

                row_count = df.count()
                col_names = df.columns
                schema_fields = [{"name": f.name, "type": str(f.dataType)} for f in df.schema.fields]

                # Sample preview
                sample_rows = [r.asDict() for r in df.limit(5).collect()]
                elapsed = round(time.time() - t0, 3)

                return {
                    "engine": "Apache PySpark",
                    "status": "SUCCESS",
                    "file_path": file_path,
                    "format": ext.upper(),
                    "row_count": row_count,
                    "column_count": len(col_names),
                    "columns": col_names,
                    "schema": schema_fields,
                    "preview": sample_rows,
                    "latency_sec": elapsed,
                    "summary": f"Spark profiled {row_count} rows across {len(col_names)} columns in {elapsed}s."
                }
            except Exception as e:
                logger.warning(f"Spark dataset analysis failed: {e}. Trying Pandas.")

        # Fallback to Pandas
        if PANDAS_AVAILABLE:
            try:
                if ext == "csv":
                    pdf = pd.read_csv(file_path, nrows=50000)
                elif ext == "json":
                    pdf = pd.read_json(file_path)
                elif ext in ["parquet", "pq"]:
                    pdf = pd.read_parquet(file_path)
                else:
                    pdf = pd.read_csv(file_path, sep=None, engine="python", nrows=5000)

                elapsed = round(time.time() - t0, 3)
                return {
                    "engine": "Pandas Data Engine",
                    "status": "SUCCESS",
                    "file_path": file_path,
                    "format": ext.upper(),
                    "row_count": len(pdf),
                    "column_count": len(pdf.columns),
                    "columns": list(pdf.columns),
                    "schema": [{"name": c, "type": str(t)} for c, t in pdf.dtypes.items()],
                    "preview": pdf.head(5).to_dict(orient="records"),
                    "latency_sec": elapsed,
                    "summary": f"Data engine profiled {len(pdf)} rows across {len(pdf.columns)} columns in {elapsed}s."
                }
            except Exception as e:
                return {"status": "ERROR", "error": str(e), "latency_sec": round(time.time() - t0, 3)}

        return {"status": "ERROR", "error": "Neither PySpark nor Pandas available for data analysis."}

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns Spark engine operational health and cluster information."""
        status = {
            "pyspark_installed": PYSPARK_AVAILABLE,
            "pandas_installed": PANDAS_AVAILABLE,
            "session_active": BasitSparkEngine._spark_session is not None,
            "master": self.master,
            "app_name": self.app_name,
            "init_error": self.init_error
        }
        if BasitSparkEngine._spark_session:
            try:
                sc = BasitSparkEngine._spark_session.sparkContext
                status.update({
                    "spark_version": BasitSparkEngine._spark_session.version,
                    "default_parallelism": sc.defaultParallelism,
                    "spark_ui_url": sc.uiWebUrl or "http://localhost:4040",
                    "status": "ONLINE"
                })
            except Exception:
                status["status"] = "INITIALIZED"
        else:
            status["status"] = "STANDBY" if PYSPARK_AVAILABLE else "FALLBACK_PANDAS"
        return status


# Global Singleton Instance
spark_engine = BasitSparkEngine()

if __name__ == "__main__":
    print(json.dumps(spark_engine.get_telemetry(), indent=2))
