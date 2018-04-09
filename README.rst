A Koji build system plugin for helga chat bot
==============================================

About
-----

Helga is a Python chat bot. Full documentation can be found at
http://helga.readthedocs.org.

This Koji plugin allows Helga to respond to koji-related commands in IRC
and print information about builds and tasks.

Estimate when the current (ongoing) build will complete::

  03:14 < ktdreyer> helgabot: current ceph build
  03:14 < helgabot> ktdreyer, ceph-12.2.1-1.el7cp should finish building in
                    3 min 45 sec
                    https://cbs.centos.org/koji/buildinfo?buildID=20348

Find out how long the most recent completed build took to finish::

  03:14 < ktdreyer> helgabot: last ceph build
  03:14 < helgabot> ktdreyer, ceph-12.2.2-0.el7 build duration was 2 hr 49 min
                    https://cbs.centos.org/koji/buildinfo?buildID=21149

Query for packages::

  03:14 < ktdreyer> helgabot: ceph package
  03:14 < helgabot> ktdreyer, ceph is
                    https://cbs.centos.org/koji/packageinfo?packageID=534

Find a user's tasks::

  03:14 < ktdreyer> helgabot: soandso's tasks
  03:14 < helgabot> ktdreyer, soandso's kernel scratch build should be done in
                    1 hr 26 min
                    (https://koji.example.com/koji/taskinfo?taskID=15741633)

Installation
------------
This Koji plugin is `available from PyPI
<https://pypi.python.org/pypi/helga-koji>`_, so you can simply install
it with ``pip``::

  pip install helga-koji

You do not need to configure anything else in Helga's settings for this plugin.

If you want to hack on the helga-koji source code, in your virtualenv
where you are running Helga, clone a copy of this repository from GitHub and
run
``python setup.py develop``.
