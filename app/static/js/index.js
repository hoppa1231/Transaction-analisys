const canvas = document.getElementById("colorRing");
const ctx = canvas.getContext("2d");
const offlineBanner = document.getElementById("offline-banner");
const uploadInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");

const costs = document.getElementById("costs");
const income = document.getElementById("income");
const state_move_money = "costs";

let start_date, end_date, month_date;
let sign = "-";
let isOffline = !navigator.onLine;
let centerX = canvas.width / 2;
let centerY = canvas.height / 2;
let outerRadius = 150;
let innerRadius = 130;
let lastOperations = [];
let lastTotal = 0;

const months = [
  "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
];

const colors = ["#027373", "#038C7F", "#A9D9D0", "#F2E7DC", "#D9D9D9"];
const colors_svg = ["#005757", "#038C7F", "#5ab8a6", "#ebccae", "#898c94"];
const sectionCount = colors.length;

function resizeChartToContainer() {
  const container = document.querySelector(".chart-pie");
  const maxSize = 380;
  const minSize = 180;
  const containerWidth = container ? container.getBoundingClientRect().width : maxSize;
  let size = Math.max(minSize, Math.min(maxSize, containerWidth));
  const dpr = window.devicePixelRatio || 1;

  canvas.style.width = `${size}px`;
  canvas.style.height = `${size}px`;
  canvas.width = Math.round(size * dpr);
  canvas.height = Math.round(size * dpr);

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  centerX = size / 2;
  centerY = size / 2;
  outerRadius = size * 0.48;
  innerRadius = size * 0.40;
}

costs.addEventListener("click", function () {
  costs.classList.add("active-mm-btn");
  income.classList.remove("active-mm-btn");
  sign = "-";
  fetchOperations(start_date, end_date, sign);
});
income.addEventListener("click", function () {
  costs.classList.remove("active-mm-btn");
  income.classList.add("active-mm-btn");
  sign = "+";
  fetchOperations(start_date, end_date, sign);
});
document.querySelector("#chart-arrow-left").addEventListener("click", function () {
  updateChartList("back");
});
document.querySelector("#chart-arrow-right").addEventListener("click", function () {
  updateChartList("forward");
});

function getIconName(type) {
  const icons = {
    transfer: "users",
    travel: "globe",
    kafe: "coffee",
    supermarket: "shopping-cart",
    subscription: "credit-card",
  };
  return icons[type] || "circle";
}
function formatPrice(price) {
  return Number(price).toLocaleString("ru-RU");
}
function setOfflineState(state) {
  isOffline = state;
  if (state) offlineBanner.classList.remove("hidden");
  else offlineBanner.classList.add("hidden");
}
function setUploadStatus(message, isError = false) {
  uploadStatus.textContent = message || "";
  uploadStatus.classList.toggle("error", Boolean(isError));
  uploadStatus.classList.toggle("success", Boolean(!isError && message));
  uploadStatus.style.display = message ? "inline" : "none";
}

function populateList(data) {
  const listContainer = document.querySelector(".list-operation");

  listContainer.innerHTML = "";
  let i = 0;

  if (!data || data.length === 0) {
    const listItem = document.createElement("li");
    listItem.classList.add("list-operation-item", "empty-state");
    listItem.textContent = "Нет данных для отображения";
    listContainer.appendChild(listItem);
    listContainer.scrollTop = 0;
    feather.replace();
    return;
  }

  data.forEach((item) => {
    const listItem = document.createElement("li");
    listItem.classList.add("list-operation-item");

    const icon = document.createElement("i");
    icon.setAttribute("data-feather", getIconName(item.type));

    icon.style.backgroundColor = colors_svg[i] + "1f";
    icon.style.stroke = colors_svg[i];
    if (i < sectionCount) i++;

    listItem.appendChild(icon);

    const operationSpan = document.createElement("span");
    operationSpan.classList.add("operation");
    operationSpan.textContent = item.operation;
    listItem.appendChild(operationSpan);

    const priceSpan = document.createElement("span");
    priceSpan.classList.add("price");
    priceSpan.textContent = `${formatPrice(item.price)} ₽`;
    listItem.appendChild(priceSpan);

    listContainer.appendChild(listItem);
  });
  listContainer.scrollTop = 0;

  feather.replace();
}

function drawChart(data) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const lengthData = data.length;
  if (!lengthData) {
    populateList([]);
    return;
  }

  let prices = [];
  let result = 0;
  for (let i = 0; i < lengthData; i++) {
    prices.push(parseInt(data[i]["price"]));
    result += parseInt(data[i]["price"]);
  }

  if (lengthData > sectionCount)
    for (let i = 0; i < lengthData - sectionCount; i++)
      prices[sectionCount - 1] += prices.pop(sectionCount);

  if (result === 0) {
    populateList(data);
    return;
  }

  let percentAngleList = [];
  prices.forEach((price) => {
    percentAngleList.push((price / result) * 2 * Math.PI);
  });

  let startAngle = 0;
  for (let i = 0; i < sectionCount; i++) {
    const endAngle = startAngle + percentAngleList[i];

    ctx.beginPath();
    ctx.arc(centerX, centerY, outerRadius, startAngle, endAngle, false);
    ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true);
    ctx.closePath();

    ctx.fillStyle = colors[i];
    ctx.fill();
    startAngle = endAngle;
  }

  populateList(data);
}

