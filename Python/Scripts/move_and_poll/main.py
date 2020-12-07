import sys
import logging
from move_and_poll import parse_arguments, MoveAndPoll

if __name__ == '__main__':
    LEVEL = logging.DEBUG


    def std_log():
        logging.basicConfig(format='[%(asctime)s.%(msecs)03d] [%(filename)s:%(lineno)s - %(funcName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=LEVEL)
    
    std_log()
    arguments = parse_arguments(sys.argv[1:])
    argdict = {'source_dir': arguments.SourceFolder,
               'destination_dir': arguments.DestinationFolder,
               'poll_folder': arguments.PollFolder,
               'regex': arguments.Regex,
               'timeout': arguments.Timeout,
               'poll_interval': arguments.PollInterval,
               'timeout_code': arguments.TimeoutCode,
               'success_code': arguments.SuccessCode
               }
    sys.exit(MoveAndPoll(**argdict).poll())
