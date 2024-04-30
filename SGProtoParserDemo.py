from datetime import datetime
import logging
import sys
import os
import re
from SGProtoParser import ASTDiffResult,  ProtoDiff,  ProtoParser

############################################################################################
class MTLogUtils:
    def InitLoggerAuto(main_file:str, level:int = logging.WARNING, format:str=''):
        print("MainFile:", main_file)
        main_file = main_file.replace("\\", "/")
        R_TempDir = re.compile('/Temp/.*?\.py')
        result = R_TempDir.search(main_file)
        if not result:
            basedir = os.path.dirname(os.path.realpath(main_file))
        else:
            basedir = os.getcwd()
        pass

        print("BaseDir:", basedir)
        appname = os.path.basename(main_file)
        pos = appname.rfind('.')
        if pos > 0: appname = appname[:pos]
        MTLogUtils.InitLogger(basedir, appname, level, format)

    def InitLogger(basedir:str, appname:str, level:int = logging.WARNING, format:str = ''):
        log_format = format
        if log_format == '' or log_format == None:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'    
        pass

        logging.basicConfig(level=level, format=log_format)
        # logger = logging.getLogger('root')
        logger = logging.getLogger()
        logger.setLevel(level=level)

        # 创建一个输出到文件的handler
        curtime = datetime.now()
        timestr = curtime.strftime("%Y-%m-%d_%H-%M-%S")
        
        logdir = basedir + '/log'
        logfile = logdir + "/" + appname  + "_" + timestr + ".log"
        if not os.path.exists(logdir):
            try:
                os.makedirs(logdir)
            except Exception as e:
                logging.error(e)
                return
            pass
        pass

        file_handler = logging.FileHandler(logfile, encoding='utf-8')
        file_handler.setLevel(level=level)

        # 配置日志格式
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        pass

############################################################################################


def Demo_ProtoDiff():

    filepath1 = 'Test/test1.proto'
    filepath2 = 'Test/test2.proto'

    result:ASTDiffResult = ProtoDiff(filepath1, filepath2)
    print('result.additions:')
    print(result.additions)
    print('result.deletions:')
    print(result.deletions)

    return


def Demo_ProtoParser():
    filepath1 = 'Test/test1.proto'
    mod = ProtoParser(filepath1)
    mod.DumpAST()
    mod.DumpAllStatements()
    return

def Run(argv):
    MTLogUtils.InitLoggerAuto(__file__, level=logging.INFO)    

    Demo_ProtoParser()
    Demo_ProtoDiff()

    return

if __name__ == '__main__':
    Run(sys.argv)