# Rollback — Pre-Phase-0 State

If Phase 0 (bge-m3 + demo_id schema) needs to be undone, the rollback is a **set of four actions**. Doing only the dump restore without the rest gives you a database whose stored vectors (nemotron@1024) and the live query vectors (bge-m3@1024) come from different models — silent retrieval garbage.

## Rollback checklist

1. **Create the `legal` Postgres role (if absent)**
   ```sql
   CREATE ROLE legal WITH LOGIN PASSWORD 'legal';
   ```
   `legalrag.dump` was taken under the `legal` role. `pg_restore` will fail or produce wrong ownership without it.

2. **Restore the dump**
   ```bash
   docker compose up -d db
   # wait for healthy
   pg_restore --clean --if-exists -d postgresql://legal:legal@localhost:5435/legalrag legalrag.dump
   ```

3. **Revert EMBED_MODEL in .env**
   ```
   EMBED_MODEL=nvidia/llama-nemotron-embed-vl-1b-v2:free
   ```

4. **Revert init.sql** to the pre-Phase-0 version (no `demo_id` column, old index names). Use git:
   ```bash
   git checkout f0dbc07 -- apps/api/scripts/init.sql
   ```

5. **Restart the API**
   ```bash
   docker compose restart api
   ```

After step 5 the system is back to the pre-Phase-0 single-demo Law state with nemotron embeddings.
