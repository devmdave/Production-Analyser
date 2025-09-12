import pandas as pd
import matplotlib.pyplot as plt
# Example DataFrame
data = {
    'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
    'Sales': [250, 300, 400, 350]
}
df = pd.DataFrame(data)


plt.plot(df['Month'], df['Sales'], marker='o')
plt.title('Monthly Sales')
plt.xlabel('Month')
plt.ylabel('Sales')
plt.grid(True)
plt.show()
