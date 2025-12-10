function renderNav() {
  const userId = localStorage.getItem("userId");
  const nav = document.getElementById("nav");

  if (!nav) return;

  if (userId) {
    nav.innerHTML = `
      <a href="index.html">Home</a>
      <a href="my_orders.html">My Orders</a>
      <span class="user-badge">👤 ${userId}</span>
      <button class="logout-btn" onclick="logout()">Logout</button>
    `;
  } else {
    nav.innerHTML = `
      <a href="index.html">Home</a>
      <a href="login.html">Login</a>
      <a href="register.html">Register</a>
    `;
  }
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("userId");
  window.location.href = "login.html";
}

document.addEventListener("DOMContentLoaded", renderNav);