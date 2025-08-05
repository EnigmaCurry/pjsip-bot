import time
import pjsua as pj

WAV_FILE = "/path/to/file.wav"


class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)


class MyCallCallback(pj.CallCallback):
    def __init__(self, call):
        pj.CallCallback.__init__(self, call)

    def on_state(self):
        print(
            "Call with", self.call.info().remote_uri, "is", self.call.info().state_text
        )

    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            call_slot = self.call.info().conf_slot
            wav_player_id = lib.create_player(WAV_FILE, loop=False)
            wav_slot = lib.player_get_slot(wav_player_id)
            lib.conf_connect(wav_slot, call_slot)
            print("Playing audio...")
            time.sleep(5)  # Wait for audio to finish
            self.call.hangup()


# Init library
lib = pj.Lib()
lib.init(log_cfg=pj.LogConfig(level=3, console_level=4))
lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5060))
lib.start()

acc = lib.create_account(
    pj.AccountConfig(
        domain="asterisk-pbx-ip",
        username="bot",
        password="supersecret",
        registrar="sip:asterisk-pbx-ip",
    )
)

acc.set_callback(MyAccountCallback(acc))
print("SIP Bot is ready to receive calls")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    acc.delete()
    lib.destroy()
