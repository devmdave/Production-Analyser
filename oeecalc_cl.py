from datetime import datetime, timedelta

def time_input(prompt):
    return datetime.strptime(input(prompt + " (HH:MM): "), "%H:%M")

def calculate_oee():
    print("=== OEE CALCULATION TOOL ===")

    # Shift timings
    shift_start = time_input("Enter shift start time")
    shift_end = time_input("Enter shift end time")
    total_shift_time = (shift_end - shift_start).total_seconds() / 60  # in minutes

    # Breaks
    num_breaks = int(input("Enter number of breaks: "))
    total_break_time = 0

    for i in range(num_breaks):
        print(f"\nBreak {i+1}:")
        b_start = time_input("  Break start time")
        b_end = time_input("  Break end time")
        break_duration = (b_end - b_start).total_seconds() / 60
        total_break_time += break_duration

    planned_production_time = total_shift_time - total_break_time
    print(f"\nTotal planned production time: {planned_production_time:.2f} minutes")

    # Downtime, counts, etc.
    downtime = float(input("Enter total downtime (in minutes): "))
    operating_time = planned_production_time - downtime

    ideal_cycle_time = float(input("Enter ideal cycle time per unit (in minutes): "))
    total_count = int(input("Enter total units produced: "))
    good_count = int(input("Enter good units produced: "))

    # OEE Calculations
    availability = operating_time / planned_production_time
    performance = (ideal_cycle_time * total_count) / operating_time
    quality = good_count / total_count

    oee = availability * performance * quality

    # Results
    print("\n=== OEE RESULTS ===")
    print(f"Availability: {availability*100:.2f}%")
    print(f"Performance:  {performance*100:.2f}%")
    print(f"Quality:      {quality*100:.2f}%")
    print(f"OEE:          {oee*100:.2f}%")

# Run program
if __name__ == "__main__":
    calculate_oee()
