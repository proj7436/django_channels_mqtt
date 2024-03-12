function change_button(status) {
  if (status == "disconnect") {
    const button = document.querySelector(".button-disconnect");
    button.textContent = "CONNECT";
    button.classList.remove("button-disconnect");
    button.classList.add("button-connect");
    button.classList.remove("button-non");
  } else if (status == "connect") {
    const button = document.querySelector(".button-connect");
    button.textContent = "DISCONNECT";
    button.classList.remove("button-connect");
    button.classList.add("button-disconnect");
    button.classList.remove("button-non");
  } else {
    const button = document.querySelector(".button-connect");
    button.textContent = "CONNECT";
    button.classList.remove("button-disconnect");
    button.classList.add("button-connect");
    button.classList.remove("button-non");
  }
}

function change_button_loading(status) {
  if (status == "disconnect") {
    const button = document.querySelector(".button-disconnect");
    button.innerHTML =
      '<i class="fa-solid fa-spinner fa-spin-pulse fa-xl"></i>';
    button.classList.add("button-non");
  } else {
    const button = document.querySelector(".button-connect");
    button.innerHTML =
      '<i class="fa-solid fa-spinner fa-spin-pulse fa-xl"></i>';
    button.classList.add("button-non");
  }
}
var status_connect_mqtt_server = false;
document.querySelector("#mqtt_serverForm").addEventListener("submit", (e) => {
  e.preventDefault();

  //chua connect thi se connect
  if (!status_connect_mqtt_server) {
    const host = document.querySelector("#host");
    const port = document.querySelector("#port");
    if (host.value == "" || port.value == "") {
      return;
    }
    status_connect_mqtt_server = true;
    change_button_loading("connect");
    return ws.send(
      JSON.stringify({
        status: "connect_mqtt_server",
        host: host.value,
        port: port.value,
      })
    );
  }
  status_connect_mqtt_server = false;
  change_button_loading("disconnect");
  return ws.send(
    JSON.stringify({
      status: "disconnect_mqtt_server",
    })
  );
});

function add_divice(topic) {
  var ul = document.querySelector(".container_divice ul");
  ul.insertAdjacentHTML(
    "afterbegin",
    `<div class="container-device-log relative">
    <li class="width:80%">${topic}</li>
    <i onclick="removeDevice('${topic}')" class="fa-solid fa-rectangle-xmark fa-lg close_divice" style="color: #d2301e; position: absolute; right:0;"></i>
    </div>
    `
  );
}
function add_log(topic, content_hex, qos) {
  const time = getTime_H_M_S_now();
  var ul = document.querySelector(".container_log ul");
  ul.insertAdjacentHTML(
    "afterbegin",
    `<li class="container-device-log flex-col" style="cursor: pointer;">
    <p value="${time}"></p>
    <a target="_blank" style="text-decoration: none;" href="/data/${topic}/${qos}/${content_hex}/" >Topic: ${topic} QoS: ${qos} ${content_hex}</a></li>`
  );
}
// get dữ liệu thiết bị
async function getTopics() {
  try {
    const response = await fetch(`${window.location.href}get-all-topics/`);
    if (!response.ok) {
      throw new Error("Network error");
    }
    const data = await response.json();
    if (data) {
      var ul = document.querySelector(".container_divice ul");
      ul.innerHTML = "";
      for (const item of data["all_topics"]) {
        add_divice(item);
      }
    }
  } catch (error) {
    console.error(error);
    return null;
  }
}
getTopics();

var protocol = "ws://";
if (window.location.protocol === "https:") {
  protocol = "wss://";
} else {
  protocol = "ws://";
}
const ws = new WebSocket(`${protocol}${window.location.host}/ws/connect`);

ws.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data); // Parse JSON data

    if (data.status == "log") {
      add_log(data.topic, data.content_hex, data.qos);
      playSoundNoti();
    }
    if (data.status == "topic_exist") {
    } else if (data.status == "created_successfully") {
      const topic = document.getElementById("topic");
      add_divice(topic.value);
      document.getElementById("topic").value = "";
    }
    if (data.status == "connect_success") {
      change_button("connect");
      // noti
      showNotification("Connected!", true);
      var ul = document.querySelector(".container_log ul");
      ul.innerHTML = "";
      getTopics();
    }
    if (data.status == "disconnect_success") {
      change_button("disconnect");
      showNotification("Disconnected!", false);
      var ul = document.querySelector(".container_log ul");
      ul.innerHTML = "";
      getTopics();
    }
    if (data.status == "connect_fail") {
      status_connect_mqtt_server = false;
      change_button("fail");
      showNotification("Connection failed!", false);
      var ul = document.querySelector(".container_log ul");
      ul.innerHTML = "";
      getTopics();
    }
    if (data.status == "remove_topic_success") {
      getTopics();
    }
  } catch (error) {
    console.error(error);
  }
};

document
  .getElementById("deviceForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    const topic = document.getElementById("topic");

    if (!status_connect_mqtt_server) {
      showNotification("Not connected to MQTT server", false);
      return;
    }
    if (topic.value == "") {
      return;
    }

    ws.send(
      JSON.stringify({
        status: "create_topic",
        topic: topic.value,
      })
    );
  });

function showNotification(msg, status) {
  var notification = document.getElementById("notification");
  var notification_msg = document.getElementById("notification-message");
  notification_msg.textContent = msg;
  if (status) {
    notification.classList.remove("noti-fail");
    notification.classList.add("noti-success");
  } else {
    notification.classList.remove("noti-success");
    notification.classList.add("noti-fail");
  }

  notification.style.display = "block"; // Hiển thị thông báo
  setTimeout(function () {
    notification.style.display = "none"; // Ẩn thông báo sau 2 giây
  }, 3000);
}

setInterval(() => {
  const host = document.querySelector("#host");
  const port = document.querySelector("#port");
  if (status_connect_mqtt_server) {
    host.readOnly = true;
    port.readOnly = true;
  } else {
    host.readOnly = false;
    port.readOnly = false;
  }
}, 100);

// Phát âm thanh
var audio = document.getElementById("notificationSound");
audio.volume = 0.3;
function playSoundNoti() {
  audio.play();
}

function removeDevice(topic) {
  ws.send(
    JSON.stringify({
      status: "remove_topic",
      topic: topic,
    })
  );
}
