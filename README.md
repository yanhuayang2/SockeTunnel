# 一个基于socket端口转发的内网穿透

---

## 基本介绍

通过socket将公网访问转发到内网服务

## 用法

server.py运行在具有公网IP的服务器，第一个参数是连接内网的端口，第二个参数是公网访问的参数。

```
python server.py 1234 1111
```

client.py运行在内网中，第一个参数是公网服务器地址，第二个参数是内网服务的地址

```
python client.py 11.11.12.12:1234 127.0.0.1:8081
python client.py myserver.com:1234 127.0.0.1:8081
```

例如在本地python -m http.server 8081开启了访问，访问myserver.com:1111即可访问到内网服务