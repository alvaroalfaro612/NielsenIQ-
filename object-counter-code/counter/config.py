import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo, CountPostgreRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def mongo_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db))

def postgre_count_action() -> CountDetectedObjects: #for using postgresql instead of mongo
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    postgre_host = os.environ.get('POSTGRE_HOST', 'localhost')
    postgre_port = os.environ.get('POSTGRE_PORT', 5432)
    postgre_db = os.environ.get('POSTGRE_DB', 'counter')
    postgre_user = os.environ.get('POSTGRE_USER', 'test')
    postgre_password = os.environ.get('POSTGRE_PASSWORD', 'test')
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                CountPostgreRepo(host=postgre_host, port=postgre_port, database=postgre_db, user=postgre_user, password=postgre_password))


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'postgre')
    count_action_fn = f"{env}_count_action"
    ( f"{env}_count_action")
    return globals()[count_action_fn]()
