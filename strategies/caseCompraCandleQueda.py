import __sub__
from dbOperations import getConnection
from getRatesDatabase import *
from inputSymbols import getSymbols
import csv

client, db = getConnection()
nameFile = f"Extracted Compra_Candle_Queda - {str(datetime.now().timestamp()).replace('.','')}"
symbols = getSymbols()
f_MinVolume = 100000
f_MinOcurrences = 15
f_varReference = -0.002
f_varReference_1 = -0.01
f_date_start = FirstDate(2021,1,1)
f_date_end = LastDate(2022,6,30)

with open(f'extracteds/{nameFile}.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Ativo', 'Qtd Registros', 'Ocorrencias', 'Acertos', 'Erros', '% Acerto', 'G/L Total', "G/L Med.", 'Max. Loss', 'Max. Gain', 'Volume Min', 'Volume Med'])
    
    for i, symbol in enumerate(symbols):
        data_result = getDayRate(symbol, db, f_date_start, f_date_end, f_MinVolume)
        if len(data_result) <= 0: continue
        data_result = data_result[0]
        datas = data_result['ticks']
        qty_datas = len(datas)
        last_object = None
        day_reference = {'close': 200000}
        ocurrences = 0
        total_gain = 0
        avg_gain = 0
        erros = 0
        acertos = 0
        percentual_acertos = 0
        maximum_loss = 0
        maximum_gain = 0
        for data in datas:
            open = data['open']
            close = data['close']
            dayOfWeek = data['date'].isoweekday()
            if (last_object != None):
                ocurrences += 1
                variation = (open / last_object['close'] - 1)
                
                total_gain += variation

                if (variation <= 0):
                    erros += 1
                    maximum_loss = variation if variation < maximum_loss else maximum_loss
                else:
                    acertos += 1
                    maximum_gain = variation if variation > maximum_gain else maximum_gain

                last_object = None

            if (close / open - 1) <= f_varReference and dayOfWeek != 5 and (close <= day_reference['close']) and (open / day_reference['close'] - 1 >= f_varReference_1 ):
                last_object = data

            day_reference = data

        if (ocurrences > 0):
            avg_gain = total_gain / ocurrences
            percentual_acertos = acertos / ocurrences
        
        if (ocurrences >= f_MinOcurrences) and ((percentual_acertos > 0.65 and avg_gain > 0.003) or (percentual_acertos <= 0.25 and avg_gain < -0.003)):
            writer.writerow([symbol, qty_datas, ocurrences, acertos, erros, percentual_acertos, total_gain, avg_gain, maximum_loss, maximum_gain, data_result['min_volume'], data_result['avg_volume']])
        print('Concluído: {:.2f}%'.format((i+1) / len(symbols) * 100))

client.close()
print("Ready!")