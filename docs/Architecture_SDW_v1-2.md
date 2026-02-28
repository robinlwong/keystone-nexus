# Keystone Nexus - Software Design Work (SDW) v1.0-2.0

**Source:** Google Docs Architecture Document  
**Date:** 2026-02-27

---

## Document 1: High-Performance Architecture Design

[Content from first Google Doc - phases, C++ gRPC implementation, Python Lakehouse layer, strategic recommendations]

## Document 2: Phase-Based Implementation

### Phase 1: Scalable Lakehouse Architecture - Enterprise Edition

**Environment:** AWS EC2 Ubuntu 24.04

**Architecture Components:**
1. **Ingestion Layer:** C++ gRPC Server → Apache Kafka
2. **Message Broker:** Amazon MSK or EC2-based Kafka
3. **Processing Layer:** Python workers with Apache Arrow
4. **Orchestration:** Apache Airflow (Amazon MWAA)
5. **Query Layer:** AWS Athena (serverless SQL)
6. **Transactional State:** AWS RDS PostgreSQL
7. **Frontend:** Node.js/TypeScript dashboards (pnpm)

**Key Technical Decisions:**
- C++ for low-latency (microsecond) ingestion
- Apache Arrow for columnar in-memory processing
- Partitioned Parquet files (year/month/day) for cost optimization
- S3 Bronze → Silver → Gold data layers

### Phase 2: Data Quality & Orchestration

**Tools:**
- Apache Airflow (Amazon MWAA)
- Great Expectations for validation
- AWS Athena for serverless aggregation

**Pipeline Flow:**
1. S3 Sensor (wait for new Parquet partitions)
2. Great Expectations validation checkpoint
3. AWS Athena aggregation (Silver → Gold)
4. SNS/Slack alerts on failure

**Data Quality Rules:**
- Logical timestamp validation (delivery > purchase)
- Revenue integrity (price > 0)
- Foreign key completeness (no null customer_id)

### Phase 3: Compute Optimization & Quarantine Routing

**Enhancements:**
1. **Athena Execution Engine for GX:**
   - Pushes validation compute to AWS Athena
   - Prevents MWAA worker OOM crashes

2. **Dead Letter Quarantine:**
   - BranchPythonOperator routes based on validation results
   - Corrupted data → `s3://olist-data-lake-quarantine/`
   - Successful data → Gold layer aggregation

**Strategic Mitigations:**
- AWS Glue Schema Registry for schema drift detection
- Amazon RDS Proxy for connection pooling
- AWS Auto Scaling Groups for elastic compute
- CloudWatch alarms for Kafka consumer lag

---

## Code Artifacts

### C++ gRPC Ingestion Server

```cpp
// olist_ingestion_enterprise.cc
// High-speed ingestion via gRPC → Kafka
// Compile: g++ -std=c++17 -lgrpc++ -lprotobuf -lrdkafka++

#include <grpcpp/grpcpp.h>
#include <librdkafka/rdkafkacpp.h>

class EnterpriseIngestionServiceImpl : public IngestionService::Service {
private:
    std::unique_ptr<RdKafka::Producer> producer_;
    std::unique_ptr<RdKafka::Topic> topic_;

public:
    EnterpriseIngestionServiceImpl(const std::string& brokers, const std::string& topic_name) {
        // Kafka producer with 5ms micro-batching
        std::string errstr;
        std::unique_ptr<RdKafka::Conf> conf(RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL));
        conf->set("bootstrap.servers", brokers, errstr);
        conf->set("queue.buffering.max.ms", "5", errstr);
        
        producer_.reset(RdKafka::Producer::create(conf.get(), errstr));
        std::unique_ptr<RdKafka::Conf> tconf(RdKafka::Conf::create(RdKafka::Conf::CONF_TOPIC));
        topic_.reset(RdKafka::Topic::create(producer_.get(), topic_name, tconf.get(), errstr));
    }

    Status SendEvent(ServerContext* context, const EventRequest* request, EventResponse* reply) override {
        std::string payload = request->payload_json();
        
        RdKafka::ErrorCode resp = producer_->produce(
            topic_.get(), 
            RdKafka::Topic::PARTITION_UA, 
            RdKafka::Producer::RK_MSG_COPY,
            const_cast<char *>(payload.c_str()), payload.size(),
            NULL, NULL);
            
        if (resp != RdKafka::ERR_NO_ERROR) {
            reply->set_success(false);
            return Status::CANCELLED;
        }

        producer_->poll(0);
        reply->set_success(true);
        return Status::OK;
    }
};

void RunServer() {
    std::string server_address("0.0.0.0:50051");
    EnterpriseIngestionServiceImpl service("10.0.1.50:9092", "olist-enterprise-events");

    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "🚀 Enterprise C++ gRPC Server listening on " << server_address << std::endl;
    server->Wait();
}
```

