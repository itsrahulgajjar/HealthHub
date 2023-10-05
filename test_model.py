import pickle

# Load the pickle model
model = pickle.load(open('model.pkl', 'rb'))

# Sample test data
test_data = [30, 120, 80, 100, 98.6, 70]

try:
    # Make a prediction
    result = model.predict([test_data])

    # Print the result
    print("Prediction Result:", result)
except Exception as e:
    print("Error:", str(e))