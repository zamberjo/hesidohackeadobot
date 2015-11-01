# hesidohackeadobot

## Synopsis

Bot telegram para uso de la API de www.hesidohackeado.com. Posibilidad de configurar la comprobación de nuevas entradas, mediante cron configurable desde el bot para horas/minutos.

## Installation

```
python setup.py install
chmod +x debian/postinst && ./debian/postinst
```

## Configuration

```
[options]
# Telegram user ID to indicate who is the administrator. Admin has commands just for him.
admin_id = 
# Cron configuration
cron_hour_every = 
cron_hour_on =
cron_minute_every =
cron_minute_on =
# Token Telegram BOT 
api_token =
```

## Telegram BOT Commands

Follow -> https://core.telegram.org/bots#3-how-do-i-create-a-bot

```
There's a… bot for that. Just talk to BotFather (described below) and follow a few simple steps. Once you've created a bot and received your authorization token...
```

```
newemail - Record new email
delemail - Unlink an email record
delemails - Unlink all emails records
emails - Show emails.
checkunread - Execute the verification on hesidohackeado.conm, only shows the results unread.
checkall - Execute the verification on hesidohackeado.conm, shows all results.
notices - Last notices.
ping - Check the connection to the server
help - Displays help.
```
