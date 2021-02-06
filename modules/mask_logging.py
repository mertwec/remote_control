import logging

logging.basicConfig(filename="/home/pi/spreli/remote_control/spreli_logfile.log",
                    format='%(asctime)s\\%(levelname)s: %(message)s',
                    datefmt='%Y\%m\%d %H:%M:%S',
                    level=logging.INFO,
                    filemode="w")

main_log = logging.getLogger("main_log")
module_log = logging.getLogger('module_log')


def info_log(message):
     return main_log.info(f'{message}')

def debug_log(message):
     return main_log.debug(f'{message}')
     
def warning_log(message):
     return main_log.warning(f'{message}')
     
def error_log(message):
     return main_log.error(f'{message}')