const API_URL = "/get/operations";

async function fetchOperations(start_date, end_date, sign) {
  const params = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      start_date: start_date,
      end_date: end_date,
      sign: sign,
    }),
  };
  try {
    const response = await fetch(API_URL, params);
    if (!response.ok) {
      throw new Error(`Ошибка запроса: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    setOfflineState(Boolean(data["offline"]));
    lastOperations = data["operations"] || [];
    lastTotal = data["total"] || 0;
    drawChart(lastOperations);
    setTotal(lastTotal);
    return 1;
  } catch (error) {
    console.error("Ошибка при получении операций:", error);
    setOfflineState(true);
    lastOperations = [];
    lastTotal = 0;
    populateList([]);
    setTotal(0);
    return [];
  }
}

function setTotal(total) {
  document.querySelector("#sum").textContent = formatPrice(total);
}
function setTextChart(text) {
  document.querySelector("#colorRing-text").textContent = text;
}

function getCurrentMonthAndYear() {
  const today = new Date();
  const newIndex = today.getMonth();
  const month = months[newIndex];
  const newYear = today.getFullYear();
  const year = newYear - 2000;
  let lastDay = new Date(newYear, newIndex + 1, 0).getDate();
  return [`${month}, ${year}`, `${newYear}-${newIndex + 1}-01`, `${newYear}-${newIndex + 1}-${lastDay}`];
}
function subtractOneMonth(input) {
  const [month, year] = input.split(", ").map((v, i) => (i === 1 ? parseInt(v) : v));
  const currentIndex = months.indexOf(month);
  let newIndex = currentIndex - 1;
  let newYear = year;
  if (newIndex < 0) {
    newIndex = 11;
    newYear -= 1;
  }
  const newMonth = months[newIndex];
  let lastDay = new Date(newYear, newIndex + 1, 0).getDate();
  return [`${newMonth}, ${newYear}`, `${newYear + 2000}-${newIndex + 1}-01`, `${newYear + 2000}-${newIndex + 1}-${lastDay}`];
}
function addOneMonth(input) {
  const [month, year] = input.split(", ").map((v, i) => (i === 1 ? parseInt(v) : v));
  const currentIndex = months.indexOf(month);
  let newIndex = currentIndex + 1;
  let newYear = year;
  if (newIndex > 11) {
    newIndex = 0;
    newYear += 1;
  }
  const newMonth = months[newIndex];
  let lastDay = new Date(newYear, newIndex + 1, 0).getDate();
  return [`${newMonth}, ${newYear}`, `${newYear + 2000}-${newIndex + 1}-01`, `${newYear + 2000}-${newIndex + 1}-${lastDay}`];
}

function updateChartList(type = "none") {
  if (type == "forward") [month_date, start_date, end_date] = addOneMonth(month_date);
  else if (type == "back") [month_date, start_date, end_date] = subtractOneMonth(month_date);
  else if (type == "none") [month_date, start_date, end_date] = getCurrentMonthAndYear();
  setTextChart(month_date);
  fetchOperations(start_date, end_date, sign);
}

function registerServiceWorker() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/service-worker.js", { scope: "/" }).catch((err) => console.error("SW registration failed", err));
  }
}

async function uploadFile() {
  if (!uploadInput.files || !uploadInput.files.length) {
    setUploadStatus("Выберите файл для загрузки", true);
    return;
  }
  const file = uploadInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Загрузка...";
  setUploadStatus("");

  try {
    const resp = await fetch("/upload", { method: "POST", body: formData });
    const data = await resp.json();
    if (!resp.ok || data.error) {
      throw new Error(data.error || "Ошибка загрузки");
    }
    setUploadStatus(`Готово: загружено ${data.rows} строк`, false);
    updateChartList();
  } catch (err) {
    setUploadStatus(err.message, true);
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Загрузить";
  }
}

document.addEventListener(
  "DOMContentLoaded",
  function () {
    resizeChartToContainer();
    window.addEventListener("resize", () => {
      resizeChartToContainer();
      drawChart(lastOperations);
      setTotal(lastTotal);
    });
    setOfflineState(!navigator.onLine);
    window.addEventListener("online", () => setOfflineState(false));
    window.addEventListener("offline", () => setOfflineState(true));
    registerServiceWorker();
    if (uploadBtn) {
      uploadBtn.addEventListener("click", uploadFile);
    }
    updateChartList();
  },
  false
);
