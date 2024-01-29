from llama_index.tools import FunctionTool
import pandas as pd
import matplotlib.pyplot as plt

def plot() -> None:
    '''
    Read apple csv data from local price.csv and plot the price using matplotlib.
    Returns:
        Message - Graph plotted.
    '''
    df = pd.read_csv("price.csv")
    df['date'] = pd.to_datetime(df['date'])
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['price'], linestyle='-')
    # Adding titles and labels
    plt.title('Time Series Plot')
    plt.xlabel('Date')
    plt.ylabel('Price')
    # Show the plot
    plt.grid(True)
    # Save the plot as an image file
    plt.savefig('plot.png')
    # Close the plot to free up resources (optional)
    plt.close()
    return "Graph plotted"

plotting_tool = FunctionTool.from_defaults(
    fn=plot, 
    name='graphplot', 
    description='Plotting function to show time series graph.')