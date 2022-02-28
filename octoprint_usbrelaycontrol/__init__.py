# coding=utf-8
from __future__ import absolute_import, print_function
from octoprint.access.permissions import Permissions

import octoprint.plugin
import flask

from .relay import Relay

class USBRelayControlPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.RestartNeedingPlugin,
):
    relays = {}

    def on_startup(self, *args, **kwargs):
        pass

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=True),
            dict(
                type="sidebar",
                custom_bindings=True,
                template="usbrelaycontrol_sidebar.jinja2",
                icon="map-signs",
            ),
        ]

    def get_assets(self):
        return dict(
            js=["js/usbrelaycontrol.js", "js/fontawesome-iconpicker.min.js"],
            css=["css/usbrelaycontrol.css", "css/fontawesome-iconpicker.min.css"],
        )

    def get_settings_defaults(self):
        return dict(usbrelay_configurations=[])

    def get_relay_key(self, configuration):
        return "%(vendor)s:%(product)s" % configuration

    def on_settings_save(self, data):
        for relay in self.relays.values():
            relay.cleanup()
        self.relays = {}

        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        for configuration in self._settings.get(["usbrelay_configurations"]):
            key = self.get_relay_key(configuration)
            try:
                vendor = int(configuration["vendor"], 16)
            except ValueError:
                self._logger.error("Invalid vendor ID")
                continue
            try:
                product = int(configuration["product"], 16)
            except ValueError:
                self._logger.error("Invalid product ID")
                continue

            if key not in self.relays:
                self.relays[key] = Relay(vendor, product)
            self._logger.info(
                "Reconfigured USB Relay {}: {}, {} ({})".format(
                    configuration["relaynumber"],
                    configuration["vendor"],
                    configuration["product"],
                    configuration["active_mode"],
                    configuration["default_state"],
                    configuration["name"],
                )
            )

            if configuration["active_mode"] == "active_low":
                if configuration["default_state"] == "default_on":
                    self.relays[key].state(int(configuration["relaynumber"]), False)
                elif configuration["default_state"] == "default_off":
                    self.relays[key].state(int(configuration["relaynumber"]), True)
            elif configuration["active_mode"] == "active_high":
                if configuration["default_state"] == "default_on":
                    self.relays[key].state(int(configuration["relaynumber"]), True)
                elif configuration["default_state"] == "default_off":
                    self.relays[key].state(int(configuration["relaynumber"]), False)

    def on_after_startup(self):
        for configuration in self._settings.get(["usbrelay_configurations"]):
            key = self.get_relay_key(configuration)
            try:
                vendor = int(configuration["vendor"], 16)
            except ValueError:
                self._logger.error("Invalid vendor ID")
                continue
            try:
                product = int(configuration["product"], 16)
            except ValueError:
                self._logger.error("Invalid product ID")
                continue
            if key not in self.relays:
                self.relays[key] = Relay(vendor, product)
            self._logger.info(
                "Configured USB Relay {}: {},{} ({})".format(
                    configuration["relaynumber"],
                    configuration["vendor"],
                    configuration["product"],
                    configuration["active_mode"],
                    configuration["default_state"],
                    configuration["name"],
                )
            )

            if configuration["active_mode"] == "active_low":
                if configuration["default_state"] == "default_on":
                    self.relays[key].state(int(configuration["relaynumber"]), False)
                elif configuration["default_state"] == "default_off":
                    self.relays[key].state(int(configuration["relaynumber"]), True)
            elif configuration["active_mode"] == "active_high":
                if configuration["default_state"] == "default_on":
                    self.relays[key].state(int(configuration["relaynumber"]), True)
                elif configuration["default_state"] == "default_off":
                    self.relays[key].state(int(configuration["relaynumber"]), False)

    def get_api_commands(self):
        return dict(turnUSBRelayOn=["id"], turnUSBRelayOff=["id"], getUSBRelayState=["id"])

    def on_api_command(self, command, data):
        if not Permissions.PLUGIN_USBRELAYCONTROL_CONTROL.can():
            return flask.make_response("Insufficient rights", 403)

        configuration = self._settings.get(["usbrelay_configurations"])[int(data["id"])]
        relaynumber = int(configuration["relaynumber"])
        key = self.get_relay_key(configuration)

        if command == "getUSBRelayState":
            if configuration["active_mode"] == "active_low":
                return flask.jsonify("off" if self.relays[key].state(relaynumber) else "on")
            elif configuration["active_mode"] == "active_high":
                return flask.jsonify("on" if self.relays[key].state(relaynumber) else "off")
        elif command == "turnUSBRelayOn":
            self._logger.info("Turned on USB Relay {}".format(configuration["relaynumber"]))

            if configuration["active_mode"] == "active_low":
                self.relays[key].state(relaynumber, False)
            elif configuration["active_mode"] == "active_high":
                self.relays[key].state(relaynumber, True)
        elif command == "turnUSBRelayOff":
            self._logger.info("Turned off USB Relay{}".format(configuration["relaynumber"]))

            if configuration["active_mode"] == "active_low":
                self.relays[key].state(relaynumber, True)
            elif configuration["active_mode"] == "active_high":
                self.relays[key].state(relaynumber, False)

    def on_api_get(self, request):
        states = []

        for configuration in self._settings.get(["usbrelay_configurations"]):
            key = self.get_relay_key(configuration)
            relaynumber = int(configuration["relaynumber"])

            if configuration["active_mode"] == "active_low":
                states.append("off" if self.relays[key].state(relaynumber) else "on")
            elif configuration["active_mode"] == "active_high":
                states.append("on" if self.relays[key].state(relaynumber) else "off")

        return flask.jsonify(states)

    def get_update_information(self):
        return dict(
            usbrelaycontrol=dict(
                displayName="USB Relay Control",
                displayVersion=self._plugin_version,
                type="github_release",
                user="abudden",
                repo="OctoPrint-USBRelayControl",
                current=self._plugin_version,
                stable_branch=dict(
                    name="Stable",
                    branch="master",
                    comittish=["master"],
                ),
                prerelease_branches=[
                    dict(
                        name="Prerelease",
                        branch="development",
                        comittish=["development", "master"],
                    )
                ],
                pip="https://github.com/abudden/OctoPrint-USBRelayControl/archive/{target_version}.zip",
            )
        )

    def get_additional_permissions(self, *args, **kwargs):
        return [
                dict(key="CONTROL",
                    name="Control",
                    description=gettext("Allows switching relays on/off"),
                    roles=["admin"],
                    dangerous=True,
                    default_groups=[Permissions.ADMIN_GROUP])
                ]

__plugin_name__ = "USB Relay Control"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = USBRelayControlPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.access.permissions": __plugin_implementation__.get_additional_permissions,
    }
