from flame_db.matching_helpers import *


#This function is to generate a theoretical dataset
def gen_data_db(n = 250,p = 5, TE = 1):
    """  
    Args:
    n (string, required parameter):
        The name of your table in the database that will contain the data.
    p (string, dataframe,required parameter):
        This is the dataset to be matched. If a string is given, that should be 
        the location of a CSV file to input.
    TE (a connection object,required parameter): 
        A connection oject returned by connector
    treatment_column_name(string, default="treated"): 
        the name of the column with a binary indicator for whether a row is
        a treatment or control unit.
    outcome_column_name (string, default="outcome"): 
        This is the name of the column with the outcome variable of each 
        unit.
        
    Return:
        data: dataset generated
        weights: weights for each covariate in the data
       
    """  
    
    if p <= 2:
        print("p should be larger than 2")
        return None
    
    weights = [0.0]*p
    covs = np.random.binomial(1,0.5,size=(n,p))
    treated = np.random.binomial(1, 0.5, size = n)
    outcome =  TE * treated + np.random.normal(size = n)
    
    for i in range(int(p/2)):
        coeff = TE*(i+1)**1
        outcome  = outcome  +  coeff*covs[:,i]
        
        weights[i] = coeff*1.0

    weights = np.array(weights)
    weights = weights/(sum(weights))


    data = np.append(covs, treated.reshape(-1,1), axis=1)
    data = np.append(data, outcome.reshape(-1,1), axis=1)


    
    col_names =['cov' + str(i+1) for i in range(p)] + ['treated', 'outcome']
    data = pd.DataFrame(data)
    data = data.astype(str)
    data.columns = col_names 
    m,n = data.shape
    for i in range(m):
        for j in range(n-3):
            if data.iloc[i,j] == '1.0':
                data.iloc[i,j] = 'Good'
            else:
                data.iloc[i,j] = 'Bad'
    data = data.astype({"treated": np.float64,"outcome": np.float64})
#     data = data.astype({})


    return data,weights


#This function is to insert the dataset to the database
def insert_data_to_db(table_name,data, conn, treatment_column_name,outcome_column_name,add_missing = False):
    """
    Args:
        table_name (string, required parameter):
            The name of your table in the database that will contain the data.
        data (string, dataframe,required parameter):
            This is the dataset to be matched. If a string is given, that should be 
            the location of a CSV file to input.
        conn (a connection object,required parameter): 
            a connection oject returned by connector
        treatment_column_name(string, default="treated"): 
            the name of the column with a binary indicator for whether a row is
            a treatment or control unit.
        outcome_column_name (string, default="outcome"): 
            This is the name of the column with the outcome variable of each 
            unit.
       
    """    
    
    cur = conn.cursor()
    table = table_name

    colnames = data.columns
    cur.execute('drop table if exists {}'.format(table))

    col_setup =""
    for i in range(len(colnames)):
        v = colnames[i]
        if v == outcome_column_name:
            col_setup += v + ' float(53)'
#             col_setup += v + ' VARCHAR'
        elif v == treatment_column_name:
            col_setup += v +' integer' # ' integer'
        else:
            col_setup += v + ' VARCHAR'
        if i != len(colnames) - 1:
            col_setup += ','
    cur.execute('CREATE TABLE ' + table +  '('+ col_setup+');')
    
 
    
    for i in range(data.shape[0]):
        col = ','.join(['{0}'.format(v) for v in colnames])
        values = ','.join(['\'{0}\''.format(v) for v in data.iloc[i,:-2]])
        values += ','
        values += ','.join(['{0}'.format(v) for v in data.iloc[i,-2:]])
#         print('INSERT INTO '+  table +'('+ col +') VALUES (' + values + ')')
        cur.execute('INSERT INTO '+  table +'('+ col +') VALUES (' + values + ')')
    
    if add_missing:      
        missing = data.iloc[:len(colnames),:].copy()

        for i in range(missing.shape[1]):
            missing.iloc[i,i] = "NULL" 
        missing.loc[:,treatment_column_name] = '0'
        missing = missing.append(missing)
        missing.loc[:,treatment_column_name] = '1'
        missing = missing.append(missing) 

        for i in range(missing.shape[0]):
            col = ','.join(['{0}'.format(v) for v in colnames])
            values = ''

            for k in range(len(missing.iloc[i,:-2])):
                j = missing.iloc[i,k]
                if j != 'NULL':
                    values += '\'' + j + '\''
                if j == 'NULL':
                    values += j
                values += ','

            values += ','.join(['{0}'.format(v) for v in missing.iloc[i,-2:]])
    #         print('INSERT INTO '+  table +'('+ col +') VALUES (' + values + ')')
            cur.execute('INSERT INTO '+  table +'('+ col +') VALUES (' + values + ')')
# 
    conn.commit()
    print('Insert {} rows successfully to Database'.format(data.shape[0]  ))


