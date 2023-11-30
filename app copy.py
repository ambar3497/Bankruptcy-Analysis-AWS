from flask import Flask, render_template, request
import pickle
import numpy as np
import mysql.connector

model =pickle.load(open('model-1.pkl','rb'))
app = Flask(__name__)


db_config = {
    "host": "database-bankruptcy-prediction.casrpvd06by3.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "#team83497",
    "database": "bankruptcy_prediction",
}

@app.route('/')
def index():
    return render_template('indexCopy.html')

@app.route('/predict', methods=['POST'])
def predict_placement():
    with mysql.connector.connect(**db_config) as cnx:
        with cnx.cursor() as cursor:
                Net_Income_to_Total_Assets_Ratio = float(request.form.get('Net_Income_to_Total_Assets_Ratio'))
                Income_to_Expense_Ratio = float(request.form.get('Income_to_Expense_Ratio'))
                Borrowing_Dependency_Ratio = float(request.form.get('Borrowing_Dependency_Ratio'))
                Retained_Earnings_to_Assets_Ratio = float(request.form.get('Retained_Earnings_to_Assets_Ratio'))
                Debt_to_Net_Worth_Ratio = float(request.form.get('Debt_to_Net_Worth_Ratio'))
                
                new_data_point = np.array([Net_Income_to_Total_Assets_Ratio, Income_to_Expense_Ratio, Borrowing_Dependency_Ratio, 
                                                Retained_Earnings_to_Assets_Ratio, Debt_to_Net_Worth_Ratio])  
                              
                result = model.predict(new_data_point.reshape(1, 5))
                #resval= int(result[0])
                probabilities = model.predict_proba(new_data_point.reshape(1, 5))
                
                insert_query = f"INSERT INTO bankruptcy_predictions (Net_Income_to_Total_Assets_Ratio, Income_to_Expense_Ratio, Borrowing_Dependency_Ratio, Retained_Earnings_to_Assets_Ratio, Debt_to_Net_Worth_Ratio, Result, Probability)" \
                    f"VALUES ({Net_Income_to_Total_Assets_Ratio}, {Income_to_Expense_Ratio}, {Borrowing_Dependency_Ratio}, {Retained_Earnings_to_Assets_Ratio}, {Debt_to_Net_Worth_Ratio}, {result[0]}, {probabilities[0][1]})"

                # insert_query = ("INSERT INTO bankruptcy_predictions " 
                #                 "(Net_Income_to_Total_Assets_Ratio, Income_to_Expense_Ratio, Borrowing_Dependency_Ratio, "
                #                 "Retained_Earnings_to_Assets_Ratio, Debt_to_Net_Worth_Ratio, Result, Probability) "
                #                 "VALUES (%f, %f, %f, %f, %f, %f, %f)"
                #                 )

                # # Use a tuple to pass the values as parameters to the execute method
                # insert_values = (Net_Income_to_Total_Assets_Ratio, Income_to_Expense_Ratio,
                #                  Borrowing_Dependency_Ratio, Retained_Earnings_to_Assets_Ratio,
                #                  Debt_to_Net_Worth_Ratio, resval, probabilities[0][1]
                #                  )

                cursor.execute(insert_query)
                # cursor.execute(insert_query)
                cnx.commit()
                cursor.close()
                cnx.close()
                
    if result[0] == 1:
        result = f"Based on the input metrics, The model predicts that company is likey to go Bankrupt with a probability of {probabilities[0][1]}"
    else:
        result = f"Based on the input metrics, The model predicts that company is not likey to go Bankrupt with a probability of {probabilities[0][0]}"
                
    return render_template('indexCopy.html', result=result)    
                

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=8080)