### Python Lakehouse Consumer

```python
# olist_lakehouse_enterprise.py
# Kafka → S3 Parquet with Apache Arrow
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
from confluent_kafka import Consumer

KAFKA_BROKERS = '10.0.1.50:9092'
S3_BUCKET = 'olist-data-lake-silver'

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'lakehouse-enterprise-writers',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})

def process_batch(messages):
    valid_data = [json.loads(msg.value().decode('utf-8')) for msg in messages]
    arrow_table = pa.Table.from_pylist(valid_data)
    
    # Extract partition columns
    timestamps = pc.strptime(arrow_table.column('order_purchase_timestamp'), format='%Y-%m-%d %H:%M:%S', unit='s')
    arrow_table = arrow_table.append_column('year', pc.year(timestamps))
    arrow_table = arrow_table.append_column('month', pc.month(timestamps))
    arrow_table = arrow_table.append_column('day', pc.day(timestamps))

    # Write partitioned Parquet to S3
    pq.write_to_dataset(
        arrow_table,
        root_path=f"s3://{S3_BUCKET}/orders/",
        partition_cols=['year', 'month', 'day'],
        compression='snappy'
    )
    consumer.commit()
```

### Airflow DAG with Quarantine Routing

```python
# dags/olist_resilient_pipeline.py
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator

def route_based_on_validation(**kwargs):
    ti = kwargs['ti']
    validation_result = ti.xcom_pull(task_ids='run_gx_athena_checks')
    
    if validation_result and validation_result['success']:
        return 'calculate_daily_regional_sales_gold'
    else:
        return 'quarantine_corrupted_data'

with DAG('olist_resilient_silver_to_gold', schedule_interval='@daily') as dag:
    validate_silver_data = GreatExpectationsOperator(
        task_id='run_gx_athena_checks',
        checkpoint_name='olist_athena_checkpoint',
        fail_task_on_validation_failure=False,
        do_xcom_push=True
    )
    
    branch_routing = BranchPythonOperator(
        task_id='validation_routing',
        python_callable=route_based_on_validation
    )
    
    aggregate_gold = AthenaOperator(task_id='calculate_daily_regional_sales_gold')
    quarantine_data = PythonOperator(task_id='quarantine_corrupted_data')
    
    validate_silver_data >> branch_routing
    branch_routing >> [aggregate_gold, quarantine_data]
```

---

## Strategic Recommendations Summary

1. **Schema Evolution:** AWS Glue Schema Registry integration
2. **Cost Optimization:** Athena partitioning (year/month/day)
3. **Connection Pooling:** Amazon RDS Proxy
4. **Elastic Compute:** AWS Auto Scaling Groups + CloudWatch alarms
5. **Data Quality:** Great Expectations with Athena execution engine
6. **Resilience:** Dead Letter quarantine routing

---

**Status:** Architecture documented, ready for implementation  
**Next Steps:** Code implementation, AWS deployment, testing
