import json, falcon, os, magic, multipart
from sqlalchemy import func

from db import session
from model import ModuleType
import model
import util

def _module_to_json(module):
	return { 'id': module.id, 'type': module.type, 'name': module.name, 'description': module.description }


class Module(object):

	def on_get(self, req, resp, id):
		user = req.context['user']

		if not user.is_logged_in():
			resp.status = falcon.HTTP_400
			return

		module = session.query(model.Module).get(id)
		module_json = _module_to_json(module)
		count = session.query(model.Evaluation.points).filter(model.Evaluation.user == user.id, model.Evaluation.module == id).count()

		if count > 0:
			status = session.query(func.max(model.Evaluation.points).label('points')).\
				filter(model.Evaluation.user == user.id, model.Evaluation.module == id).first()
			module_json['state'] = 'correct' if status.points == module.max_points else 'incorrect'
		else:
			module_json['state'] = 'blank'

		if module.type == ModuleType.PROGRAMMING:
			code = util.programming.build(module.id)
			module_json['code'] = code
			module_json['default_code'] = code
		elif module.type == ModuleType.QUIZ:
			module_json['questions'] = util.quiz.build(module.id)
		elif module.type == ModuleType.SORTABLE:
			module_json['sortable_list'] = util.sortable.build(module.id)
		elif module.type == ModuleType.GENERAL:
			module_json['state'] = 'correct' if count > 0 else 'blank'

		req.context['result'] = { 'module': module_json }


class ModuleSubmit(object):

	def _upload_files(self, req, module, user_id, resp):
		report = '=== Uploading files for module id \'%s\' for task id \'%s\' ===\n\n' % (module.id, module.task)

		evaluation = model.Evaluation(user=user_id, module=module.id)
		session.add(evaluation)
		session.commit()

		dir = util.module.submission_dir(module.id, user_id)

		try:
			os.makedirs(dir)
		except OSError:
			pass

		if not os.path.isdir(dir):
			resp.status = falcon.HTTP_400
			req.context['result'] = { 'result': 'incorrect' }
			return

		files = multipart.MultiDict()
		content_type, options = multipart.parse_options_header(req.content_type)
		boundary = options.get('boundary','')

		if not boundary:
			raise multipart.MultipartError("No boundary for multipart/form-data.")

		for part in multipart.MultipartParser(req.stream, boundary, req.content_length):
			path = '%s/%d_%s' % (dir, evaluation.id, part.filename)
			part.save_as(path)
			mime = magic.Magic(mime=True).from_file(path)

			report += '  [y] uploaded file: \'%s\' (mime: %s) to file %s\n' % (part.filename, mime, path)
			submitted_file = model.SubmittedFile(evaluation=evaluation.id, mime=mime, path=path)

			session.add(submitted_file)

		evaluation.full_report = report
		session.add(evaluation)
		session.commit()
		session.close()

		req.context['result'] = { 'result': 'correct' }

	def _evaluate_code(self, req, module, user_id, resp, data):
		evaluation = model.Evaluation(user=user_id, module=module.id)
		session.add(evaluation)
		session.commit()

		code = model.SubmittedCode(evaluation=evaluation.id, code=data)
		session.add(code)

		if not module.autocorrect:
			session.commit()
			session.close()
			req.context['result'] = { 'result': 'correct' }
			return

		result, report = util.programming.evaluate(module.task, module, data)

		points = module.max_points if result else 0
		evaluation = model.Evaluation(user=user_id, module=module.id, points=points, full_report=report)

		session.add(evaluation)
		session.commit()
		session.close()

		req.context['result'] = { 'result': 'correct' if result else 'incorrect', 'score': points }

	def on_post(self, req, resp, id):
		user = req.context['user']

		if not user.is_logged_in():
			resp.status = falcon.HTTP_400
			return

		module = session.query(model.Module).get(id)

		if module.type == ModuleType.GENERAL:
			self._upload_files(req, module, user.id, resp)
			return

		data = json.loads(req.stream.read())['content']

		if module.type == ModuleType.PROGRAMMING:
			self._evaluate_code(req, module, user.id, resp, data)
			return

		if module.type == ModuleType.QUIZ:
			result, report = util.quiz.evaluate(module.task, module.id, data)
		elif module.type == ModuleType.SORTABLE:
			result, report = util.sortable.evaluate(module.task, module.id, data)

		points = module.max_points if result else 0
		evaluation = model.Evaluation(user=user.id, module=module.id, points=points, full_report=report)
		req.context['result'] = { 'result': 'correct' if result else 'incorrect', 'score': points }

		session.add(evaluation)
		session.commit()
		session.close()
