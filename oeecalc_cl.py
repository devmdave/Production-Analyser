from datetime import datetime, timedelta
import time
import os

def time_input(prompt):
    return datetime.strptime(input(prompt + " (HH:MM): "), "%H:%M")

def in_break(now, breaks):
    """Check if current time is inside a break."""
    for (b_start, b_end) in breaks:
        if b_start <= now <= b_end:
            return True
    return False

def calculate_realtime_oee():
    print("=== REALTIME OEE MONITOR ===")

    # Shift details
    shift_start = time_input("Enter shift start time")
    shift_end = time_input("Enter shift end time")

    # Break details
    num_breaks = int(input("Enter number of breaks: "))
    breaks = []
    for i in range(num_breaks):
        print(f"\nBreak {i+1}:")
        b_start = time_input("  Break start time")
        b_end = time_input("  Break end time")
        breaks.append((b_start, b_end))

    ideal_cycle_time = float(input("Enter ideal cycle time per unit (in minutes): "))

    print("\n--- Monitoring started ---\n(Press Ctrl+C to stop)\n")

    total_count = 0
    good_count = 0
    downtime = 0.0

    try:
        while True:
            now = datetime.now()

            if now >= shift_end:
                print("Shift ended. Stopping monitoring...")
                break

            # Calculate time so far (excluding breaks)
            elapsed_minutes = 0
            temp_time = shift_start
            while temp_time < now:
                if not in_break(temp_time, breaks):
                    elapsed_minutes += 1
                temp_time += timedelta(minutes=1)

            # Update dynamic data from operator
            print("\nCurrent Time:", now.strftime("%H:%M:%S"))
            print(f"Effective Operating Time: {elapsed_minutes} min")
            print(f"Current Total Count: {total_count}, Good Count: {good_count}, Downtime: {downtime} min")

            # Ask user for updates
            add_prod = int(input("Enter new units produced since last update: "))
            add_good = int(input("Enter good units from those: "))
            add_downtime = float(input("Enter additional downtime (in minutes): "))

            total_count += add_prod
            good_count += add_good
            downtime += add_downtime

            # Calculate OEE components
            if elapsed_minutes > 0:
                operating_time = elapsed_minutes - downtime
                availability = operating_time / elapsed_minutes if elapsed_minutes else 0
                performance = (ideal_cycle_time * total_count) / operating_time if operating_time else 0
                quality = good_count / total_count if total_count else 0
                oee = availability * performance * quality

                os.system('cls' if os.name == 'nt' else 'clear')  # clear console for cleaner UI
                print("=== REALTIME OEE DASHBOARD ===")
                print(f"Time: {now.strftime('%H:%M:%S')}")
                print(f"Operating Time: {operating_time:.1f} min (Excl. downtime/breaks)")
                print(f"Total Count: {total_count}, Good: {good_count}, Downtime: {downtime:.1f} min")
                print(f"Availability: {availability*100:.2f}%")
                print(f"Performance:  {performance*100:.2f}%")
                print(f"Quality:      {quality*100:.2f}%")
                print(f"OEE:          {oee*100:.2f}%")
            else:
                print("Waiting for production time to start...")

            # Sleep or continue
            time.sleep(5)  # refresh every 5 seconds

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
        print("Final OEE Summary:")
        print(f"Total Produced: {total_count}, Good: {good_count}, Downtime: {downtime} min")

if __name__ == "__main__":
    calculate_realtime_oee()
