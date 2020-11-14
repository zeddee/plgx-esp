from polylogyx.models import DistributedQuery, DistributedQueryTask, db
import datetime as dt

def add_distributed_query(sql, description):
    return DistributedQuery.create(sql=sql,description=description)

def create_distributed_task_obj(node, query):
    return DistributedQueryTask(node=node, distributed_query=query)


def updatedistributedquerytask(guid = None):
    task = DistributedQueryTask.query.filter(DistributedQueryTask.guid == guid).first()
    task.viewed_at = dt.datetime.utcnow()
    db.session.add(task)
    db.session.commit()