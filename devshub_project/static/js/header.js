const userMenuButton = document.querySelector("[data-js-user-menu-button]");
const userMenu = document.querySelector("[data-js-user-menu]");

const burgerButton = document.querySelector("[data-js-burger-button]");
const mobileMenu = document.querySelector("[data-js-mobile-menu]");

if (userMenuButton && userMenu) {
  userMenuButton.addEventListener("click", (e) => {
    e.stopPropagation();
    userMenu.classList.toggle("hidden");
  });

  userMenu.addEventListener("click", () => {
    userMenu.classList.add("hidden");
  });
}

burgerButton.addEventListener("click", () => {
  mobileMenu.classList.toggle("hidden");
});
