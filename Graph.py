
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
    # Example DataFrame


class GraphPlotter:
    def pie_graph(self, df, cycle_time):

        # Convert to dictionary of lists
        df= (df - cycle_time).clip(lower=0)
        data = df.T.to_dict(orient="list")
        # print(data)
    
        # Step 2: Convert to DataFrame and transpose
        df = pd.DataFrame(data).T

        # Step 3: Sum each row to get total per UBG label
        totals = df.sum(axis=1)
        # Find index of largest slice
        max_index = totals.idxmax()
        # Create explode list: 0 for others, 0.1 for largest
        explode = [0.2 if label == max_index else 0 for label in totals.index]

        # Step 4: Plot pie chart
        plt.figure(figsize=(10,7))
        plt.pie(totals, 
            labels=totals.index,
            autopct='%1.1f%%', 
            startangle=90,
            explode=explode,
            shadow=False,
            textprops={'fontsize':12, 'color':'black', 'fontweight':'bold'},
            wedgeprops={'edgecolor':'black','linewidth':1})
        plt.title("Station Delay Distribution", fontsize=16, pad= 30,fontweight='bold', color='purple')
        plt.axis('equal')  # Ensures pie is circular
        plt.show()
        


def main(): 
    # Load Excel file
    file_path = "./CycleTimeBackup/" + '15-08-2025'+ ".xlsx"  # your actual file path
    sheet_name = '15-08-2025'    # your sheet name 

    # Read the Excel file
    df = pd.read_excel(file_path, index_col=0)
    graph = GraphPlotter()
    graph.pie_graph(df, cycle_time=95)


if __name__ == "__main__":
    main()
