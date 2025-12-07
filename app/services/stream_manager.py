import asyncio
import logging
import reactivex as rx
from reactivex import operators as ops
from reactivex.subject import Subject
from reactivex.scheduler.eventloop import AsyncIOScheduler

from app.services.evaluator import RuleEvaluator
from app.models.sensors import SensorEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JurassicReactor")

class JurassicStreamManager:
    
    def __init__(self, park_context, dinos_context):
        self.park = park_context
        self.dinos_map = {str(d.id): d for d in dinos_context}
        
        self.incoming_stream = Subject()
        self.scheduler = None

    def initialize(self):
        
        loop = asyncio.get_event_loop()
        self.scheduler = AsyncIOScheduler(loop)

        # === THE PIPELINE ===
        self.incoming_stream.pipe(
            
            ops.buffer_with_time_or_count(timespan=2.0, count=10),
            
            ops.filter(lambda batch: len(batch) > 0),
            
            ops.observe_on(self.scheduler)
            
        ).subscribe(
            on_next=lambda batch: self._process_batch(batch),
            on_error=lambda e: logger.error(f"Stream Error: {e}")
        )
        logger.info("Reactive Stream Initialized with Backpressure Strategy.")

    def on_sensor_data(self, data: SensorEvent):
        
        self.incoming_stream.on_next(data)

    def _process_batch(self, batch: list[SensorEvent]):
        
        logger.info(f"--- Processing Batch of {len(batch)} events ---")
        
        for reading in batch:
            self._analyze_reading(reading)

    def _analyze_reading(self, reading: SensorEvent):
        
        alert = None
        
        if reading.sensor_type == "temperature":
            habitat = next((h for h in self.park.habitats if h.id == reading.habitat_id), None)
            if habitat:
                alert = RuleEvaluator.evaluate_temperature(reading, habitat)
        
        elif reading.sensor_type == "motion":
            habitat = next((h for h in self.park.habitats if h.id == reading.habitat_id), None)
            if habitat:
                alert = RuleEvaluator.evaluate_motion(reading, habitat)
                
        elif reading.sensor_type == "heart_rate":
            dino = self.dinos_map.get(reading.dinosaur_id)
            if dino:
                alert = RuleEvaluator.evaluate_heart_rate(reading, dino)

        if alert:
            logger.critical(f"ALERT [{alert.severity}]: {alert.message}")
        else:
            logger.debug(f"OK: {reading.sensor_type}")