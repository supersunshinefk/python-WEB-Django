# indass_boss说明

## 环境要求
```
Python 3.6.5

Django==2.0.4
mysqlclient=1.3.12
```

## 完成功能
* Django admin
* Django mysql
* Django models+admin+url
* Django i18n
* Django locale
* Django Signals
  * pre_save,post_save
  * pre_delete,post_delete
  * request_finished
  * enable, disable
* boss与manager交互脚本service.py
  * mysql操作类mixmysql.py
  * redis连接类mixredis.py