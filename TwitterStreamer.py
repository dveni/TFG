#Importamos 
#Stream listener
from tweepy.streaming import StreamListener
#Autenticación de desarrollador de twitter
from tweepy import OAuthHandler
#Funciones de tratado de streams
from tweepy import Stream
#Api de twitter
from tweepy import API
#Funciones de tratado de tiempos
from time import gmtime, strftime, localtime
import logging, datetime
import time
#Funciones del sistema operativo
import os

#Clase FileListener, control
class FileListener(StreamListener):
    # Constructor
    def __init__(self, path, restart_time):
        self.path = path
        self.current_file = None
        self.restart_time = restart_time
        self.file_start_time = time.time()
        self.file_start_date = datetime.datetime.now()
        self.firstTweet = False

    # Me llegan los datos de un tweet
    def on_data(self, data):
        # Guardo la fecha
        current_time = datetime.datetime.now()
        # Creo un fichero nuevo si:
        # - No existe fichero anterior( inicializar)
        # - Si se ha superado el tiempo para restart
        # - Si se ha cambiado de dia
        if self.current_file == None or time.time() - self.restart_time > self.file_start_time \
                or self.file_start_date.day != current_time.day:
            self.startFile()
            self.file_start_date = datetime.datetime.now()
        # Escribo los datos en el fichero
        if self.firstTweet:
            self.current_file.write('[')
        if data.startswith('{'):
            if not self.firstTweet:
                self.current_file.write(',')
            self.current_file.write(data)
            self.firstTweet=False
            if not data.endswith('\n'):
                self.current_file.write('\n')

    def on_error(self, status_code):
        # Error 420: Rate Limited -> We want disconnect
        logger.error(status_code)
        if status_code == 420:
            exit()
            return False

    #Función que crea un nuevo archivo
    def startFile(self):
        #Si hay un archivo en marcha lo cerramos
        if self.current_file:
            self.current_file.write("]")
            self.current_file.close()
        #Cogemos la fecha actual y le damos formato
        local_time_obj = localtime()
        datetime = strftime("%Y_%m_%d_%H_%M_%S", local_time_obj)
        year = strftime("%Y", local_time_obj)
        month = strftime("%m", local_time_obj)
        day = strftime("%d", local_time_obj)
        #Creamos el sistema de directorios
        full_path = os.path.join(self.path, year)
        full_path = os.path.join(full_path, month)
        full_path = os.path.join(full_path, day)
        try:
            # Creo un directorio con la fecha de hoy
            os.makedirs(full_path)
            logger.info('Created %s' % full_path)
        except:
            pass
        # Creo el fichero de nombre: fecha y hora
        filename = os.path.join(full_path, '%s.json' % datetime)
        #self.current_file = gzip.open(filename, 'w')
        self.current_file = open(filename,'w')
        self.file_start_time = time.time()
        self.firstTweet=True
        logger.info('Starting new file: %s' % filename)



# Al lanzarlo como script
if __name__ == '__main__':
 
    consumer_key = ''
    consumer_secret = ''
    access_token = '-'
    access_token_secret = ''
    output_directory = './data/JSONFiles/GenericTweets'
    if not os.path.isdir('log'):
        os.makedirs('log')
    log_filename = 'log/logEsGeneric'

    logger = logging.getLogger('tweepy_streaming')
    handler = logging.FileHandler(log_filename, mode='a')
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    #Boundary boxes got from http://bboxfinder.com/
    # Hay algunas regiones españolas que no entran en estas cajas, pero las grandes ciudades están incluidas en cualquier caso
    norte = [-9.832764,42.147114,-1.812744,43.937462]
    centroeste = [-6.130371,37.037640,4.570313,42.358544]
    oestesur = [-6.690674,35.995785,-1.538086,41.253032]
    huelva = [-7.300415,37.033255,-6.652222,37.848833]
    badajoz = [-7.020264,38.233865,-6.009521,38.959409]
    canarias = [-19.467773,27.513143,-13.304443,29.869229]
    
    
    spain = norte + centroeste + oestesur + huelva + badajoz + canarias
    
    marcas =['Cocacola', 'Coca cola', 'Pepsi', '100 montaditos', 'McDonalds', 'Burguer King', 'TacoBell', 'Telepizza',
                'Dominos', 'Dominos Pizza', 'Starbucks', '#Rodilla', 'Pans & company', 'KFC',
                 'Fanta', 'Estrella Galicia', 'Cruzcampo', 'Mahou', 'Estrella Damn', 'Amstel', '-filter:retweets']
    food_keywords = ['bacon', 'pastel', 'tarta', 'galletas', 'bebida energética', 'perrito caliente', 'helado', 
                     'pizza', 'frito', 'cerveza', 'hamburguesa', 'kebab', 'refresco', 'fastfood', 'vodka', 'whiskey',
                    'ron', 'tequila', 'sandwich', 'ginebra', 'anís', 'brandy','nuggets']
    stream_args = marcas + food_keywords
    
    
    if not os.path.isdir('pid'):
        os.makedirs('pid')
    pid_file = 'pid/pidSpanishGenericTweets'
    file = open(pid_file, 'w')
    file.write(str(os.getpid()))
    file.close()

    #Creo el Listener:
    # - Con el directorio donde colocar los tweets
    # - Y con el tiempo de crear un fichero nuevo
    listener = FileListener(output_directory, 3600)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    logger.warning("Connecting Process Spanish")
    api = API(auth)
    logger.warning(api.me().name)

    stream = Stream(auth=auth, listener=listener)
    try:
        stream.filter(locations=spain)#, track=stream_args)
    except Exception as e:
        #SEND A EMAIL
        logger.error('Failed to upload to ftp: '+ str(e))