import asyncio
import logging
from datetime import datetime
import reactivex as rx
from reactivex import operators as ops
from reactivex.subject import Subject
from reactivex.scheduler.eventloop import AsyncIOScheduler

from app.services.evaluator import RuleEvaluator
from app.models.sensors import SensorEvent

logger = logging.getLogger("JurassicReactor")

class JurassicStreamManager:
    def __init__(self, park_context, dinos_context):
        self.park = park_context
        self.dinos_map = {str(d.id): d for d in dinos_context}
        
        self.incoming_stream = Subject()
        self.scheduler = None

        self.stats = {
            "total_events_processed": 0,
            "total_alerts_triggered": 0,
            "start_time": datetime.now(),
            "last_batch_size": 0,
            "current_avg_bpm": 0
        }

    def initialize(self):
        loop = asyncio.get_event_loop()
        self.scheduler = AsyncIOScheduler(loop)

        self.incoming_stream.pipe(
            ops.buffer_with_time_or_count(timespan=2.0, count=10),
            ops.filter(lambda batch: len(batch) > 0),
            ops.observe_on(self.scheduler)
        ).subscribe(
            on_next=lambda batch: self._process_batch(batch),
            on_error=lambda e: logger.error(f"Stream Error: {e}")
        )
        logger.info("Reactive Stream Initialized.")

    def on_sensor_data(self, data: SensorEvent):
        self.incoming_stream.on_next(data)
        
    def register_dinosaur(self, dino):
        self.dinos_map[str(dino.id)] = dino

    def unregister_dinosaur(self, dino_id):
        if str(dino_id) in self.dinos_map:
            del self.dinos_map[str(dino_id)]

    def _process_batch(self, batch: list[SensorEvent]):
        count = len(batch)
        self.stats["total_events_processed"] += count
        self.stats["last_batch_size"] = count
        
        bpm_readings = [r.bpm for r in batch if r.sensor_type == "heart_rate"]
        
        if bpm_readings:
            avg_bpm = sum(bpm_readings) / len(bpm_readings)
            self.stats["current_avg_bpm"] = round(avg_bpm, 1)
        
        logger.info(f"Processing Batch of {count} events...")
        
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
            self.stats["total_alerts_triggered"] += 1
            logger.critical(f"==> ALERT! [{alert.severity}]: {alert.message}")
        else:
            logger.debug(f"OK: {reading.sensor_type}")

    def get_system_metrics(self):
        now = datetime.now()
        uptime = (now - self.stats["start_time"]).total_seconds()
        
        tps = 0
        if uptime > 0:
            tps = self.stats["total_events_processed"] / uptime

        return {
            "uptime_seconds": round(uptime, 2),
            "total_processed": self.stats["total_events_processed"],
            "total_alerts": self.stats["total_alerts_triggered"],
            "current_throughput_tps": round(tps, 2),
            "last_batch_size": self.stats["last_batch_size"],
            "avg_bpm": self.stats["current_avg_bpm"]
        }