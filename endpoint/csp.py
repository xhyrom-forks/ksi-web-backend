# -*- coding: utf-8 -*-

import falcon, util, json

# Content-security policy reports of frontend
# Every CSP report is forwarded to ksi-admin@fi.muni.cz.
# This is testing solution, if a lot of spam occurs, some intelligence should
# be added to this endpoint.

class CSP(object):

	def on_post(self, req, resp):
		data = json.loads(req.stream.read())
		text = "<p>" + util.config.ksi_web() + \
			"<br><pre>" + json.dumps(data, indent=4) + "</pre></p>" + \
			util.mail.easteregg()
		util.mail.send("ksi-admin@fi.muni.cz", "[KSI-WEB] CSP report", text.decode('utf-8'), )
		req.context['result'] = {}
		resp.status = falcon.HTTP_200
