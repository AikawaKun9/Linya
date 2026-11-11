// Stop double joining: disable the button once the form is submitted.
const joinForm = document.getElementById("join-form");
if (joinForm) {
  const button = joinForm.querySelector("button[type=submit]");
  const originalText = button.textContent;

  joinForm.addEventListener("submit", () => {
    button.disabled = true;
    button.textContent = "Getting your ticket…";
  });

  // If the person taps Back, the browser may keep the disabled button.
  window.addEventListener("pageshow", () => {
    button.disabled = false;
    button.textContent = originalText;
  });
}

// Ask before anything that cannot be undone: <form data-confirm="...">.
document.addEventListener("submit", (event) => {
  const form = event.target;
  if (form.matches && form.matches("form[data-confirm]")) {
    if (!confirm(form.dataset.confirm)) event.preventDefault();
  }
});
