# 导入db，用于操作数据库
from .. import db
from . import celer


@celer.task
def async_order(o):
	if o.status == "daifukuan":
		o.status = "close"
		db.session.add(o)
	elif o.status == "daifahuo":
		o.status = "finish"
		db.session.add(o)
