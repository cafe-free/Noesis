import asyncio
import json
import logging
from apps.api.db.redis import get_redis
from apps.api.services.generation import GenerationService

logger = logging.getLogger(__name__)

QUEUE_NAME = "generation_jobs"

async def process_jobs():
    redis = await get_redis()
    service = GenerationService()
    
    logger.info("Worker started, waiting for jobs...")
    
    while True:
        try:
            # Block until a job is available
            result = await redis.blpop(QUEUE_NAME, timeout=0)
            if result:
                _, job_data_str = result
                job_data = json.loads(job_data_str)
                job_id = job_data.get("job_id")
                
                if job_id:
                    logger.info(f"Processing job: {job_id}")
                    await service.run_generation_job(job_id)
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(process_jobs())
