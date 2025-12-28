# gennet
A Docker based network components builder from config.toml

## Getting started.
* prepare docker. and run docker/gennet/run.sh
* generate and start by generated/start.sh
* change config.toml that you want to use.

```
$ sh docker/gennet/run.sh
created docker/gennet/generated
$ tree docker/gennet/generated/
docker/gennet/generated/
├── dhcpd_v0202
│   ├── Dockerfile
│   ├── build.sh
│   ├── conf
│   │   ├── dhcpd.conf
│   │   └── dhcpd.leases
│   ├── start.sh
│   └── stop.sh
├── dnsmasq_v0202
│   ├── Dockerfile
│   ├── build.sh
│   ├── conf
│   │   ├── dnsmasq.conf
│   │   ├── hosts
│   │   └── resolv.conf
│   ├── start.sh
│   └── stop.sh
├── gw_v3000
│   ├── conf
│   ├── rules.sh
│   ├── start.sh
│   └── stop.sh
├── mailcatcher_v0202
│   ├── start.sh
│   └── stop.sh
├── ntpd_v0202
│   ├── Dockerfile
│   ├── build.sh
│   ├── check.sh
│   ├── conf
│   │   ├── ntpd.conf
│   │   └── resolv.conf
│   ├── start.sh
│   └── stop.sh
├── radiusd_v0202
│   ├── Dockerfile
│   ├── build.sh
│   ├── conf
│   │   ├── clients.conf
│   │   ├── proxy.conf
│   │   └── users
│   ├── start.sh
│   └── stop.sh
├── rsyslogd_v0202
│   ├── Dockerfile
│   ├── build.sh
│   ├── conf
│   │   └── rsyslog.conf
│   ├── start.sh
│   └── stop.sh
├── start.sh
├── stop.sh
└── tftpd_v0202
    ├── Dockerfile
    ├── build.sh
    ├── start.sh
    └── stop.sh

14 directories, 43 files
```
