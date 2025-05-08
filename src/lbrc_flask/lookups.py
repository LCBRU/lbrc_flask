from lbrc_flask.database import db
from lbrc_flask.security import AuditMixin
from lbrc_flask.model import CommonMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select


class Lookup(AuditMixin, CommonMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(500), index=True, unique=True)

    def __str__(self):
        return self.name


class NullObject:
    def __init__(self, object):
        self.object = object
    
    def __getattr__(self, name):
        try:
            return self.object.__getattr__(name)
        except AttributeError:
            pass
        return None


class LookupRepository:
    def __init__(self, cls):
        self.cls = cls

    def get(self, name):
        name = name.strip()

        if not name:
            return None

        q = select(self.cls).where(self.cls.name == name.strip('.,;'))
        result = db.session.execute(q).scalar_one_or_none()

        return result

    def get_or_create(self, name):
        name = name.strip()

        if not name:
            return None

        result = self.get(name)

        if not result:
            result = self.cls(name=name)
        
        return result
    
    def get_or_create_all(self, names):
        return [self.get_or_create(n) for n in names]

    def get_datalist_choices(self):
        lookups = db.session.execute(
            select(self.cls).order_by(self.cls.name)
        ).scalars()
        return [l.name for l in lookups]


    def get_select_choices(self):
        lookups = db.session.execute(
            select(self.cls).order_by(self.cls.name)
        ).scalars()
        return [('0', '')] + [(str(l.id), l.name) for l in lookups]
