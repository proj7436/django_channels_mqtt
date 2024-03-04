function connect() {
  this.mqttClient = mqtt.connect("mqtts://mqvnaa01.rogo.com.vn:31884", {
    clientId: "clientId" + `${uuidv4()}`,
    rejectUnauthorized: true,
    clean: true,
  });
  this.mqttClient.on("error", (e) => {
    Logger.error("MQTT client connected e", e);
  });
  this.mqttClient.on("connect", () => {
    Logger.log("MQTT client connected");
  });
}
connect();

function add_divice(topic) {
  var ul = document.querySelector(".container_divice ul");
  ul.insertAdjacentHTML(
    "afterbegin",
    `<li class='container-device-log' >${topic}</li>`
  );
}
function add_log(topic, content_hex, qos) {
  var ul = document.querySelector(".container_log ul");
  ul.insertAdjacentHTML(
    "afterbegin",
    `<li class="container-device-log" style="cursor: pointer;"><a target="_blank" style="text-decoration: none;" href="/data/${topic}/${qos}/${content_hex}/" >Topic: ${topic} QoS: ${qos} ${content_hex}</a></li>`
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
    console.log(data);

    if (data.status == "log") {
      add_log(data.topic, data.content_hex, data.qos);
    }
    if (data.status == "topic_exist") {
    } else if (data.status == "created_successfully") {
      const topic = document.getElementById("topic");
      add_divice(topic.value);
      document.getElementById("topic").value = "";
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
