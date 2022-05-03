import __sub__
from dbOperations import getConnection
from getRatesDatabase import *
from inputSymbols import getSymbols
import csv

client, db = getConnection()
nameFile = f"Extracted (Case CYRE3) - {str(datetime.now().timestamp()).replace('.','')}"
symbols = getSymbols()
f_StopGain = 0.016
f_StopLoss = -0.016
f_MinVolume = 100000
f_MinOcurrences = 15
f_varReference = 0.005
f_date_start = FirstDate(2021,4,18)
f_date_end = LastDate(2022,4,20)

with open(f'extracteds/{nameFile}.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Ativo', 'Qtd Registros', 'Ocorrencias', 'Acertos', 'Erros', '% Acerto', 'G/L Total', "G/L Med.", 'Max. Loss', 'Max. Gain', 'Volume Min', 'Volume Med'])
    
    for i, symbol in enumerate(symbols):
        data_result = getDayRate(symbol, db, f_date_start, f_date_end, f_MinVolume)
        if len(data_result) <= 0: continue
        data_result = data_result[0]
        datas = data_result['ticks']
        qty_datas = 0
        last_object = None
        ocurrences = 0
        total_gain = 0
        avg_gain = 0
        erros = 0
        acertos = 0
        percentual_acertos = 0
        maximum_loss = 0
        maximum_gain = 0
        for data in datas:
            qty_datas += 1
            open = data['open']
            close = data['close']
            high = data['high']
            low = data['low']

            if (last_object == None) and ((close / low - 1) <= f_varReference):
                last_object = data
            elif (last_object != None):
                ocurrences += 1
                if ((high / last_object['close'] - 1) >= f_StopGain): # and (low / last_object['close'] - 1) > f_StopLoss)
                    variation = f_StopGain
                else:
                    variation =  close / last_object['close'] - 1 # f_StopLoss
                total_gain += variation

                if (variation <= 0):
                    erros += 1
                    maximum_loss = variation if variation < maximum_loss else maximum_loss
                else:
                    acertos += 1
                    maximum_gain = variation if variation > maximum_gain else maximum_gain

                last_object = None


        if (ocurrences > 0):
            avg_gain = total_gain / ocurrences
            percentual_acertos = acertos / ocurrences
        
        if (ocurrences >= f_MinOcurrences) and ((percentual_acertos > 0.65 and avg_gain > 0.0025) or (percentual_acertos <= 0.25 and avg_gain < -0.0025)):
            writer.writerow([symbol, qty_datas, ocurrences, acertos, erros, percentual_acertos, total_gain, avg_gain, maximum_loss, maximum_gain, data_result['min_volume'], data_result['avg_volume']])
        print('Concluído: {:.2f}%'.format((i+1) / len(symbols) * 100))

client.close()
print("Ready!")