#!/usr/bin/bash
# Connect to a paired BT device.
MAC=5C_EB_68_1E_E4_ED
if [ -n "$1" ]; then
    MAC="$1"
fi

DEST="org.bluez"
DBUS_PATH="/org/bluez/hci0"
PROPS="org.freedesktop.DBus.Properties"
ADAPTER="org.bluez.Adapter1"
powered=$(dbus-send --system --type=method_call --print-reply=literal --dest="$DEST" "$DBUS_PATH" "${PROPS}.Get" string:org.bluez.Adapter1 string:Powered | grep boolean | awk '{print $3}')

if [ "$powered" == "false" ]; then
    echo "BT powered off, powering on!"
    dbus-send --system --type=method_call --print-reply=literal --dest="$DEST" "$DBUS_PATH" "${PROPS}.Set" string:${ADAPTER} string:Powered variant:boolean:true
fi
if ! dbus-send --system --type=method_call --print-reply=literal --dest="$DEST" "${DBUS_PATH}/dev_$MAC" org.bluez.Device1.Connect; then
    >&2 echo Failed to connect to $MAC
    exit 1
fi
pacmd set-default-sink "bluez_sink.$MAC"
