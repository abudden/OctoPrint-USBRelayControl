/*
 * View model for OctoPrint-USBRelayControl
 *
 * Author: Damian Wójcik
 * License: AGPLv3
 */
$(function () {
    function USBRelayControlViewModel(parameters) {
        var self = this;
        self.settings = parameters[0];
        self.usbrelayButtons = ko.observableArray();
        self.usbrelayConfigurations = ko.observableArray();

        self.onBeforeBinding = function () {
            self.usbrelayConfigurations(self.settings.settings.plugins.usbrelaycontrol.usbrelay_configurations.slice(0));
            self.updateUSBRelayButtons();
        };

        self.onSettingsShown = function () {
            self.usbrelayConfigurations(self.settings.settings.plugins.usbrelaycontrol.usbrelay_configurations.slice(0));
            self.updateIconPicker();
        };

        self.onSettingsHidden = function () {
            self.usbrelayConfigurations(self.settings.settings.plugins.usbrelaycontrol.usbrelay_configurations.slice(0));
            self.updateUSBRelayButtons();
        };

        self.onSettingsBeforeSave = function () {
            self.settings.settings.plugins.usbrelaycontrol.usbrelay_configurations(self.usbrelayConfigurations.slice(0));
        };

        self.addUSBRelayConfiguration = function () {
            self.usbrelayConfigurations.push({relaynumber: 1, vendor: "16c0", product: "05df", icon: "fas fa-plug", name: "", active_mode: "active_high", default_state: "default_off"});
            self.updateIconPicker();
        };

        self.removeUSBRelayConfiguration = function (configuration) {
            self.usbrelayConfigurations.remove(configuration);
        };

        self.updateIconPicker = function () {
            $('.iconpicker').each(function (index, item) {
                $(item).iconpicker({
                    placement: "bottomLeft",
                    hideOnSelect: true,
                });
            });
        };

        self.updateUSBRelayButtons = function () {
            self.usbrelayButtons(ko.toJS(self.usbrelayConfigurations).map(function (item) {
                return {
                    icon: item.icon,
                    name: item.name,
                    current_state: "unknown",
                }
            }));

            OctoPrint.simpleApiGet("usbrelaycontrol").then(function (states) {
                self.usbrelayButtons().forEach(function (item, index) {
                    self.usbrelayButtons.replace(item, {
                        icon: item.icon,
                        name: item.name,
                        current_state: states[index],
                    });
                });
            });
        }

        self.turnUSBRelayOn = function () {
            OctoPrint.simpleApiCommand("usbrelaycontrol", "turnUSBRelayOn", {id: self.usbrelayButtons.indexOf(this)}).then(function () {
                self.updateUSBRelayButtons();
            });
        }

        self.turnUSBRelayOff = function () {
            OctoPrint.simpleApiCommand("usbrelaycontrol", "turnUSBRelayOff", {id: self.usbrelayButtons.indexOf(this)}).then(function () {
                self.updateUSBRelayButtons();
            });
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: USBRelayControlViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_usbrelaycontrol", "#sidebar_plugin_usbrelaycontrol"]
    });
});
