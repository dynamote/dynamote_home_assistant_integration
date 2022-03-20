# Dynamote Home Assistant Integration

<p align="center">
	<img src="images/logo.png" alt="" width="200" height="200">
</p>

<p align="center">
	<a href='https://play.google.com/store/apps/details?id=com.electricedge.dynamote'>
		<img alt='Get it on Google Play' src='https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png' width="150"/>
	</a>
</p>

This is the third party integration for Home Assistant that enables it to communicate with Dynamote devices.

## Installation

### Recommended Method - HACS

- Ensure that [HACS](https://hacs.xyz/) is installed
- Add this repository as a custom repository in HACS (integration type repository)
- Install the Dynamote integration in HACS
- Restart your Home Assistant server

### Manual install

- Download this repository
- Copy the folder "custom_components/dynamote" into the "custom_components" directory of your config folder
- Restart your Home Assistant Server

## Configuration

Add the following line to your configuration file to enable this integration, then restart your Home Assistant server.

```yaml
dynamote:
```

## Configuration

First you must configure and upload your commands to Home Assistant, this is done from the Dynamote app. You must create a [long-lived access token](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token) for the app to be able to communicate with your Home Assistant server.

Connect with the IP address, port, and access token of your Home Assistant server. It usually uses port 8123.

<p align="center">
	<img src="images/hass_connection_settings_from_app.png" alt="">
</p>

Once connected, you may edit/add the available commands for Home Assistant to use. For the "IP Address", use the IP address of the Dynamote device on your local network. It is recommended that you assign a static IP to your device so that the IP remains constant and doesn't change. Once completed, press the upload button at the top of the page in the app.

<p align="center">
	<img src="images/remote_command_configuration_from_app.png" alt="">
</p>

## Usage

In Home Assistant, Dynamote commands are invoked with the "Dynamote.send_command" service. Fill out an action like in the following example. An IP address may be optionally specified, this will overwrite the IP address that the command was originally configured with.

```yaml
service: dynamote.send_command
data:
  commandId: turn_on_tv
  ipAddress: 192.168.2.71             # optional
```