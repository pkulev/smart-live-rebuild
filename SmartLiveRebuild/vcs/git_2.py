#	vim:fileencoding=utf-8
# (c) 2010 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 3-clause BSD license or the GPL-2 license.

import subprocess, sys

from SmartLiveRebuild.vcs import VCSSupport, NonLiveEbuild

class GitSupport(VCSSupport):
	reqenv = ['EGIT_BRANCH', 'EGIT_DIR', 'EGIT_UPDATE_CMD']
	optenv = ['EGIT_COMMIT', 'EGIT_HAS_SUBMODULES', 'EGIT_OPTIONS', 'EGIT_REPO_URI', 'EGIT_VERSION']

	def __init__(self, *args):
		VCSSupport.__init__(self, *args)
		if self.env['EGIT_COMMIT'] and self.env['EGIT_COMMIT'] != self.env['EGIT_BRANCH']:
			raise NonLiveEbuild('EGIT_COMMIT set, package is not really a live one')

	def getpath(self):
		return self.env['EGIT_DIR']

	def __str__(self):
		return self.env['EGIT_REPO_URI'] or VCSSupport.__str__(self)

	def getsavedrev(self):
		return self.env['EGIT_VERSION']

	def getrev(self):
		branch = self.env['EGIT_BRANCH']
		if self.env['EGIT_HAS_SUBMODULES']:
			branch = 'origin/%s' % branch
		return self.call(['git', 'rev-parse', branch]).split('\n')[0]

	def getremoterev(self):
		return self.call(['git', 'ls-remote', '--heads', self.env['EGIT_REPO_URI'],
				self.env['EGIT_BRANCH']]).split()[0]

	def getupdatecmd(self):
		if self.env['EGIT_HAS_SUBMODULES']:
			upcmd = ['%s %s' % (self.env['EGIT_UPDATE_CMD'], self.env['EGIT_OPTIONS'])]
			upcmd += ['git submodule %s' % x for x in ('init', 'sync', 'update')]
			return ' && '.join(upcmd)
		else:
			return '%s %s origin %s:%s' % (self.env['EGIT_UPDATE_CMD'], self.env['EGIT_OPTIONS'], self.env['EGIT_BRANCH'], self.env['EGIT_BRANCH'])

	def diffstat(self, oldrev, newrev):
		subprocess.Popen('%s %s..%s' % ('git diff', oldrev, newrev), stdout=sys.stderr, shell=True).wait()