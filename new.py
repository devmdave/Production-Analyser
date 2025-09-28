import argparse

def one():
    print("Function one() called — no PLC mode")

def two():
    print("Function two() called — PLC mode")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run test.py with plc or no-plc mode")
    parser.add_argument("mode", choices=["plc", "no-plc"], help="Choose 'plc' or 'no-plc' mode")
    args = parser.parse_args()

    if args.mode == "plc":
        two()
    elif args.mode == "no-plc":
        one()
