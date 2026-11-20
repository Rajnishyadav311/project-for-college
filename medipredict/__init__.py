# medipredict/__init__.py
# Install pymysql as MySQLdb if MySQL is configured
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
