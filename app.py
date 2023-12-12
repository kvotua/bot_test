import pandas as pd

data_client_input = 'data_read/discount_cards.xlsx'
data_client_output = 'data_read/info_output.xlsx'
cols = ['first', 'second', 'phone']

excel_reader = pd.ExcelFile(data_client_input)
sheets = excel_reader.sheet_names
tableOutput = excel_reader.parse(sheets[0], usecols=cols)
tableOutput.to_excel(data_client_output, sheet_name='Client numbers', index=False, columns=cols)

print('ok')
