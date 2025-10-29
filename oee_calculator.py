import json
import os
from datetime import datetime, timedelta
from pycomm3 import LogixDriver
import threading
import time
import random

class OEECalculator:
    """
    A class to calculate Overall Equipment Effectiveness (OEE).
    OEE = Availability x Performance x Quality.
    Where:
    - Availability measures the percentage of scheduled time that the operation is available to operate.
    - Performance measures the speed at which the operation runs as a percentage of its designed speed.
    - Quality measures the percentage of good units produced out of the total units produced.

    For example, if Availability is 95%, Performance is 85%, and Quality is 70%, then OEE = (95 * 85 * 70) / 10000 = 56.525%
    """

    def __init__(self, config_file="oee_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.latest_oee = {'availability': 0, 'performance': 0, 'quality': 0, 'oee': 0}
        self.current_total_pieces = 0
        self.current_downtime = 0.0

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {}

    def get_breaks(self):
        """Return list of break periods as (start_datetime, end_datetime) tuples for today."""
        breaks = []
        for i in range(1, 4):
            start_key = f"break_{i}_start"
            end_key = f"break_{i}_end"
            if start_key in self.config and end_key in self.config:
                try:
                    start_time = datetime.strptime(self.config[start_key], "%H:%M").time()
                    end_time = datetime.strptime(self.config[end_key], "%H:%M").time()
                    today = datetime.now().date()
                    start_dt = datetime.combine(today, start_time)
                    end_dt = datetime.combine(today, end_time)
                    breaks.append((start_dt, end_dt))
                except ValueError:
                    continue
        return breaks

    def in_break(self, now, breaks):
        """Check if current time is inside a break."""
        for (b_start, b_end) in breaks:
            if b_start <= now <= b_end:
                return True
        return False

    def calculate_elapsed_minutes(self, shift_start, shift_end, current_time, breaks):
        """Calculate elapsed minutes from shift start to current time, excluding breaks."""
        if current_time < shift_start:
            return 0
        if current_time > shift_end:
            current_time = shift_end

        elapsed_minutes = 0
        temp_time = shift_start
        while temp_time < current_time:
            if not self.in_break(temp_time, breaks):
                elapsed_minutes += 1
            temp_time += timedelta(minutes=1)
        return elapsed_minutes

    def Compute_OEE(self, planned_production_time, actual_production_time, ideal_cycle_time, total_pieces, good_pieces):
        """
        Computes the OEE percentage.

        Parameters:
        - planned_production_time (float): Total planned production time in minutes.
        - actual_production_time (float): Actual operating time in minutes (planned time minus downtime).
        - ideal_cycle_time (float): Ideal cycle time per piece in minutes.
        - total_pieces (int): Total number of pieces produced.
        - good_pieces (int): Number of good (quality) pieces produced.

        Returns:
        - float: OEE as a percentage (0-100).
        """
        if planned_production_time <= 0 or actual_production_time <= 0 or ideal_cycle_time <= 0 or total_pieces <= 0 or good_pieces < 0:
            raise ValueError("All parameters must be positive, and good_pieces cannot be negative.")

        if good_pieces > total_pieces:
            raise ValueError("Good pieces cannot exceed total pieces.")

        # Availability (%) = (Actual Production Time / Planned Production Time) * 100
        availability_percent = (actual_production_time / planned_production_time) * 100

        # Performance (%) = (Ideal Cycle Time * Total Pieces / Actual Production Time) * 100
        performance_percent = (ideal_cycle_time * total_pieces / actual_production_time) * 100

        # Quality (%) = (Good Pieces / Total Pieces) * 100
        quality_percent = (good_pieces / total_pieces) * 100

        # OEE (%) = (Availability% * Performance% * Quality%) / 10000
        oee_percent = (availability_percent * performance_percent * quality_percent) / 10000

        return oee_percent

    def compute_realtime_oee(self, shift_start, shift_end, current_time, total_count, good_count, downtime, ideal_cycle_time=None):
        """
        Computes realtime OEE considering breaks and current time.

        Parameters:
        - shift_start (datetime): Shift start time.
        - shift_end (datetime): Shift end time.
        - current_time (datetime): Current time.
        - total_count (int): Total pieces produced.
        - good_count (int): Good pieces produced.
        - downtime (float): Downtime in minutes.
        - ideal_cycle_time (float): Ideal cycle time per piece in minutes (from config if None).

        Returns:
        - dict: {'availability': float, 'performance': float, 'quality': float, 'oee': float}
        """
        if ideal_cycle_time is None:
            ideal_cycle_time = float(self.config.get("ideal_cycle_time", 1.0))

        breaks = self.get_breaks()
        elapsed_minutes = self.calculate_elapsed_minutes(shift_start, shift_end, current_time, breaks)

        if elapsed_minutes <= 0:
            return {'availability': 0, 'performance': 0, 'quality': 0, 'oee': 0}

        operating_time = elapsed_minutes - downtime
        if operating_time < 0:
            operating_time = 0

        availability = operating_time / elapsed_minutes if elapsed_minutes else 0
        performance = (ideal_cycle_time * total_count) / operating_time if operating_time else 0
        quality = good_count / total_count if total_count else 0
        oee = availability * performance * quality

        return {
            'availability': availability * 100,
            'performance': performance * 100,
            'quality': quality * 100,
            'oee': oee * 100
        }

    def get_current_shift(self, now=None):
        """Determine the current shift based on the current time."""
        if now is None:
            now = datetime.now()
        current_time = now.time()

        shifts = [
            ("shift_a_start", "shift_a_end"),
            ("shift_b_start", "shift_b_end"),
            ("shift_c_start", "shift_c_end")
        ]

        for start_key, end_key in shifts:
            start_str = self.config.get(start_key)
            end_str = self.config.get(end_key)
            if start_str and end_str:
                start_time = datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.strptime(end_str, "%H:%M").time()

                if start_time <= end_time:
                    # Same day shift
                    if start_time <= current_time <= end_time:
                        return datetime.combine(now.date(), start_time), datetime.combine(now.date(), end_time)
                else:
                    # Overnight shift
                    if current_time >= start_time or current_time <= end_time:
                        if current_time >= start_time:
                            start_dt = datetime.combine(now.date(), start_time)
                        else:
                            start_dt = datetime.combine(now.date() - timedelta(days=1), start_time)
                        end_dt = datetime.combine(now.date(), end_time)
                        return start_dt, end_dt
        return None, None  # No active shift

    def read_plc_tags(self):
        """Read the production and downtime tags from PLC."""
        plc_ip = self.config.get("plc_ip")
        production_tag = self.config.get("production_tag")
        downtime_tag = self.config.get("fault_delay_tag")

        if not plc_ip or not production_tag or not downtime_tag:
            raise ValueError("PLC IP, production tag, and downtime tag must be configured.")

        # For testing, use random values instead of PLC read
        total_pieces = random.randint(100, 127)
        downtime = random.uniform(0, 60)  # Random downtime in minutes

        # Commented out actual PLC reading
        # try:
        #     with LogixDriver(plc_ip) as plc:
        #         if plc.connected:
        #             total_pieces = plc.read(production_tag).value
        #             downtime = float(plc.read(downtime_tag).value)
        #         else:
        #             raise ConnectionError("Unable to connect to PLC.")
        # except Exception as e:
        #     raise ConnectionError(f"Error reading PLC tags: {e}")

        return total_pieces, downtime

    def start_realtime_calculation(self):
        """Start a thread to calculate realtime OEE every 2 seconds."""
        ideal_cycle_time = float(self.config.get("ideal_cycle_time", 1.0))
        def calculate_loop():
            while True:
                try:
                    total_pieces, downtime = self.read_plc_tags()
                    self.current_total_pieces = total_pieces
                    self.current_downtime = downtime
                    now = datetime.now()
                    shift_start, shift_end = self.get_current_shift(now)
                    if shift_start and shift_end:
                        oee_result = self.compute_realtime_oee(shift_start, shift_end, now, total_pieces, total_pieces, downtime, ideal_cycle_time)
                        self.latest_oee = oee_result
                        print(f"Realtime OEE: {oee_result}")
                    else:
                        print("No active shift.")
                except Exception as e:
                    print(f"Error in realtime calculation: {e}")
                time.sleep(2)

        thread = threading.Thread(target=calculate_loop, daemon=True)
        thread.start()
        return thread

    def get_latest_oee(self):
        """Get the latest calculated OEE data."""
        return self.latest_oee

    def get_current_production_data(self):
        """Get current production data."""
        return self.current_total_pieces, self.current_downtime
