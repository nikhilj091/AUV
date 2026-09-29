import os
import pandas as pd
import asyncio
from app.twin.engine import twin_engine

class ReplayEngine:
    def __init__(self):
        self.status = "STOPPED" # STOPPED, RUNNING, PAUSED
        self.engine_id = None
        self.current_index = 0
        self.speed = 1.0 # default speed
        self.data: pd.DataFrame = None
        self.task: asyncio.Task = None
        
    def load_data(self, engine_id: str):
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        data_file = os.path.join(base_dir, 'data', 'test_preprocessed.csv')
        df = pd.read_csv(data_file)
        # Filter for engine
        # unit_number in dataset is integer (1, 2, ...)
        # engine_id in our api is like "ENGINE_001"
        try:
            unit_num = int(engine_id.split("_")[1])
        except:
            unit_num = 1
            
        self.data = df[df['unit_number'] == unit_num].copy()
        self.data.reset_index(drop=True, inplace=True)
        self.engine_id = engine_id
        self.current_index = 0
        
    async def _replay_loop(self):
        try:
            while self.status == "RUNNING" and self.current_index < len(self.data):
                row = self.data.iloc[self.current_index]
                cycle = int(row['time_cycles'])
                
                # Update Twin Engine
                twin_engine.update_state(self.engine_id, cycle, row)
                
                self.current_index += 1
                
                # Sleep based on speed
                await asyncio.sleep(1.0 / self.speed)
                
            if self.current_index >= len(self.data):
                self.status = "STOPPED"
        except asyncio.CancelledError:
            pass

    def start(self, engine_id: str):
        if self.status == "RUNNING" and self.engine_id == engine_id:
            return
            
        if self.engine_id != engine_id:
            self.load_data(engine_id)
            twin_engine.history[engine_id] = [] # Reset history on new start
            
        self.status = "RUNNING"
        if self.task:
            self.task.cancel()
        self.task = asyncio.create_task(self._replay_loop())
        
    def pause(self):
        self.status = "PAUSED"
        if self.task:
            self.task.cancel()
            
    def resume(self):
        if self.status == "PAUSED" and self.data is not None:
            self.status = "RUNNING"
            self.task = asyncio.create_task(self._replay_loop())
            
    def stop(self):
        self.status = "STOPPED"
        self.current_index = 0
        if self.task:
            self.task.cancel()
            
    def reset(self):
        self.stop()
        if self.engine_id:
            twin_engine.history[self.engine_id] = []
        
    def set_speed(self, speed: float):
        self.speed = speed

replay_engine = ReplayEngine()
