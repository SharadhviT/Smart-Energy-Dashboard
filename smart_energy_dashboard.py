import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from scipy.optimize import minimize

# Load dataset
data = pd.read_csv('energy_data_100.csv')

# Preprocess data
X = data.drop('energy_consumption', axis=1)
y = data['energy_consumption']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict energy consumption
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f'Mean Squared Error: {mse}')

# Optimization function
def optimize_energy_cost(params):
    # Example parameters: [temperature, humidity, time_of_day]
    temperature, humidity, time_of_day = params
    predicted_consumption = model.predict(np.array([[temperature, humidity, time_of_day]]))
    return predicted_consumption[0]

# Constraints and bounds
constraints = ({'type': 'ineq', 'fun': lambda x: x[0] - 0},  # temperature >= 0
               {'type': 'ineq', 'fun': lambda x: x[1] - 0},  # humidity >= 0
               {'type': 'ineq', 'fun': lambda x: x[2] - 0})  # time_of_day >= 0
bounds = [(0, 100), (0, 100), (0, 24)]  # Example bounds

# Optimize
result = minimize(optimize_energy_cost, [20, 50, 12], bounds=bounds, constraints=constraints)
print(f'Optimized Parameters: {result.x}')
print(f'Optimized Energy Consumption: {result.fun}')

