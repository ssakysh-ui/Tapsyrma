
(function () {
  "use strict";

  function formatTenge(value) {
    return String(Math.round(value)).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " ₸";
  }

  function clamp(value, min, max) {
    if (Number.isNaN(value)) {
      return min;
    }
    return Math.max(min, Math.min(max, value));
  }

  function initNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.querySelector("[data-nav]");
    if (!toggle || !nav) {
      return;
    }
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function initFlashes() {
    document.querySelectorAll("[data-flash-close]").forEach(function (button) {
      button.addEventListener("click", function () {
        button.closest(".flash").remove();
      });
    });
  }

  function initSteppers() {
    document.querySelectorAll("[data-stepper]").forEach(function (stepper) {
      var input = stepper.querySelector("input");
      var min = Number(input.min);
      var max = Number(input.max);
      stepper.querySelectorAll("[data-step]").forEach(function (button) {
        button.addEventListener("click", function () {
          var step = Number(button.dataset.step);
          if (step > 0) {
            input.value = clamp(Number(input.value) + 1, min, max);
          } else {
            input.value = clamp(Number(input.value) - 1, min, max);
          }
          input.dispatchEvent(new Event("input", { bubbles: true }));
        });
      });
    });
  }

  function initCart() {
    var form = document.querySelector("[data-cart]");
    if (!form) {
      return;
    }
    var fee = Number(form.dataset.fee);
    var freeFrom = Number(form.dataset.freeFrom);
    var subtotalEl = document.querySelector("[data-subtotal]");
    var deliveryEl = document.querySelector("[data-delivery]");
    var totalEl = document.querySelector("[data-total]");
    var hintEl = document.querySelector("[data-free-hint]");
    var leftEl = document.querySelector("[data-left]");
    var saveButton = form.querySelector("[data-cart-save]");

    function recalc() {
      var subtotal = 0;
      form.querySelectorAll("[data-cart-row]").forEach(function (row) {
        var input = row.querySelector("input");
        var quantity = clamp(Number(input.value), 0, Number(input.max));
        var line = Number(row.dataset.price) * quantity;
        row.querySelector("[data-line-total]").textContent = formatTenge(line);
        row.classList.toggle("is-removed", quantity === 0);
        subtotal += line;
      });
      var delivery = subtotal === 0 || subtotal >= freeFrom ? 0 : fee;
      subtotalEl.textContent = formatTenge(subtotal);
      deliveryEl.textContent = delivery ? formatTenge(delivery) : "тегін";
      totalEl.textContent = formatTenge(subtotal + delivery);
      if (hintEl) {
        var left = Math.max(freeFrom - subtotal, 0);
        hintEl.hidden = left === 0;
        leftEl.textContent = formatTenge(left);
      }
      saveButton.classList.add("btn-attention");
    }

    form.addEventListener("input", recalc);
  }

  initNav();
  initFlashes();
  initSteppers();
  initCart();
})();
