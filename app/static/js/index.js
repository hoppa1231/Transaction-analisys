const canvas = document.getElementById("colorRing");
const ctx = canvas.getContext("2d");

const costs = document.getElementById("costs");
const income = document.getElementById("income");
const state_move_money = "costs"

costs.addEventListener('click', function() {
    costs.classList.add('active-mm-btn');
    income.classList.remove('active-mm-btn');
    sign = '-';
    fetchOperations(start_date, end_date, sign);
});
income.addEventListener('click', function() {
    costs.classList.remove('active-mm-btn');
    income.classList.add('active-mm-btn');
    sign = '+'
    fetchOperations(start_date, end_date, sign);
});
document.querySelector('#chart-arrow-left').addEventListener('click', function() {
    updateChartList('back');
});
document.querySelector('#chart-arrow-right').addEventListener('click', function() {
    updateChartList('forward');
});
let start_date, end_date, month_date;
let sign = '-';
const months = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

// Центр и радиусы кольца
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;
const outerRadius = 150; // Внешний радиус кольца
const innerRadius = 130;  // Внутренний радиус кольца

// Цвета для секций
const colors = ["#027373", "#038C7F", "#A9D9D0", "#F2E7DC", "#D9D9D9"];
const colors_svg = ["#005757", "#038C7F", "#5ab8a6", "#ebccae", "#898c94"];
const sectionCount = colors.length;

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

function populateList(data) {
    const listContainer = document.querySelector(".list-operation"); // Контейнер списка

    listContainer.innerHTML = '';
    let i = 0;

    data.forEach((item) => {
        // Создаем <li> с классом
        const listItem = document.createElement("li");
        listItem.classList.add("list-operation-item");

        // Добавляем иконку
        const icon = document.createElement("i");
        icon.setAttribute("data-feather", getIconName(item.type)); // Выбираем иконку на основе типа
        
        // Меняем стиль
        icon.style.backgroundColor = colors_svg[i] + '1f';
        icon.style.stroke = colors_svg[i];
        if (i < sectionCount)
            i++;
        
        listItem.appendChild(icon);

        // Добавляем описание операции
        const operationSpan = document.createElement("span");
        operationSpan.classList.add("operation");
        operationSpan.textContent = item.operation;
        listItem.appendChild(operationSpan);

        // Добавляем цену
        const priceSpan = document.createElement("span");
        priceSpan.classList.add("price");
        priceSpan.textContent = `${formatPrice(item.price)} ₽`;
        listItem.appendChild(priceSpan);

        // Добавляем созданный <li> в список
        listContainer.appendChild(listItem);
    });
    listContainer.scrollTop = 0;

    // Обновляем Feather Icons
    feather.replace();
}

function drawChart(data) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const lengthData = data.length;
    let prices = [];
    let result = 0;
    for (let i = 0; i < lengthData; i++) {
        prices.push(parseInt(data[i]['price']));
        result += parseInt(data[i]['price']);
    }

    if (lengthData > sectionCount)
        for (let i = 0; i < lengthData - sectionCount; i++)
            prices[sectionCount-1] += prices.pop(sectionCount);

    let percentAngleList = [];
    prices.forEach((price) => {
        percentAngleList.push( (price / result) * 2 * Math.PI );
    });

    let startAngle = 0;
    // Рисуем секции кольца
    for (let i = 0; i < sectionCount; i++) {
        const endAngle = startAngle + percentAngleList[i];

        // Рисуем внешнюю часть секции
        ctx.beginPath();
        ctx.arc(centerX, centerY, outerRadius, startAngle, endAngle, false);
        ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true);
        ctx.closePath();

        // Задаем цвет
        ctx.fillStyle = colors[i];
        ctx.fill();
        startAngle = endAngle;
    }
    // Рисуем таблицу
    populateList(data);
}

const API_URL = '/get/operations';

// Функция для получения данных
async function fetchOperations(start_date, end_date, sign) {
    // Параметры для запроса
    const params = {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
        start_date: start_date,
        end_date: end_date,
        sign: sign
        })
    };
    try {
        const response = await fetch(API_URL, params);
        if (!response.ok) {
            throw new Error(`Ошибка: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        drawChart(data['operations']);
        setTotal(data['total']);
        return 1;
    } catch (error) {
        console.error('Ошибка при получении операций:', error);
        return [];
    }
}

function setTotal(total) {
    document.querySelector('#sum').textContent = formatPrice(total);
}
function setTextChart(text) {
    document.querySelector('#colorRing-text').textContent = text;
}

function getCurrentMonthAndYear() {
    const today = new Date();
    const newIndex = today.getMonth()
    const month = months[newIndex];
    const newYear = today.getFullYear();
    const year = newYear - 2000;
    let lastDay = new Date(newYear, newIndex + 1, 0).getDate();
    return [`${month}, ${year}`, `${newYear}-${newIndex+1}-01`, `${newYear}-${newIndex+1}-${lastDay}`];
}
function subtractOneMonth(input) {
    const [month, year] = input.split(', ').map((v, i) => (i === 1 ? parseInt(v) : v));
    const currentIndex = months.indexOf(month);
    let newIndex = currentIndex - 1;
    let newYear = year;
    if (newIndex < 0) {
        newIndex = 11;
        newYear -= 1;
    }
    const newMonth = months[newIndex];
    let lastDay = new Date(newYear, newIndex + 1, 0).getDate();
    return [`${newMonth}, ${newYear}`, `${newYear+2000}-${newIndex+1}-01`, `${newYear+2000}-${newIndex+1}-${lastDay}`];
}
function addOneMonth(input) {
    const [month, year] = input.split(', ').map((v, i) => (i === 1 ? parseInt(v) : v));
    const currentIndex = months.indexOf(month);
    let newIndex = currentIndex + 1;
    let newYear = year;
    if (newIndex > 11) {
        newIndex = 0;
        newYear += 1;
    }
    const newMonth = months[newIndex];
    let lastDay = new Date(newYear, newIndex + 1, 0).getDate();
    return [`${newMonth}, ${newYear}`, `${newYear+2000}-${newIndex+1}-01`, `${newYear+2000}-${newIndex+1}-${lastDay}`];
}

function updateChartList(type='none') {
    if (type == 'forward') 
        [month_date, start_date, end_date] = addOneMonth(month_date);
    else if (type == 'back')
        [month_date, start_date, end_date] = subtractOneMonth(month_date);
    else if (type == 'none')
        [month_date, start_date, end_date] = getCurrentMonthAndYear();
    setTextChart(month_date)
    fetchOperations(start_date, end_date, sign);
}

document.addEventListener('DOMContentLoaded', function() {
    updateChartList();
 }, false);
