from pycomm3 import LogixDriver
import pandas as pd
# Function to read data from PLC
# This function connects to the PLC, reads the specified tags, and returns their values in a dictionary.
# It uses the LogixDriver from the pycomm3 library to establish a connection with the PLC at the specified IP address.
def plc_read():
    # List of tags to read from the PLC
    tags = ['UBG10_cycle_time[0]{499}', 'UBG20_cycle_time[0]{499}','UBG30_cycle_time[0]{499}','UBG40_cycle_time[0]{499}',
        'UBG50_cycle_time[0]{499}','UBG60_cycle_time[0]{499}','UBG70_cycle_time[0]{499}','UBG80_cycle_time[0]{499}',
        'UBG90_cycle_time[0]{499}','UBG100_cycle_time[0]{499}']
    
    # Dictionary to store the PLC data
    tags_data = {}
  
    # Connect to the PLC using LogixDriver
    with LogixDriver('192.168.0.10') as plc:
        if(plc.connected):
            for tag in tags:
                tags_data[tag.replace("_cycle_time[0]{499}","")] = list(plc.read(tag).value)
        else:
            print("Failed to connect to PLC")
    return tags_data

# Function to save PLC data to an Excel file
# This function takes a dictionary of PLC data, converts it to a pandas DataFrame, and saves it to an Excel file named 'data.xlsx'.
def save_to_excel(tags_data):
    # Convert dictionary to DataFrame
    df = pd.DataFrame(tags_data,index=pd.RangeIndex(start=1, stop=499, name='Station No'))
    # Transpose the DataFrame to have tags as rows and their values as columns
    df = df.transpose()
    # Save DataFrame to Excel file
    df.to_excel('data.xlsx',sheet_name="Sheet1", index=True)



if __name__ == "__main__":
    # Print a message indicating the start of the PLC data reading process
    print("----------------------------------------------plc_read------------------------------------")
    print("\n \n")

    # Read data from PLC
    plc_data = plc_read()
    print(plc_data)
    # Save the PLC data to an Excel file
    save_to_excel(plc_data)
    print("PLC data saved to data.xlsx")

