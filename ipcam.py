import requests
from flufl.enum import Enum


# this list is meant to be accessed by the status code returned
# so the order matters,
# eg: ddns_status[0] returns 'No action', because status 0 means 'No action'
ddns_status = ['No Action',
               'It’s connecting...',
               'Can’t connect to the Server'
               'Dyndns Succeed',
               'DynDns Failed: Dyndns.org Server Error',
               'DynDns Failed: Incorrect User or Password',
               'DynDns Failed: Need Credited User',
               'DynDns Failed: Illegal Host Format',
               'DynDns Failed: The Host Does not Exist',
               'DynDns Failed: The Host Does not Belong to You',
               'DynDns Failed: Too Many or Too Few Hosts',
               'DynDns Failed: The Host is Blocked for Abusing',
               'DynDns Failed: Bad Reply from Server',
               'DynDns Failed: Bad Reply from Server',
               'Oray Failed: Bad Reply from Server',
               'Oray Failed: Incorrect User or Password',
               'Oray Failed: Incorrect Hostname',
               'Oray Succeed',
               'Reserved',
               'Reserved',
               'Reserved',
               'Reserved']


# this list is meant to be accessed by the status code returned
# so the order matters
upnp_status = ['No Action',
               'Succeed',
               'Device System Error',
               'Errors in Network Communication',
               'Errors in Chat with UPnP Device',
               'Rejected by UPnP Device, Maybe Port Conflict']


# this list is meant to be accessed by the status code returned
# so the order matters
alarm_status = ['No Alarm',
                'Motion Alarm',
                'Input Alarm']


class upnp(Enum):
    """Values to set UPnP settings"""
    disable = 0
    enable = 1


class api(Enum):
    """Device cgi APIs"""
    snapshot = 'snapshot.cgi'
    videostream = 'videostream.cgi'
    videostream = 'videostream.asf'
    get_status = 'get_status.cgi'
    decoder_control = 'decoder_control.cgi'
    camera_control = 'camera_control.cgi'
    reboot = 'reboot.cgi'
    restore_factory = 'restore_factory.cgi'
    get_params = 'get_params.cgi'
    upgrade_firmware = 'upgrade_firmware.cgi'
    upgrade_htmls = 'upgrade_htmls.cgi'
    set_alias = 'set_alias.cgi'
    set_datetime = 'set_datetime.cgi'
    set_users = 'set_users.cgi'
    set_devices = 'set_devices.cgi'
    set_network = 'set_network.cgi'
    set_wifi = 'set_wifi.cgi'
    set_pppoe = 'set_pppoe.cgi'
    set_upnp = 'set_upnp.cgi'
    set_ddns = 'set_ddns.cgi'
    set_ftp = 'set_ftp.cgi'
    set_mail = 'set_mail.cgi'
    set_alarm = 'set_alarm.cgi'
    comm_write = 'comm_write.cgi'
    set_forbidden = 'set_forbidden.cgi'
    set_misc = 'set_misc.cgi'
    get_misc = 'get_misc.cgi'
    set_decoder = 'set_decoder.cgi'


class decoderctl(Enum):
    """
    Decoder control commands.
    Values [8, 24] and [30, 93] are reserved.
    """
    up = 0
    stop_up = 1
    down = 2
    stop_down = 3
    left = 4
    stop_left = 5
    right = 6
    stop_right = 7
    center = 25
    vertical_patrol = 26
    stop_vertical_patrol = 27
    horizon_patrol = 28
    stop_horizon_patrol = 29
    io_output_high = 94
    io_output_low = 95


def _parse_status_response(response):
    """
    Parses the reponse from get_status cgi call.
    :param response: (Required) String response from get_status cgi call.
    """
    return dict(now='', alarm_status=alarm_status[0],
                ddns_status=ddns_status[0], upnp_status=upnp_status[0])


class IPCam(object):
    def __init__(self, ip, port, user='admin', password=''):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password

    def send_command(self, cmd, **request_params):
        """
        Performs the cgi command call.
        :param cmd: (Required) The cgi command to call.
        :param request_params: (Optional) key=value params to send to the cgi command
        """
        url = 'http://' + self.ip + ':' + str(self.port) + '/' + cmd
        request_params['user'] = self.user
        request_params['password'] = self.password
        return requests.get(url, params=request_params).content

    def snapshot(self, name=None):
        """
        Obtains a snapshot from the camera.
        Requires visitor permission.
        :param name: (Optional) Snapshot's name. Defaults to 'device_id(Alias)_Currenttime.jpg'
        """
        # Use “next_url” (for example:next_url=1
        # will name the photo: 1.jpg)
        params = dict(next_url=name)  if name else {}
        self.send_command(api.snapshot, **params)

    def videostream(self, resolution='640*480'):
        """
        Use server push mode to send videostream to Client APP.
        Requires visitor permission.
        :param resolution: (Optional) Output's resolution. Can be either 320*240 or 640*480.
        """
        self.send_command(api.videostream, resolution=resolution)

    def videostream_asf(self, resolution='640*480'):
        """
        Ipcam send videostream of asf format, only support vlc player and mplayer.
        Requires visitor permission.
        :param resolution: (Optional) Output's resolution. Can be either 320*240 or 640*480.
        """
        self.send_command(api.videostream_asf, resolution=resolution)

    def move_a_little(self, direction):
        pass

    def get_status(self):
        """
        Obtains the device status info.
        Requires visitor permission.
        """
        return _parse_status_response(self.send_command(api.get_status))

    def reboot(self):
        """
        Reboots device.
        Requires administrator permission.
        """
        self.send_command(api.reboot)

    def set_alias(self, alias):
        """
        Sets device alias.
        Requires administrator permission.
        :param alias: (Optional) New device alias. Defaults to 'IPCAM'.
        """
        self.send_command(api.set_alias, alias='IPCAM')

    def decoder_control(self, command):
        """
        Sends a control command to operate the device.
        Requires operator permission.
        :param command: (Required) Control command to operate the device.
        """
        self.send_command(api.decoder_control, command=command)

    def restore_factory(self):
        """
        Restores factory settings.
        Requires administrator permission.
        """
        self.send_command(api.restore_factory)

    def set_upnp(self, status):
        """
        Enables/Disables the UPnP settings.
        Requires administrator permission.
        :param status: (Required) upnp.enable or upnp.disable
        """
        self.send_command(api.set_upnp, enable=status)
