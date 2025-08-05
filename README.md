# pjsip-bot

pjsip-bot is a SIP client that registers itself to a PBX (e.g.,
Asterisk) and awaits for incoming calls. It will eventually become a
chat bot with a stack of piper+whisper+ollama, but for now it just
plays a .wav file.

## Provision SIP account on your PBX.

For example, on Asterisk, define the following config:

```
# pjsip.conf

[internal-endpoint](!)
type=endpoint
transport=transport-udp
context=internal
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
disallow=all
direct_media=no
allow=g722

[internal-aor](!)
type=aor
remove_existing=yes
default_expiration=90
max_contacts=1

; 4xx LLM agent
; ...
[400](internal-endpoint)
auth=400-auth
aors=400
[400](internal-aor)
max_contacts=1
[400-auth]
type=auth
auth_type=userpass
username=400
password=supersecret
```

```
# extensions.conf:
[internal]
exten => 400,1,NoOp(Ringing 400)
 same => n,Dial(PJSIP/400,20)
 same => n,Hangup()
```

## Usage

Run:

```
just config
```

Edit the generated `.env` file to suit your config.

Prepare an audio file in the same directory, and set the `WAV_FILE`
variable in `.env`.

```
just build
```

```
just run
```

The SIP client should automatically register to your PBX and become
reachable.

Test reachability by dialing `400`.
