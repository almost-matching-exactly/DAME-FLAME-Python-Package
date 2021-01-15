
# This function is to make connections between python and database you are using
def connect_db(database_name,user, password, host, port,  select_db = "postgreSQL" ,driver= None):
    """
    Args:
        database_name (string, required parameter):
            The name of your database.
        user (string, required parameter): 
            user name used to authenticate
        password(string, required parameter): 
            password used to authenticate
        host (string, required parameter): 
            database host address
        port (string, required parameter): 
            connection port number
        select_db ("MySQL", "postgreSQL","Microsoft SQL server", default = "postgreSQL"): 
           Select the type of database you want to use from three options above.  
        driver(string, default=None):
            This parameter will be put into pyodbc if you use Microsoft SQL server.
            
    Returns:
        conn: a connection oject returned by connector   
    """
    conn = None;
    if select_db == "MySQL":
        import mysql.connector
        conn = mysql.connector.connect(host=host,
                                        port=port,
                                        user=user,
                                        password=password,
                                        database=database_name)
    elif select_db == "postgreSQL":
        import psycopg2
        conn = psycopg2.connect(host=host,
                                port=port,
                                user=user,
                                password=password,
                                database=database_name)
        
    elif select_db == "Microsoft SQL server":
        import pyodbc
        conn = pyodbc.connect('DRIVER='+driver+
                              '; SERVER='+host+
                              ';DATABASE='+database_name+
                              ';UID='+user+
                              ';PWD='+ password)
    else:
        raise Exception("please select the database you are using ")

    return conn


#Calculate ATT for the whole dataset
def ATT_db(res):
    """
    Args:
        res (required parameter):
            the output from FLAME_db
            
    Returns:
        ATT: average treatment effect on treated   
    """
    df_matched = res[0]
    weight_sum = 0
    weight_TT_sum = 0
    for i in range(len(df_matched)):
        for j in range(df_matched[i].shape[0]):
            MG = df_matched[i].iloc[j]
            MG_weight = MG['num_control']
            num_MG_treated =  MG['num_treated']
            mean_Y1 = MG['avg_outcome_treated']
            mean_Y0 = MG['avg_outcome_control']
            weight_sum = weight_sum + MG_weight
            weight_TT_sum += MG_weight*(mean_Y1-mean_Y0)
            
    ATT = weight_TT_sum/weight_sum
    return ATT



#Calculate ATE for the whole dataset
def ATE_db(res):
    """
    Args:
        res (required parameter):
            the output from FLAME_db
            
    Returns:
        ATE: average treatment effect  
    """    
    df_matched= res[0]
    weight_sum = 0; 
    weight_CATE_sum = 0
    for i in range(len(df_matched)):
        for j in range(df_matched[i].shape[0]):
            MG = df_matched[i].iloc[j]
            CATE = MG['avg_outcome_treated'] - MG['avg_outcome_control']
            MG_weight = MG['num_control'] + MG['num_treated']


            weight_sum +=  MG_weight
            weight_CATE_sum += MG_weight*CATE
            
    ATE = weight_CATE_sum/weight_sum

    return ATE