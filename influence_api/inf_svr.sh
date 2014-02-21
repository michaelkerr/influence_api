#!/bin/bash
# /etc/init.d/inf_svr

### BEGIN INIT INFO
# Provides:          inf_svr
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

DIR=/media/sf_projects/influence_api/influence_api/
DAEMON=$DIR/inf_server.py
DAEMON_NAME=inf_svr
DAEMON_USER=root
PIDFILE=/var/run/$DAEMON_NAME.pid

do_start () {
echo "Starting system $DAEMON_NAME daemon"
}

do_stop () {
echo "Stopping system $DAEMON_NAME daemon"
}
 
case "$1" in
 
start|stop)
do_${1}
;;
 
restart|reload|force-reload)
do_stop
do_start
;;
 
status)
status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
;;
*)
echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
exit 1
;;
 
esac
exit 0