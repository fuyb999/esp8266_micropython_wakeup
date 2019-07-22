var ws;

var password = '123456';
var ENTER = "\r\n";

var PARAM_PASSORD = password + ENTER;

var REQ_PASSWORD = "Password: ";
var REQ_CONNECTED = "WebREPL connected";
var REQ_NETWORK_STATUS = "network status: ";

var SCAN_WIFI_SCRIPT = "" +
    "import network" + ENTER +
    "sta_if = network.WLAN(network.STA_IF)" + ENTER +
    "sta_if.active(True)" + ENTER +
    "sta_if.scan()" + ENTER;

var STORE_WIFI_SCRIPT = "" +
    "from configparser import Configparser" + ENTER +
    "c = Configparser()" + ENTER +
    "c.set('ssid', %ssid)" + ENTER +
    "c.set('password', %password)" + ENTER;

var TRY_CONNECT_WIFI = "" +
    "import utils" + ENTER +
    "status = utils.connect_to_internet(%ssid, %password)" + ENTER +
    "print('" + REQ_NETWORK_STATUS + "'+str(status))" + ENTER;

var READ_STORE_WIFI_SCRIPT = "" +
    "import utils" + ENTER +
    "utils.read_profiles()" + ENTER;

var REBOOT = "" +
    "import machine" + ENTER +
    "machine.reset()" + ENTER;

var scan_state = 0;
var scan_result = "";
var reboot_state = 0;
var connect_wifi_state = 0;
$(function () {

    $("#connect-server").click(function () {
        var url = $("#url").val();
        websocket(url);
    });

    $("#scan-wifi").click(function () {
        scan_state = 1;
        scan_result = "";
        $("#wifi-list").html("");
        ws.send(SCAN_WIFI_SCRIPT);
    });

    $("#connect-wifi").click(function () {
        var ssid = $("#wifi-list").val();
        var password = $("#password").val();
        if (ssid == "") {
            alert("请选择wifi");
            return;
        }
        if (password == "") {
            alert("请输入wifi密码");
            return;
        }
        $(this).button("loading");
        connect_wifi_state = 1;
        ws.send(TRY_CONNECT_WIFI.replace("%ssid", "'"+ssid+"'").replace("%password", "'"+password+"'"));
        // ws.send(TRY_CONNECT_WIFI.replace("%s", "'" + ssid + "','" + password + "'"));
    });

    $("#read-wifi").click(function () {
        ws.send(READ_STORE_WIFI_SCRIPT);
    });

    $("#reboot").click(function () {
        reboot(function () {
            alert("重启成功");
            $("#reboot").button('reset');
        });
    });

    $(".btn:not(#connect-wifi)").click(function () {
        $(this).button('loading')
        // $(this).button('loading').delay(1000).queue(function() {
        //     $(this).button('reset');
        //     $(this).dequeue();
        // });
    });

});


function websocket(url) {

    ws = new WebSocket(url);

    ws.onopen = function () {
        console.log("connect " + url + " successful.");
    };

    ws.onmessage = function (event) {
        var data = event.data;

        console.log(event);
        if (data == REQ_PASSWORD) {
            ws.send(PARAM_PASSORD);
        }
        if (data.indexOf(REQ_CONNECTED) != -1) {
            if (reboot_state == 0) {
                alert("连接成功！");
                $("#scan-wifi").removeAttr("disabled");
                $("#reboot").removeAttr("disabled");
                $("#connect-server").button('reset');
            }
            reboot_state = 0;
        }

        if (data == "[" && scan_state == 1) {
            scan_state = 2;
        }
        if (scan_state == 2) {
            scan_result += data;
            if (data == "]") {
                $("#scan-wifi").button('reset');
                $("#wifi-list").removeAttr("disabled");
                $("#wifi-list").append("<option value=''></option>");
                scan_state = 0;
                var wifiList = scan_result.match(/\(b'(\w|\d|_|-)+'/ig);
                wifiList.forEach(function (item) {
                    var wifi_name = item.match(/\(b'((\w|\d|_|-)+)'/i)[1];
                    var $option = $("<option value=" + wifi_name + ">" + wifi_name + "</option>");
                    $("#wifi-list").append($option);

                });
                $("#password").removeAttr("disabled");
                $("#connect-wifi").removeAttr("disabled");
                alert("共扫描到 " + wifiList.length + " 个wifi");
            }
        }
        if (connect_wifi_state == 1 && data.indexOf(REQ_NETWORK_STATUS) != -1) {
            console.log(data);
            connect_wifi_state = 0;
            var status = data.replace(REQ_NETWORK_STATUS, "");
            if (status == "1") {
                setTimeout(function () {
                    alert("wifi连接成功");
                    var ssid = $("#wifi-list").val();
                    var password = $("#password").val();
                    // var store = JSON.stringify({ssid: ssid, password: password});
                    ws.send(STORE_WIFI_SCRIPT.replace("%ssid", "'"+ssid+"'").replace("%password", "'"+password+"'"));
                    $("#connect-wifi").button('reset');
                }, 500);
            } else {
                alert("wifi连接失败，请重试");
                $("#connect-wifi").button('reset');
            }
        }
    };

}

//重启
function reboot(callback) {
    setTimeout(function () {
        // send reboot cmd
        ws.send(REBOOT);
        reboot_state = 1;
        // reconnecting
        setTimeout(function () {
            var url = $("#url").val();
            websocket(url);
            //wait connect successful
            var reboot_timer = setInterval(function () {
                if (reboot_state == 0) {
                    clearInterval(reboot_timer);
                    callback && callback();
                }
            }, 1000);

        }, 3 * 1000);

    }, 3 * 1000);
}