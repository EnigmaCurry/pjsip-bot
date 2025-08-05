import time
import os
import pjsua2 as pj


# Load configuration from environment
SIP_ID = os.environ.get("PJSIP_ID_URI", "sip:bot@asterisk.local")
SIP_REG = os.environ.get("PJSIP_REG_URI", "sip:asterisk.local")
SIP_USER = os.environ.get("PJSIP_USERNAME", "bot")
SIP_PASS = os.environ.get("PJSIP_PASSWORD", "supersecret")
SIP_PORT = int(os.environ.get("PJSIP_PORT", "5060"))
WAV_FILE = os.environ.get("PJSIP_WAV_FILE", "hello.wav")


class MyCall(pj.Call):
    def __init__(self, account, call_id):
        super().__init__(account, call_id)

    def onCallMediaState(self, prm):
        ci = self.getInfo()
        for i in range(len(ci.media)):
            if ci.media[i].type == pj.PJMEDIA_TYPE_AUDIO and (
                ci.media[i].status == pj.PJSUA_CALL_MEDIA_ACTIVE
                or ci.media[i].status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD
            ):
                try:
                    aud_med = self.getAudioMedia(i)
                    self.player = pj.AudioMediaPlayer()  # must keep a reference!
                    self.player.createPlayer(WAV_FILE)
                    self.player.startTransmit(aud_med)
                    print(f"✅ Playing {WAV_FILE} to caller")
                except pj.Error as e:
                    print("❌ Audio setup failed:", e)

    def onCallState(self, prm):
        ci = self.getInfo()
        print("📞 Call state:", ci.stateText)
        if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            print("📴 Call ended.")
            del self


class MyAccount(pj.Account):
    def __init__(self, cfg):
        super().__init__()
        self.calls = []
        self.cfg = cfg

    def onIncomingCall(self, iprm):
        print("📥 Incoming call...")
        call = MyCall(self, iprm.callId)
        call_prm = pj.CallOpParam(True)
        call_prm.statusCode = 200
        call.answer(call_prm)
        self.calls.append(call)


def main():
    global ep  # Needed so MyCall can access it

    ep = pj.Endpoint()
    ep.libCreate()
    ep_cfg = pj.EpConfig()
    ep_cfg.uaConfig.stunIgnoreFailure = True
    ep_cfg.medConfig.enableIce = False
    ep.libInit(ep_cfg)

    tc = pj.TransportConfig()
    tc.port = SIP_PORT
    tc.boundAddr = "0.0.0.0"  # allow Asterisk to reach it
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tc)

    ep.libStart()
    print(f"📡 PJSUA2 ready (listening on UDP {SIP_PORT})")

    cfg = pj.AccountConfig()
    cfg.idUri = SIP_ID
    cfg.regConfig.registrarUri = SIP_REG
    cfg.regConfig.timeoutSec = 90
    cfg.regConfig.registerOnAdd = True  # be explicit
    cfg.sipConfig.authCreds.append(
        pj.AuthCredInfo("digest", "*", SIP_USER, 0, SIP_PASS)
    )
    cfg.sipConfig.contactRewriteMethod = 1
    cfg.mediaConfig.enableRtcp = False
    cfg.mediaConfig.enableRtcpMux = True

    ep_cfg.uaConfig.userAgent = "PJSUA2 Python Bot"  # optional but nice

    global acc
    acc = MyAccount(cfg)
    acc.create(cfg)
    time.sleep(2)
    acc.setRegistration(True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("👋 Shutting down")
    finally:
        ep.libDestroy()


if __name__ == "__main__":
    main()
