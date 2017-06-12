#!/bin/bash

### BEGIN INIT INFO
# Provides:                 NLP_Python
# Required-Start:           $remote_fs $syslog
# Required-Stop:            $remote_fs $syslog
# Default-Start:            2 3 4 5
# Default-Stop:             0 1 6
# Short-Description:        Using google speech API and Gmail API.
# Description:              Analyzing record audio and response automatically
### END INIT INFO

DIR=/home/pi/tenenceraspberry
DAEMON=$DIR/speech_rec.py
DAEMON_NAME=tenence

DAEMON_OPTS=""
DAEMON_USER=root

PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

do_start () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
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