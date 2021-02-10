import configparser
from PM import *
from Plotting import *

def cfg():
    config = configparser.ConfigParser()
    config.read("settings.ini", encoding="utf-8")
    mas = dict(config.items('Settings'))
    return mas


def Test(model):
    params = configparser.ConfigParser()
    params.read("settings.ini", encoding="utf-8")
    begin = params.get("Autotest", 'data_begin')
    end = params.get("Autotest", 'data_last')
    ind1 = dates.index(begin)
    ind2 = dates.index(end)
    test_dates = dates[ind1-int(params.get('Settings', 'fh')):ind2+1]
    # test_dates = ['2020-04-07', '2020-04-08', '2020-04-09', '2020-04-10', '2020-04-11', '2020-04-12', '2020-04-13',
    #               '2020-04-14', '2020-04-15', '2020-04-16', '2020-04-17', '2020-04-18']
    indexes = dates[ind1:ind2+1]
    dataframe = obj.df[obj.selected_cols[0]]
    dataframe = dataframe[indexes]
    dataframe = pd.DataFrame(dataframe)
    for i in range(int(obj.params['fh'])):
        dataframe[i + 1] = np.nan
    print(dataframe)
    for i in range(len(test_dates)):
        cfg = configparser.ConfigParser()
        cfg.read('settings.ini')
        cfg.set('Settings', 'end_date', test_dates[i])
        with open('settings.ini', 'w+') as fp:
            cfg.write(fp)
        tensor = Data('Urovni2_1_1_new.xlsx')
        settings = cfg()
        ind = index_search(tensor.x_data, settings['end_date'])
        predict_result = model.predict(np.array(tensor.x[ind]).reshape(1, int(settings['fh']), len(x[0][0])))
        result = [k*(tensor.a_max[0] - tensor.a_min[0]) + tensor.a_min[0] for k in predict_result[0]]
        predict_dates = [j[0] for j in tensor.y_data[ind]]
        predicted_true = [j[-1] for j in tensor.y_data[ind]]
        for j in range(i, i+int(obj.params['fh'])+1):
            if j > len(test_dates) - 1:
                break
            if test_dates[j] in predict_dates and test_dates[j] in indexes:
                ind = predict_dates.index(test_dates[j])
                dataframe.loc[predict_dates[ind], ind+1] = abs(predicted_true[ind]-result[ind])
    dataframe.loc['mean_value'] = dataframe.mean()
    print(dataframe)
    file_format = '.xlsx'
    name = "Test " + datetime.datetime.strftime(datetime.datetime.now(),
            f"%d-%m-%Y %H-%M-%S {obj.params['restore_data']}") + file_format
    dataframe.to_excel(name)