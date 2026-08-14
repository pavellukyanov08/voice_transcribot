const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const user = tg.initDataUnsafe?.user;

const userInfo = document.getElementById("user-info");

if (user) {
    userInfo.textContent =
        `Вы вошли как ${user.first_name}`;
} else {
    userInfo.textContent =
        "Пользователь не определён";
}