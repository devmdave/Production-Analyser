"""
OEE_calculation.py

This module provides a class to calculate Overall Equipment Effectiveness (OEE) for car company production.
OEE is calculated as: Availability × Performance × Quality
"""

class OEE_Calculator:
    """
    Class for calculating OEE components and overall OEE.
    """

    def calculate_availability(self, total_available_time, downtime):
        """
        Calculate Availability.

        Availability = (Total Available Time - Downtime) / Total Available Time

        Parameters:
        - total_available_time (float): Total time the equipment was available for production (in hours or minutes).
        - downtime (float): Total downtime due to faults, delays, etc. (in same units as total_available_time).

        Returns:
        - float: Availability as a percentage (0-100).
        """
        if total_available_time <= 0:
            return 0.0
        availability = ((total_available_time - downtime) / total_available_time) * 100
        return max(0.0, min(100.0, availability))

    def calculate_performance(self, ideal_cycle_time, actual_cycle_time, total_units_produced):
        """
        Calculate Performance.

        Performance = (Ideal Cycle Time × Total Units Produced) / (Actual Cycle Time × Total Units Produced)
        Simplified: Performance = Ideal Cycle Time / Actual Cycle Time

        Parameters:
        - ideal_cycle_time (float): Ideal time to produce one unit (in minutes or seconds).
        - actual_cycle_time (float): Actual average time to produce one unit (in same units).
        - total_units_produced (int): Total number of units produced.

        Returns:
        - float: Performance as a percentage (0-100).
        """
        if actual_cycle_time <= 0 or total_units_produced <= 0:
            return 0.0
        performance = (ideal_cycle_time / actual_cycle_time) * 100
        return max(0.0, min(100.0, performance))

    def calculate_quality(self, total_units_produced, defective_units):
        """
        Calculate Quality.

        Quality = (Total Units Produced - Defective Units) / Total Units Produced

        Parameters:
        - total_units_produced (int): Total number of units produced.
        - defective_units (int): Number of defective units.

        Returns:
        - float: Quality as a percentage (0-100).
        """
        if total_units_produced <= 0:
            return 0.0
        quality = ((total_units_produced - defective_units) / total_units_produced) * 100
        return max(0.0, min(100.0, quality))

    def calculate_oee(self, availability, performance, quality):
        """
        Calculate Overall Equipment Effectiveness (OEE).

        OEE = Availability × Performance × Quality

        Parameters:
        - availability (float): Availability percentage (0-100).
        - performance (float): Performance percentage (0-100).
        - quality (float): Quality percentage (0-100).

        Returns:
        - float: OEE as a percentage (0-100).
        """
        oee = (availability / 100) * (performance / 100) * (quality / 100) * 100
        return max(0.0, min(100.0, oee))

    def ComputeOEE(self, total_available_time, downtime, ideal_cycle_time, actual_cycle_time, total_units_produced, defective_units):
        """
        Compute Overall Equipment Effectiveness (OEE) using the provided parameters.

        Parameters:
        - total_available_time (float): Total time the equipment was available for production (in hours or minutes).
        - downtime (float): Total downtime due to faults, delays, etc. (in same units as total_available_time).
        - ideal_cycle_time (float): Ideal time to produce one unit (in minutes or seconds).
        - actual_cycle_time (float): Actual average time to produce one unit (in same units).
        - total_units_produced (int): Total number of units produced.
        - defective_units (int): Number of defective units.

        Returns:
        - float: OEE as a percentage (0-100).
        """
        avail = self.calculate_availability(total_available_time, downtime)
        perf = self.calculate_performance(ideal_cycle_time, actual_cycle_time, total_units_produced)
        qual = self.calculate_quality(total_units_produced, defective_units)
        oee = self.calculate_oee(avail, perf, qual)
        return oee

# Example usage (replace with real data)
if __name__ == "__main__":
    # Sample data - replace with actual values from PLC or Excel
    total_available_time = 480  # minutes in a shift
    downtime = 30  # minutes
    ideal_cycle_time = 5  # minutes per unit
    actual_cycle_time = 6  # minutes per unit
    total_units_produced = 80
    defective_units = 5

    calculator = OEE_Calculator()
    oee = calculator.ComputeOEE(total_available_time, downtime, ideal_cycle_time, actual_cycle_time, total_units_produced, defective_units)

    print(f"OEE: {oee:.2f}%")
