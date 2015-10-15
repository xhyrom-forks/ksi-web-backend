from db import session
import model

def to_json(post, user_id, last_visit=None):
	if user_id:
		if not last_visit:
			last_visit = session.query(model.ThreadVisit).\
				filter(model.ThreadVisit.user == user_id, model.ThreadVisit.thread == post.thread, model.ThreadVisit.last_last_visit.isnot(None)).first()
		is_new = True if not last_visit else last_visit.last_last_visit < post.published_at
	else:
		is_new = False

	return {
		'id': post.id,
		'thread': post.thread,
		'author': post.author,
		'body': post.body,
		'published_at': post.published_at.isoformat(),
		'reaction': [ reaction.id for reaction in post.reactions ],
		'is_new': is_new
	}