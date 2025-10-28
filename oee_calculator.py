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
