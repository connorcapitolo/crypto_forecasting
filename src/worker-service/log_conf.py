import logging

def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


@singleton
class Logger():
    def __init__(self):
        # reminder that within the container when worker-service is spun up, it's placed within /app
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] :: %(message)s', filename='/app/worker_logging.log')
        self.logr = logging.getLogger('root')
