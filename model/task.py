import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from . import Base

class Task(Base):
	__tablename__ = 'tasks'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}

	id = Column(Integer, primary_key=True)
	title = Column(String(255), nullable=False)
	author = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
	category = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
	prerequisite = Column(Integer, ForeignKey('prerequisities.id'), nullable=True)
	intro = Column(String(500), nullable=False)
	body = Column(Text, nullable=False)
	max_score = Column(Integer, nullable=False, default=0, server_default="0")
	position_x = Column(Integer, nullable=False, default=0, server_default="0")
	position_y = Column(Integer, nullable=False, default=0, server_default="0")
	thread = Column(Integer, ForeignKey('threads.id'), nullable=False)
	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_published = Column(DateTime, default=datetime.datetime.utcnow)
	time_deadline = Column(DateTime, default=datetime.datetime.utcnow)

	parents = relationship('TaskParents', primaryjoin='Task.id==TaskParents.task_id')
	prerequisite_obj = relationship('Prerequisite', primaryjoin='Task.prerequisite==Prerequisite.id', uselist=False)

class TaskParents(Base):
	__tablename__ = 'task_parents'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8'
	}

	task_id = Column(Integer, ForeignKey(Task.id), primary_key=True, nullable=False)
	parent_id = Column(Integer, ForeignKey(Task.id), primary_key=True, nullable=False)
