from fabric import Connection, Config

config = Config(overrides={'sudo': {'password': 'pydj1234'}})
connect_kwargs = {'password': 'pydj1234'}

c = Connection(host='10.239.1.213', user='hzg', connect_kwargs=connect_kwargs, config=config)
c.run("cd work/nfinccm; git pull", pty=True)
c.sudo("supervisorctl stop gunicorn", pty=True)
c.sudo("supervisorctl start gunicorn", pty=True)