# Phase 1: High-Performance Ingestion Architecture

**Goal:** Establish low-latency ingestion and durable messaging backbone.

## 1. C++ gRPC Ingestion Server (`src/ingestion/olist_ingestion_enterprise.cc`)
- **Role:** High-speed event producer running on EC2 (Ubuntu 24.04).
- **Tech:** gRPC (C++) → Apache Kafka (librdkafka).
- **Performance:** 5ms micro-batching for optimal throughput.
- **Security:**
  - TLS/SSL ready (`grpc::SslServerCredentials` documented).
  - Environment-based broker configuration.
- **Resilience:**
  - Robust `try-catch` blocks around producer initialization.
  - Automatic reconnection logic (`initializeProducer()`) on broker failure.

## 2. Message Broker (Amazon MSK)
- **Config:** `infra/msk/cluster_config.json`.
- **Setup:** Multi-AZ deployment for high availability.
- **Integration:** Acts as the central nervous system, buffering high-velocity write events.

## 3. Streaming Ingestion Producer (`src/streaming/msk_producer.py`)
- **Role:** Python-based alternative producer for rapid development and testing.
- **Tech:** `kafka-python` with JSON serialization.
- **Features:** `acks='all'` durability, automatic retries.

---

**Status:** Code Implemented & Documented ✅
