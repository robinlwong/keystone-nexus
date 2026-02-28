# Redis - Not Used in Keystone Nexus

**Date:** 2026-02-27  
**Decision:** Redis excluded from project architecture

---

## Course Module Coverage

**Module 2.2 - Data Architecture** covers Redis as a key-value store technology:
- In-memory caching
- Session management
- Real-time leaderboards
- Pub/Sub messaging

---

## Why Not Redis for Keystone Nexus?

### Project Requirements
- **Analytics-focused:** Historical order analysis, customer segmentation
- **Batch processing:** Daily ELT runs, not real-time streaming
- **Cost optimization:** Serverless Athena vs Redis cluster maintenance

### Technology Decision Matrix

| Requirement | Redis | S3 + Athena | Decision |
|---|---|---|---|
| **Cost** | $50-200/month (EC2 instance) | $5-20/month (storage only) | ✅ S3 + Athena |
| **Query Flexibility** | Limited (key-value) | Full SQL (Athena) | ✅ S3 + Athena |
| **Data Durability** | Requires snapshots | Native durability | ✅ S3 + Athena |
| **Latency** | <1ms | ~2-5 seconds | Redis wins, but not needed |
| **Scalability** | Manual cluster management | Auto-scales | ✅ S3 + Athena |

### Use Cases WHERE Redis WOULD Be Appropriate

**Real-Time Scenarios:**
1. **Session management:** User shopping cart state
2. **Live leaderboards:** Top sellers ranking (refreshed every second)
3. **Rate limiting:** API call throttling
4. **Caching:** Frequently accessed product metadata

**Keystone Nexus Doesn't Need:**
- Sub-second query latency (executives can wait 3 seconds for insights)
- Mutable state (analytics is read-only, append-only)
- Real-time triggers (batch processing is sufficient)

---

## Alternative: When Would We Add Redis?

**Future Enhancement Scenarios:**

1. **Real-Time Dashboard:**
   - If CEO wants "live" GMV counter (updates every 5 seconds)
   - Cache aggregated metrics in Redis
   - Athena → Redis pipeline (every 5 min)

2. **Customer-Facing API:**
   - If building "Track My Order" feature
   - Redis stores order status (fast lookups)
   - Sync from S3 Gold layer hourly

3. **ML Feature Store:**
   - If training recommendation engine
   - Redis caches customer features
   - Low-latency serving for predictions

---

## Documentation for Presentation

**If Executives Ask: "Why not Redis?"**

**Answer:**
> "Redis is excellent for real-time, low-latency use cases like session management. However, Keystone Nexus is an **analytics** platform focused on historical insights, not real-time operations. We prioritized:
> 1. **Cost efficiency:** S3 + Athena costs $20/month vs $200+ for Redis clusters
> 2. **Query flexibility:** Athena supports full SQL, Redis is key-value only
> 3. **Simplicity:** Serverless architecture reduces operational burden
>
> If we expand to real-time dashboards in Phase 2, Redis would be a strong candidate for caching aggregated metrics."

---

**Status:** Redis materials stored in `~/knowledge/` for reference  
**Impact:** Zero impact on project deliverables  
**Future Consideration:** May revisit for real-time enhancements
